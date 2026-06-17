"""
GAIA benchmark batch evaluation runner for HDMAS.

Loads cases from the HuggingFace dataset `gaia-benchmark/GAIA` (validation split
by default, which has ground-truth answers), runs each case through HDMAS,
extracts the model's FINAL ANSWER, and scores it with GAIA's official scorer.

Usage examples (PowerShell):

    # Run first 10 validation cases (skipping multimodal) with 3 agents
    python -m HDMAS.gaia_eval `
        --first_n 10 `
        --output_root HDMAS/gaia_benchmark_results/run_$(Get-Date -Format yyyyMMdd_HHmmss)

    # Run only Level-1 cases, 8 agents, gpt-4.1
    python -m HDMAS.gaia_eval `
        --level 1 `
        --agent_count 8 `
        --model gpt-4.1 `
        --output_root HDMAS/gaia_benchmark_results/level1_8agents

    # Resume an interrupted run (skips cases that already have eval results)
    python -m HDMAS.gaia_eval `
        --output_root HDMAS/gaia_benchmark_results/level1_8agents `
        --level 1 --agent_count 8 --model gpt-4.1 --resume

    # Run a specific subset of task ids
    python -m HDMAS.gaia_eval `
        --task_ids c61d22de-5f6c-4958-a7f6-5e9707bd3466,17b5a6a3-bc87-42e8-b0fb-6ab0781ef2cc `
        --output_root HDMAS/gaia_benchmark_results/sample
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import string
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── GAIA-specific configuration ──────────────────────────────────────

# File extensions HDMAS cannot handle.
# Copilot SDK supports vision (images) via FileAttachment, so images are kept.
# Audio/video are still skipped because Copilot models are vision-only, not
# audio/video-capable today.
UNSUPPORTED_EXT = {
    ".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".wma",
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv",
}

# Image extensions that should be sent as vision attachments (also kept on disk
# in the workspace so the agent can reference them by path).
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"}

UNSUPPORTED_QUESTION_PATTERNS = [
    "listen to", "in the audio", "the recording", "the video",
    "watch the", "street view",
]

# Appended to every GAIA query so the agents emit the official format.
GAIA_TASK_PROMPT = (
    "You are answering a question from the GAIA benchmark.\n\n"
    "**Output protocol — MANDATORY:**\n"
    "Your final report (written to `answer/final.md`) MUST end with a single line "
    "of the form:\n\n"
    "    FINAL ANSWER: <your answer>\n\n"
    "Rules for `<your answer>`:\n"
    "- A number, OR as few words as possible, OR a comma-separated list of numbers "
    "and/or strings.\n"
    "- If the answer is a number: do NOT use commas as thousands separators, do NOT "
    "include units (such as $ or %) unless the question explicitly requests them.\n"
    "- If the answer is a string: do NOT use articles, do NOT use abbreviations "
    "(e.g. write 'Saint Petersburg', not 'St. Petersburg'), and write digits in "
    "plain text unless the question specifies otherwise.\n"
    "- If the answer is a comma-separated list: apply the rules above to each "
    "element.\n\n"
    "Search the web aggressively before giving up — GAIA answers are almost always "
    "verifiable from public sources. If a search fails, rephrase, try synonyms, "
    "consult primary sources (Wikipedia, official sites, PDFs, news, papers)."
)


# ── GAIA dataset loading ─────────────────────────────────────────────

def load_gaia_cases(split: str = "validation", level: Optional[int] = None,
                    task_ids: Optional[list[str]] = None,
                    first_n: Optional[int] = None) -> list[dict]:
    """Load GAIA cases from HF dataset.

    Returns list of dicts with keys: task_id, Question, Level, Final answer,
    file_name, file_path, Annotator Metadata.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit(
            "The `datasets` package is required: pip install datasets huggingface-hub"
        )

    logger.info("Loading GAIA dataset (split=%s) from HuggingFace ...", split)
    ds = load_dataset("gaia-benchmark/GAIA", "2023_all", split=split)

    cases: list[dict] = []
    for row in ds:
        cases.append(dict(row))

    logger.info("Loaded %d total GAIA cases", len(cases))

    if task_ids:
        wanted = set(task_ids)
        cases = [c for c in cases if c.get("task_id") in wanted]
        logger.info("Filtered to %d cases by --task_ids", len(cases))
    if level is not None:
        cases = [c for c in cases if int(c.get("Level", 0)) == int(level)]
        logger.info("Filtered to %d cases at Level %d", len(cases), level)
    if first_n is not None:
        cases = cases[:first_n]
        logger.info("Truncated to first %d cases", len(cases))

    return cases


def is_suitable(case: dict) -> tuple[bool, str]:
    """Check if a case is runnable by HDMAS (text-only)."""
    fname = case.get("file_name") or ""
    question = case.get("Question") or ""

    if fname:
        ext = "." + fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
        if ext in UNSUPPORTED_EXT:
            return False, f"unsupported file type: {ext}"

    q_lower = question.lower()
    for pattern in UNSUPPORTED_QUESTION_PATTERNS:
        if pattern in q_lower:
            return False, f"question references media: '{pattern}'"

    return True, "ok"


# ── GAIA official scorer ─────────────────────────────────────────────

def _normalize_number_str(number_str: str) -> float:
    for ch in ["$", "%", ","]:
        number_str = number_str.replace(ch, "")
    try:
        return float(number_str)
    except ValueError:
        return float("inf")


def _split_string(s: str, char_list: list[str] = [",", ";"]) -> list[str]:
    pattern = f"[{''.join(char_list)}]"
    return re.split(pattern, s)


def _normalize_str(s: str, remove_punct: bool = True) -> str:
    s = s.strip().lower()
    if remove_punct:
        s = s.translate(str.maketrans("", "", string.punctuation))
    s = re.sub(r"\s+", " ", s)
    return s


def _is_float(element) -> bool:
    try:
        float(element)
        return True
    except (ValueError, TypeError):
        return False


def gaia_scorer(model_answer: str, ground_truth: str) -> bool:
    """Official GAIA scoring (exact match after normalization)."""
    if model_answer is None:
        model_answer = ""
    model_answer = str(model_answer).strip()
    ground_truth = str(ground_truth).strip()

    if _is_float(ground_truth):
        return _normalize_number_str(model_answer) == float(ground_truth)

    if any(c in ground_truth for c in [",", ";"]):
        gt_list = [s.strip() for s in _split_string(ground_truth)]
        ma_list = [s.strip() for s in _split_string(model_answer)]
        if len(gt_list) != len(ma_list):
            return False
        comparisons = []
        for gt_elem, ma_elem in zip(gt_list, ma_list):
            if _is_float(gt_elem):
                comparisons.append(_normalize_number_str(ma_elem) == float(gt_elem))
            else:
                comparisons.append(_normalize_str(ma_elem, True) == _normalize_str(gt_elem, True))
        return all(comparisons)

    return _normalize_str(model_answer, True) == _normalize_str(ground_truth, True)


# ── Answer extraction ────────────────────────────────────────────────

_FINAL_ANSWER_RE = re.compile(r"FINAL ANSWER\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def extract_final_answer(text: str) -> str:
    """Pull the last 'FINAL ANSWER: ...' line from the response text."""
    if not text:
        return ""
    matches = _FINAL_ANSWER_RE.findall(text)
    if matches:
        return matches[-1].strip().strip("`*_ \"'")
    # Fallback: use last non-empty line
    for line in reversed(text.strip().splitlines()):
        if line.strip():
            return line.strip().strip("`*_ \"'")
    return ""


# ── Single-case run ──────────────────────────────────────────────────

async def run_single_async(
    query_text: str,
    output_dir: Path,
    agent_count: int,
    model: str,
    timeout: float,
    task_prompt: str,
    attachments: Optional[list] = None,
) -> tuple[str, dict]:
    """Run HDMAS on a single query.

    Returns (concatenated_answer_text, raw_result_dict).
    """
    from HDMAS.orchestrator import Orchestrator

    workspace = str(output_dir / "workspace")
    log_dir = str(output_dir / "logs")

    orch = Orchestrator(
        query=query_text,
        n_agents=agent_count,
        workspace=workspace,
        log_dir=log_dir,
        model=model,
        timeout=timeout,
        task_prompt=task_prompt,
        attachments=attachments,
    )

    result = await orch.run()
    answer_files = result.get("answer_files", {}) or {}

    # Prefer answer/final.md; otherwise concatenate all *.md under answer/.
    answer_text = ""
    for priority in ["answer/final.md", "answer/result.md", "answer/answer.md"]:
        if priority in answer_files:
            answer_text = answer_files[priority]
            break
    if not answer_text:
        md_parts = [
            f"\n--- {p} ---\n{c}"
            for p, c in sorted(answer_files.items())
            if p.endswith(".md")
        ]
        if md_parts:
            answer_text = "\n".join(md_parts)
    if not answer_text and answer_files:
        answer_text = next(iter(answer_files.values()))

    return answer_text, result


def run_single(query_text, output_dir, agent_count, model, timeout, task_prompt,
               attachments=None):
    return asyncio.run(run_single_async(
        query_text, output_dir, agent_count, model, timeout, task_prompt,
        attachments=attachments,
    ))


# ── GAIA query construction ──────────────────────────────────────────

def build_query(case: dict, attached_path: Optional[Path]) -> str:
    """Construct the user-visible query for a GAIA case."""
    q = case["Question"].strip()
    parts = [q]
    if attached_path is not None:
        rel = attached_path.name
        ext = attached_path.suffix.lower()
        if ext in IMAGE_EXT:
            parts.append(
                f"\nAn image is attached (also saved at `{rel}` in your workspace "
                f"root). Use vision to read it."
            )
        else:
            parts.append(
                f"\nAn input file is attached at `{rel}` (located in your workspace "
                f"root). Read it with the appropriate tool before answering."
            )
    return "\n".join(parts)


def build_attachments(attached_path: Optional[Path]) -> Optional[list]:
    """Build Copilot SDK attachment list for a GAIA case (None if no file).

    Always send a FileAttachment so the model can either (a) treat it as a
    vision input when supported, or (b) read it via tools. Path is absolute so
    it works regardless of agent CWD.
    """
    if attached_path is None:
        return None
    return [{
        "type": "file",
        "path": str(attached_path.resolve()),
        "displayName": attached_path.name,
    }]


def stage_attached_file(case: dict, ds_split: str, workspace_dir: Path) -> Optional[Path]:
    """Copy the GAIA-attached file into the workspace root.

    Tries `case['file_path']` first (set by HF datasets when files are local),
    then falls back to looking under HF cache via the same dataset.
    Returns the destination path or None.
    """
    fname = case.get("file_name") or ""
    if not fname:
        return None

    src_path = case.get("file_path") or ""
    if src_path and Path(src_path).exists():
        src = Path(src_path)
    else:
        # File not staged locally — skip gracefully.
        logger.warning("Attached file %s not found locally for task %s; "
                       "running without the file.", fname, case.get("task_id"))
        return None

    workspace_dir.mkdir(parents=True, exist_ok=True)
    dst = workspace_dir / fname
    try:
        shutil.copy2(src, dst)
        logger.info("  Staged attached file: %s", dst)
        return dst
    except Exception as e:
        logger.warning("  Failed to stage attached file: %s", e)
        return None


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="HDMAS GAIA benchmark runner")
    parser.add_argument("--output_root", type=str, required=True,
                        help="Output directory for this run")
    parser.add_argument("--split", type=str, default="validation",
                        choices=["validation", "test"],
                        help="GAIA split (validation has answers; test does not)")
    parser.add_argument("--level", type=int, default=None, choices=[1, 2, 3],
                        help="Filter to a single difficulty level")
    parser.add_argument("--first_n", type=int, default=None,
                        help="Run first N cases (after filtering)")
    parser.add_argument("--task_ids", type=str, default=None,
                        help="Comma-separated GAIA task_id list")
    parser.add_argument("--include_unsuitable", action="store_true",
                        help="Do NOT skip image/audio/video cases")
    parser.add_argument("--agent_count", type=int, default=3)
    parser.add_argument("--model", type=str, default="gpt-4.1")
    parser.add_argument("--timeout", type=float, default=1800.0,
                        help="Per-case wall-clock timeout in seconds")
    parser.add_argument("--stage", type=str, default="both",
                        choices=["infer", "eval", "both"])
    parser.add_argument("--resume", action="store_true",
                        help="Skip cases whose response/eval already exist")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    # Persist the run config
    (output_root / "run_config.json").write_text(
        json.dumps(vars(args), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    task_ids = [t.strip() for t in args.task_ids.split(",")] if args.task_ids else None
    cases = load_gaia_cases(
        split=args.split, level=args.level,
        task_ids=task_ids, first_n=None,  # apply first_n after filtering
    )

    # Suitability filter
    skipped = []
    if not args.include_unsuitable:
        kept = []
        for c in cases:
            ok, reason = is_suitable(c)
            if ok:
                kept.append(c)
            else:
                skipped.append({"task_id": c.get("task_id"), "reason": reason})
        cases = kept
        logger.info("After multimodal filter: %d cases kept, %d skipped",
                    len(cases), len(skipped))

    if args.first_n is not None:
        cases = cases[: args.first_n]
        logger.info("Truncated to first %d cases", len(cases))

    if skipped:
        (output_root / "skipped_cases.json").write_text(
            json.dumps(skipped, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    summary_rows: list[dict] = []
    n_correct = 0
    n_evaluated = 0
    n_resumed = 0

    for idx, case in enumerate(cases, 1):
        task_id = case["task_id"]
        level = case.get("Level", "?")
        gt = (case.get("Final answer") or "").strip()

        case_dir = output_root / task_id
        case_dir.mkdir(parents=True, exist_ok=True)

        resp_path = output_root / f"{task_id}_response.jsonl"
        eval_path = output_root / f"{task_id}_eval_result.json"

        # --resume handling
        if args.resume:
            if args.stage == "infer" and resp_path.exists():
                logger.info("[%d/%d] Skipping %s (response exists)", idx, len(cases), task_id)
                n_resumed += 1; continue
            if args.stage == "eval" and eval_path.exists():
                logger.info("[%d/%d] Skipping %s (eval exists)", idx, len(cases), task_id)
                n_resumed += 1; continue
            if args.stage == "both" and resp_path.exists() and eval_path.exists():
                logger.info("[%d/%d] Skipping %s (response+eval exist)", idx, len(cases), task_id)
                n_resumed += 1
                # Still load eval for summary aggregation
                try:
                    prev = json.loads(eval_path.read_text(encoding="utf-8"))
                    summary_rows.append(prev)
                    if prev.get("is_correct"): n_correct += 1
                    n_evaluated += 1
                except Exception:
                    pass
                continue

        logger.info("[%d/%d] Level %s | %s | %s",
                    idx, len(cases), level, task_id[:8],
                    case["Question"][:80].replace("\n", " "))

        # --- Inference ---
        response_text = ""
        infer_error = ""
        if args.stage in ("infer", "both"):
            workspace_dir = case_dir / "workspace"
            attached = stage_attached_file(case, args.split, workspace_dir)
            query_text = build_query(case, attached)
            attachments = build_attachments(attached)

            t0 = time.time()
            try:
                response_text, _ = run_single(
                    query_text=query_text,
                    output_dir=case_dir,
                    agent_count=args.agent_count,
                    model=args.model,
                    timeout=args.timeout,
                    task_prompt=GAIA_TASK_PROMPT,
                    attachments=attachments,
                )
            except Exception as e:
                infer_error = f"{type(e).__name__}: {e}"
                logger.error("Inference failed for %s: %s", task_id, infer_error)
                traceback.print_exc()
            elapsed = round(time.time() - t0, 1)

            resp_path.write_text(
                json.dumps({
                    "task_id": task_id,
                    "level": level,
                    "question": case["Question"],
                    "file_name": case.get("file_name") or "",
                    "ground_truth": gt,
                    "response": response_text,
                    "duration_sec": elapsed,
                    "error": infer_error,
                }, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        # --- Evaluation ---
        if args.stage in ("eval", "both"):
            if not response_text and resp_path.exists():
                try:
                    response_text = json.loads(
                        resp_path.read_text(encoding="utf-8").strip()
                    ).get("response", "")
                except Exception:
                    response_text = ""

            extracted = extract_final_answer(response_text)
            is_correct = False
            try:
                if gt and extracted:
                    is_correct = gaia_scorer(extracted, gt)
            except Exception as e:
                logger.warning("Scorer error for %s: %s", task_id, e)

            eval_record = {
                "task_id": task_id,
                "level": level,
                "question": case["Question"],
                "ground_truth": gt,
                "extracted_answer": extracted,
                "is_correct": bool(is_correct),
                "has_response": bool(response_text),
                "error": infer_error,
            }
            eval_path.write_text(
                json.dumps(eval_record, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            summary_rows.append(eval_record)
            n_evaluated += 1
            if is_correct:
                n_correct += 1
            logger.info("  → extracted=%r | gt=%r | %s",
                        extracted[:80], gt[:80],
                        "CORRECT" if is_correct else "WRONG")

        # Update aggregate summary after every case
        _write_summary(output_root, summary_rows, args, n_correct, n_evaluated, skipped)

    logger.info("=" * 60)
    logger.info("DONE. Evaluated: %d | Correct: %d | Accuracy: %.1f%% | Resumed: %d",
                n_evaluated, n_correct,
                100.0 * n_correct / n_evaluated if n_evaluated else 0.0,
                n_resumed)
    logger.info("Results: %s", output_root)


def _write_summary(output_root: Path, rows: list[dict], args,
                   n_correct: int, n_evaluated: int, skipped: list[dict]):
    by_level: dict[str, dict[str, int]] = {}
    for r in rows:
        lvl = str(r.get("level", "?"))
        bucket = by_level.setdefault(lvl, {"total": 0, "correct": 0})
        bucket["total"] += 1
        if r.get("is_correct"):
            bucket["correct"] += 1

    summary = {
        "config": vars(args),
        "n_evaluated": n_evaluated,
        "n_correct": n_correct,
        "overall_accuracy": (n_correct / n_evaluated) if n_evaluated else 0.0,
        "by_level": {
            lvl: {
                "total": v["total"],
                "correct": v["correct"],
                "accuracy": (v["correct"] / v["total"]) if v["total"] else 0.0,
            }
            for lvl, v in sorted(by_level.items())
        },
        "n_skipped_unsuitable": len(skipped),
        "rows": rows,
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
