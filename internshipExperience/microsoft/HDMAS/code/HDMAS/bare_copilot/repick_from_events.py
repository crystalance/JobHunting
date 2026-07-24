"""Re-pick BARE final answers from already-recorded events.jsonl files.

Background: an earlier version of run.py used ``max(messages, key=len)`` to
choose the final assistant message, which systematically picked verbose
interim status messages and threw away the short ``FINAL ANSWER: <value>``
commit. This script fixes that without re-running the LLM:

  * For each ``<task_id>/logs/events.jsonl`` under the results dir,
    reconstruct the list of ASSISTANT_MESSAGE previews,
  * Re-pick using ``_pick_final_message`` from run.py,
  * Rewrite ``<task_id>_response.jsonl`` (response field),
  * Re-extract + re-score, rewrite ``<task_id>_eval_result.json``,
  * Regenerate ``summary.json``.

Note: events.jsonl only stores the first 200 chars (the "preview") of each
assistant message. For the BARE-bug fix that's enough because the FINAL
ANSWER line is always at the very end of the message and tends to be short.
We additionally fall back to ``logs/final_answer.md`` (the full picked
message) only when ``events.jsonl`` doesn't help.
"""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path

# Import helpers from sibling run.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import (  # type: ignore
    _pick_final_message,
    gaia_extract_final_answer,
    gaia_scorer,
    _write_gaia_summary,
)


def repick_one(case_dir: Path) -> tuple[str, bool]:
    """Return (new_response_text, used_events).

    events.jsonl truncates each ASSISTANT_MESSAGE to a 200-char ``preview``,
    which can drop a tail-located ``FINAL ANSWER:`` marker. To recover the
    full text we splice in ``logs/final_answer.md`` (the *full* text of
    whichever message the old picker chose, almost always the longest one).
    Whichever preview matches that full text by prefix gets upgraded to the
    full version before re-picking.
    """
    events_path = case_dir / "logs" / "events.jsonl"
    if not events_path.exists():
        return "", False
    msgs: list[str] = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "ASSISTANT_MESSAGE":
            preview = ev.get("preview", "")
            if preview:
                msgs.append(preview)
    if not msgs:
        return "", False

    # Upgrade truncated previews using final_answer.md when possible.
    full_path = case_dir / "logs" / "final_answer.md"
    if full_path.exists():
        full = full_path.read_text(encoding="utf-8")
        # final_answer.md was written verbatim from one of the messages.
        # Match by the first ~150 chars (after collapsing newlines like the
        # preview did).
        full_head = full[:150].replace("\n", " ")
        for i, m in enumerate(msgs):
            if m.startswith(full_head[:min(150, len(m))]):
                msgs[i] = full
                break

    return _pick_final_message(msgs), True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", required=True, type=Path)
    args = p.parse_args()

    root: Path = args.results_dir
    if not root.exists():
        sys.exit(f"Not found: {root}")

    eval_files = sorted(root.glob("*_eval_result.json"))
    print(f"Found {len(eval_files)} eval files in {root}")

    summary_rows: list[dict] = []
    n_correct = 0
    n_evaluated = 0
    n_changed = 0
    n_repicked = 0

    for eval_path in eval_files:
        task_id = eval_path.stem.removesuffix("_eval_result")
        case_dir = root / task_id
        resp_path = root / f"{task_id}_response.jsonl"

        old_eval = json.loads(eval_path.read_text(encoding="utf-8"))
        old_resp = {}
        if resp_path.exists():
            try:
                old_resp = json.loads(resp_path.read_text(encoding="utf-8").strip())
            except Exception:
                pass

        new_response, used_events = repick_one(case_dir)
        if not used_events:
            # Fall back to existing response
            new_response = old_resp.get("response", "")
        else:
            n_repicked += 1

        gt = (old_eval.get("ground_truth") or "").strip()
        extracted = gaia_extract_final_answer(new_response)
        is_correct = False
        try:
            if gt and extracted:
                is_correct = bool(gaia_scorer(extracted, gt))
        except Exception:
            pass

        new_eval = {
            "task_id": task_id,
            "level": old_eval.get("level", ""),
            "question": old_eval.get("question", ""),
            "ground_truth": gt,
            "extracted_answer": extracted,
            "is_correct": is_correct,
            "has_response": bool(new_response),
            "error": old_eval.get("error", ""),
        }

        if (new_eval["extracted_answer"] != old_eval.get("extracted_answer")
                or new_eval["is_correct"] != old_eval.get("is_correct")):
            n_changed += 1
            print(f"  [{task_id[:8]}] {old_eval.get('is_correct')} -> {is_correct}  "
                  f"old_ans={(old_eval.get('extracted_answer') or '')[:60]!r}  "
                  f"new_ans={extracted[:60]!r}  gt={gt[:60]!r}")

        # Write back
        if old_resp:
            old_resp["response"] = new_response
            resp_path.write_text(json.dumps(old_resp, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
        eval_path.write_text(json.dumps(new_eval, indent=2, ensure_ascii=False),
                             encoding="utf-8")

        summary_rows.append(new_eval)
        n_evaluated += 1
        if is_correct:
            n_correct += 1

    # Rebuild summary.json — preserve old config and skipped
    summary_path = root / "summary.json"
    skipped: list = []
    args_obj = None
    if summary_path.exists():
        try:
            old = json.loads(summary_path.read_text(encoding="utf-8"))
            cfg = old.get("config", {})

            class _Cfg:
                pass
            args_obj = _Cfg()
            for k, v in cfg.items():
                setattr(args_obj, k, v)
            # Reconstruct skipped list from old summary if present
            if old.get("skipped"):
                skipped = old["skipped"]
        except Exception:
            pass

    if args_obj is None:
        class _Cfg:
            pass
        args_obj = _Cfg()
        args_obj.benchmark = "gaia"
        args_obj.output_root = str(root)
        args_obj.model = ""
        args_obj.timeout = 0
        args_obj.stage = "eval"
        args_obj.first_n = None
        args_obj.instance_ids = None
        args_obj.split = ""
        args_obj.level = None
        args_obj.task_ids = None
        args_obj.include_unsuitable = False
        args_obj.resume = True

    # Try to load skipped from skipped_cases.json
    skipped_path = root / "skipped_cases.json"
    if skipped_path.exists():
        try:
            skipped = json.loads(skipped_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    _write_gaia_summary(root, summary_rows, args_obj, n_correct, n_evaluated, skipped)

    print()
    print(f"Re-picked from events.jsonl: {n_repicked}/{n_evaluated}")
    print(f"Eval rows changed:           {n_changed}/{n_evaluated}")
    print(f"NEW score: {n_correct}/{n_evaluated} = "
          f"{100.0*n_correct/n_evaluated:.1f}%" if n_evaluated else "NEW score: n/a")


if __name__ == "__main__":
    main()
