"""
Bare-bones single-agent Copilot runner for benchmarks.

Originally built for WideSearch; extended to also run GAIA. The benchmark is
chosen with `--benchmark {widesearch,gaia}`. Each benchmark has its own
system prompt (WIDESEARCH_PROMPT / GAIA_PROMPT) and its own loader + evaluator;
the Copilot session machinery is shared.
"""

import argparse
import asyncio
import dataclasses
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

from copilot import CopilotClient, SubprocessConfig
from copilot.generated.session_events import SessionEvent, SessionEventType
from copilot.session import PermissionHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-5s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

MODEL = "gpt-5.4"
TIMEOUT = 1800.0  # 30 min

# ── System prompts (one per benchmark; pick with --benchmark) ────────

WIDESEARCH_PROMPT = """\
You are a research assistant. The user will give you a data-collection task.

Your job:
1. Search the web thoroughly to find ALL requested data.
2. For each piece of data, verify it from official or reliable sources.
3. Output the final result as a single Markdown table inside ```markdown``` fences.
4. Every cell must be filled — never leave blanks. If data truly cannot be found after exhaustive search, write "Not found".
5. Match the user's requested column names and format exactly.
6. Output ONLY the markdown table — no commentary before or after.
"""

GAIA_PROMPT = """\
You are answering a question from the GAIA benchmark. Use web search and any
attached file aggressively to ground your answer in primary sources.

**Output protocol — MANDATORY.**
After your reasoning, end your final assistant message with a single line of
the form:

    FINAL ANSWER: <your answer>

Rules for `<your answer>`:
- A number, OR as few words as possible, OR a comma-separated list of numbers
  and/or strings.
- If the answer is a number: do NOT use commas as thousands separators, do NOT
  include units (such as $ or %) unless the question explicitly requests them.
- If the answer is a string: do NOT use articles, do NOT use abbreviations
  (e.g. write 'Saint Petersburg', not 'St. Petersburg'), and write digits in
  plain text unless the question specifies otherwise.
- If the answer is a comma-separated list: apply the rules above to each
  element.

Search aggressively before giving up. GAIA answers are almost always verifiable
from public sources (Wikipedia, official sites, PDFs, news, papers).
"""

PROMPTS = {
    "widesearch": WIDESEARCH_PROMPT,
    "gaia": GAIA_PROMPT,
}


# ── Generic single-session runner ────────────────────────────────────

def _pick_final_message(messages: list[str]) -> str:
    """Choose the model's final answer from the streamed assistant messages.

    Copilot streams one or more interim 'status' messages (e.g. "I'm
    narrowing it down...") followed by a short final commit (often
    'FINAL ANSWER: <value>'). Picking ``max(by len)`` systematically
    selects the verbose interim message and discards the real answer.

    Strategy:
      1. Prefer the **last** message that contains an explicit
         ``FINAL ANSWER:`` line (matches the GAIA / WideSearch protocol).
      2. Otherwise fall back to the **last** assistant message
         (Copilot's terminal commit).
    """
    if not messages:
        return ""
    final_marker = [m for m in messages if _FINAL_ANSWER_RE.search(m)]
    if final_marker:
        return final_marker[-1]
    return messages[-1]


async def run_single(query: str, system_prompt: str, model: str = MODEL,
                     timeout: float = TIMEOUT,
                     attachments: Optional[list] = None,
                     log_dir: Path | None = None) -> str:
    """Run one Copilot session on `query`. Returns the final response text."""

    client = CopilotClient(SubprocessConfig(), auto_start=True)
    await client.start()

    result_text = ""
    event_log = []
    t_start = time.time()

    try:
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model=model,
            system_message={"content": system_prompt},
            infinite_sessions={"enabled": True},
        ) as session:
            done = asyncio.Event()
            messages = []

            def on_event(event: SessionEvent):
                nonlocal result_text
                elapsed = round(time.time() - t_start, 1)
                etype = event.type.name if hasattr(event.type, "name") else str(event.type)

                if event.type == SessionEventType.ASSISTANT_MESSAGE:
                    content = getattr(event.data, "content", "") or ""
                    if content:
                        messages.append(content)
                        result_text = content
                        preview = content[:200].replace("\n", " ")
                        logger.info("  [%.1fs] ASSISTANT_MESSAGE (%d chars): %s%s",
                                    elapsed, len(content), preview, "..." if len(content) > 200 else "")
                        event_log.append({"t": elapsed, "type": etype, "chars": len(content), "preview": preview})
                elif event.type == SessionEventType.TOOL_EXECUTION_START:
                    tool_name = getattr(event.data, "name", None) or getattr(event.data, "tool_name", "unknown")
                    args_raw = getattr(event.data, "arguments", None) or getattr(event.data, "input", "")
                    args_preview = str(args_raw)[:150]
                    logger.info("  [%.1fs] TOOL_START: %s(%s)", elapsed, tool_name, args_preview)
                    event_log.append({"t": elapsed, "type": etype, "tool": tool_name, "args": args_preview})
                elif event.type == SessionEventType.TOOL_EXECUTION_COMPLETE:
                    result_preview = str(getattr(event.data, "content", ""))[:100]
                    logger.info("  [%.1fs] TOOL_DONE: %s...", elapsed, result_preview)
                    event_log.append({"t": elapsed, "type": etype, "preview": result_preview})
                elif event.type == SessionEventType.SESSION_IDLE:
                    logger.info("  [%.1fs] SESSION_IDLE", elapsed)
                    event_log.append({"t": elapsed, "type": etype})
                    done.set()
                else:
                    event_log.append({"t": elapsed, "type": etype})

            session.on(on_event)
            send_kwargs = {}
            if attachments:
                send_kwargs["attachments"] = attachments
            await session.send(query, **send_kwargs)

            try:
                await asyncio.wait_for(done.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning("Session timed out after %.0fs", timeout)
                event_log.append({"t": round(time.time() - t_start, 1), "type": "TIMEOUT"})

            if messages:
                result_text = _pick_final_message(messages)

    finally:
        await client.stop()

    total_time = round(time.time() - t_start, 1)
    logger.info("  Session done in %.1fs, %d messages, final answer %d chars",
                total_time, len(messages), len(result_text))

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in event_log) + "\n",
            encoding="utf-8",
        )
        (log_dir / "final_answer.md").write_text(result_text, encoding="utf-8")
        (log_dir / "summary.json").write_text(json.dumps({
            "total_time_s": total_time,
            "n_messages": len(messages),
            "n_events": len(event_log),
            "answer_chars": len(result_text),
            "timed_out": any(e.get("type") == "TIMEOUT" for e in event_log),
        }, indent=2, ensure_ascii=False), encoding="utf-8")

    return result_text


# =====================================================================
# WideSearch
# =====================================================================

def load_widesearch_queries(instance_ids=None, first_n=None):
    widesearch_root = Path(__file__).resolve().parent.parent.parent / "WideSearch"
    root_str = str(widesearch_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    from src.evaluation.data_loader import WideSearchDataLoaderHF

    loader = WideSearchDataLoaderHF()
    all_ids = loader.get_instance_id_list()

    if instance_ids:
        selected = [iid for iid in instance_ids if iid in all_ids]
    elif first_n:
        selected = all_ids[:first_n]
    else:
        selected = all_ids

    return [loader.load_query_by_instance_id(iid) for iid in selected]


def _patch_widesearch_eval_client():
    from dotenv import load_dotenv
    load_dotenv()
    endpoint = os.getenv("AZURE_OPENAI_EVAL_ENDPOINT", "").strip()
    if not endpoint:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").split(",")[0].strip()
    if not endpoint:
        return

    widesearch_root = Path(__file__).resolve().parent.parent.parent / "WideSearch"
    root_str = str(widesearch_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from openai import AzureOpenAI
    from tenacity import retry, stop_after_attempt, wait_incrementing
    import src.utils.llm as ws_llm
    import src.utils.config as ws_cfg

    eval_model = os.getenv("AZURE_OPENAI_EVAL_MODEL", "gpt-4.1")
    ws_cfg.model_config["default_eval_config"]["base_url"] = endpoint
    ws_cfg.model_config["default_eval_config"]["api_key"] = "unused"
    ws_cfg.model_config["default_eval_config"]["model_name"] = eval_model

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    @retry(stop=stop_after_attempt(8), wait=wait_incrementing(8, 8))
    def _complete(base_url, api_key, messages, tools=None,
                  model_name="gpt-4.1", retry_if_empty=False, **kwargs):
        client = AzureOpenAI(
            azure_endpoint=base_url,
            azure_ad_token_provider=token_provider,
            api_version="2025-01-01-preview",
            timeout=300,
        )
        completion = client.chat.completions.create(
            messages=messages, model=model_name, tools=tools, **kwargs
        )
        msg = completion.choices[0].message
        if retry_if_empty and not msg.content and not msg.tool_calls:
            raise RuntimeError("empty response")
        return msg

    ws_llm.openai_complete = _complete
    logger.info("Patched eval client: %s", endpoint)


def evaluate_widesearch_single(instance_id, response_text, output_dir):
    widesearch_root = Path(__file__).resolve().parent.parent.parent / "WideSearch"
    root_str = str(widesearch_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    from src.evaluation.data_loader import WideSearchDataLoaderHF, WideSearchResponse, WideSearchResponseLoader
    from src.evaluation.evaluation import evaluate_single_query

    loader = WideSearchDataLoaderHF()
    query = loader.load_query_by_instance_id(instance_id)

    resp_path = output_dir / f"{instance_id}_response.jsonl"
    response_list = WideSearchResponseLoader.load_response(str(resp_path))
    response = response_list[0] if response_list else WideSearchResponse(
        instance_id=instance_id, response=response_text,
    )

    result_csv = output_dir / f"{instance_id}_eval_result.csv"
    result = evaluate_single_query(query, response, str(result_csv))

    result_dict = dataclasses.asdict(result)
    result_path = output_dir / f"{instance_id}_eval_result.json"
    result_path.write_text(json.dumps(result_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("  %s: item_f1=%.3f row_f1=%.3f", instance_id, result.f1_by_item, result.f1_by_row)
    return result_dict


def run_widesearch(args):
    instance_ids = args.instance_ids.split(",") if args.instance_ids else None
    output_root = Path(args.output_root) if args.output_root else Path(
        f"COPILOT_FOR_Widesearch/results/widesearch_{time.strftime('%Y%m%d_%H%M%S')}"
    )
    output_root.mkdir(parents=True, exist_ok=True)

    queries = load_widesearch_queries(instance_ids, args.first_n)
    logger.info("Loaded %d WideSearch queries", len(queries))

    for query in queries:
        iid = query.instance_id
        resp_path = output_root / f"{iid}_response.jsonl"

        if args.stage in ("infer", "both") and resp_path.exists():
            logger.info("Skipping %s (response already exists)", iid)
            if args.stage == "both":
                eval_path = output_root / f"{iid}_eval_result.json"
                if not eval_path.exists():
                    _patch_widesearch_eval_client()
                    evaluate_widesearch_single(iid, "", output_root)
            continue

        logger.info("Processing %s ...", iid)

        if args.stage in ("infer", "both"):
            case_log_dir = output_root / iid
            t0 = time.time()
            response_text = asyncio.run(run_single(
                query=query.query,
                system_prompt=WIDESEARCH_PROMPT,
                model=args.model, timeout=args.timeout,
                log_dir=case_log_dir,
            ))
            elapsed = round(time.time() - t0, 1)
            logger.info("  %s: %.1fs, response %d chars", iid, elapsed, len(response_text))

            resp_path.write_text(
                json.dumps({"instance_id": iid, "response": response_text,
                            "messages": None, "trial_idx": 0},
                           ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        if args.stage in ("eval", "both"):
            _patch_widesearch_eval_client()
            evaluate_widesearch_single(iid, "", output_root)


# =====================================================================
# GAIA
# =====================================================================

GAIA_UNSUPPORTED_EXT = {
    ".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".wma",
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv",
}
GAIA_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"}
GAIA_UNSUPPORTED_QUESTION_PATTERNS = [
    "listen to", "in the audio", "the recording", "the video",
    "watch the", "street view",
]


def gaia_load_cases(split="validation", level=None, task_ids=None, first_n=None):
    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit("pip install datasets huggingface-hub")

    logger.info("Loading GAIA dataset (split=%s) ...", split)
    ds = load_dataset("gaia-benchmark/GAIA", "2023_all", split=split)
    cases = [dict(row) for row in ds]
    logger.info("Loaded %d total GAIA cases", len(cases))

    if task_ids:
        wanted = set(task_ids)
        cases = [c for c in cases if c.get("task_id") in wanted]
        logger.info("Filtered to %d by --task_ids", len(cases))
    if level is not None:
        cases = [c for c in cases if int(c.get("Level", 0)) == int(level)]
        logger.info("Filtered to %d at Level %d", len(cases), level)
    if first_n is not None:
        cases = cases[:first_n]
        logger.info("Truncated to first %d", len(cases))
    return cases


def gaia_is_suitable(case):
    fname = case.get("file_name") or ""
    question = case.get("Question") or ""
    if fname:
        ext = "." + fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
        if ext in GAIA_UNSUPPORTED_EXT:
            return False, f"unsupported file: {ext}"
    q_lower = question.lower()
    for pat in GAIA_UNSUPPORTED_QUESTION_PATTERNS:
        if pat in q_lower:
            return False, f"question references media: '{pat}'"
    return True, "ok"


def _normalize_number_str(s):
    for ch in ["$", "%", ","]:
        s = s.replace(ch, "")
    try:
        return float(s)
    except ValueError:
        return float("inf")


def _split_string(s, char_list=[",", ";"]):
    return re.split(f"[{''.join(char_list)}]", s)


def _normalize_str(s, remove_punct=True):
    s = s.strip().lower()
    if remove_punct:
        s = s.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", s)


def _is_float(x):
    try:
        float(x); return True
    except (ValueError, TypeError):
        return False


def gaia_scorer(model_answer, ground_truth):
    """Official GAIA scoring (exact match after normalization)."""
    model_answer = str(model_answer or "").strip()
    ground_truth = str(ground_truth or "").strip()
    if _is_float(ground_truth):
        return _normalize_number_str(model_answer) == float(ground_truth)
    if any(c in ground_truth for c in [",", ";"]):
        gt_list = [s.strip() for s in _split_string(ground_truth)]
        ma_list = [s.strip() for s in _split_string(model_answer)]
        if len(gt_list) != len(ma_list):
            return False
        out = []
        for gt, ma in zip(gt_list, ma_list):
            if _is_float(gt):
                out.append(_normalize_number_str(ma) == float(gt))
            else:
                out.append(_normalize_str(ma) == _normalize_str(gt))
        return all(out)
    return _normalize_str(model_answer) == _normalize_str(ground_truth)


_FINAL_ANSWER_RE = re.compile(r"FINAL ANSWER\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def gaia_extract_final_answer(text):
    if not text:
        return ""
    matches = _FINAL_ANSWER_RE.findall(text)
    if matches:
        return matches[-1].strip().strip("`*_ \"'")
    for line in reversed(text.strip().splitlines()):
        if line.strip():
            return line.strip().strip("`*_ \"'")
    return ""


def gaia_stage_attached_file(case, dst_dir: Path):
    fname = case.get("file_name") or ""
    if not fname:
        return None
    src_path = case.get("file_path") or ""
    if not (src_path and Path(src_path).exists()):
        logger.warning("Attached file %s not found locally for %s; running without it.",
                       fname, case.get("task_id"))
        return None
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / fname
    try:
        shutil.copy2(src_path, dst)
        logger.info("  Staged attached file: %s", dst)
        return dst
    except Exception as e:
        logger.warning("  Failed to stage attached file: %s", e)
        return None


def gaia_build_query(case, attached_path: Optional[Path]) -> str:
    q = case["Question"].strip()
    parts = [q]
    if attached_path is not None:
        rel = attached_path.name
        ext = attached_path.suffix.lower()
        if ext in GAIA_IMAGE_EXT:
            parts.append(f"\nAn image is attached (`{rel}`). Use vision to read it.")
        else:
            parts.append(f"\nAn input file is attached at `{rel}`. Read it with the appropriate tool.")
    return "\n".join(parts)


def gaia_build_attachments(attached_path: Optional[Path]):
    if attached_path is None:
        return None
    return [{
        "type": "file",
        "path": str(attached_path.resolve()),
        "displayName": attached_path.name,
    }]


def _write_gaia_summary(output_root: Path, rows: list, args, n_correct: int, n_eval: int, skipped: list):
    by_level = {}
    for r in rows:
        lvl = str(r.get("level", "?"))
        b = by_level.setdefault(lvl, {"total": 0, "correct": 0})
        b["total"] += 1
        if r.get("is_correct"):
            b["correct"] += 1
    summary = {
        "config": vars(args),
        "n_evaluated": n_eval,
        "n_correct": n_correct,
        "overall_accuracy": (n_correct / n_eval) if n_eval else 0.0,
        "by_level": {
            lvl: {
                "total": v["total"],
                "correct": v["correct"],
                "accuracy": (v["correct"] / v["total"]) if v["total"] else 0.0,
            } for lvl, v in sorted(by_level.items())
        },
        "n_skipped_unsuitable": len(skipped),
        "rows": rows,
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def run_gaia(args):
    output_root = Path(args.output_root) if args.output_root else Path(
        f"COPILOT_FOR_Widesearch/results/gaia_{time.strftime('%Y%m%d_%H%M%S')}"
    )
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "run_config.json").write_text(
        json.dumps(vars(args), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    task_ids = [t.strip() for t in args.task_ids.split(",")] if args.task_ids else None
    cases = gaia_load_cases(split=args.split, level=args.level,
                            task_ids=task_ids, first_n=None)

    skipped = []
    if not args.include_unsuitable:
        kept = []
        for c in cases:
            ok, reason = gaia_is_suitable(c)
            if ok:
                kept.append(c)
            else:
                skipped.append({"task_id": c.get("task_id"), "reason": reason})
        cases = kept
        logger.info("After multimodal filter: %d kept, %d skipped", len(cases), len(skipped))

    if args.first_n is not None:
        cases = cases[: args.first_n]
        logger.info("Truncated to first %d", len(cases))

    if skipped:
        (output_root / "skipped_cases.json").write_text(
            json.dumps(skipped, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    summary_rows = []
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
                try:
                    prev = json.loads(eval_path.read_text(encoding="utf-8"))
                    summary_rows.append(prev)
                    if prev.get("is_correct"): n_correct += 1
                    n_evaluated += 1
                except Exception:
                    pass
                continue

        logger.info("[%d/%d] Level %s | %s | %s", idx, len(cases), level, task_id[:8],
                    case["Question"][:80].replace("\n", " "))

        response_text = ""
        infer_error = ""

        if args.stage in ("infer", "both"):
            workspace_dir = case_dir / "workspace"
            attached = gaia_stage_attached_file(case, workspace_dir)
            query_text = gaia_build_query(case, attached)
            attachments = gaia_build_attachments(attached)

            t0 = time.time()
            try:
                response_text = asyncio.run(run_single(
                    query=query_text,
                    system_prompt=GAIA_PROMPT,
                    model=args.model, timeout=args.timeout,
                    attachments=attachments,
                    log_dir=case_dir / "logs",
                ))
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

        if args.stage in ("eval", "both"):
            if not response_text and resp_path.exists():
                try:
                    response_text = json.loads(
                        resp_path.read_text(encoding="utf-8").strip()
                    ).get("response", "")
                except Exception:
                    response_text = ""

            extracted = gaia_extract_final_answer(response_text)
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
            eval_path.write_text(json.dumps(eval_record, indent=2, ensure_ascii=False),
                                 encoding="utf-8")
            summary_rows.append(eval_record)
            n_evaluated += 1
            if is_correct:
                n_correct += 1
            logger.info("  → extracted=%r | gt=%r | %s",
                        extracted[:80], gt[:80],
                        "CORRECT" if is_correct else "WRONG")

        _write_gaia_summary(output_root, summary_rows, args, n_correct, n_evaluated, skipped)

    logger.info("=" * 60)
    logger.info("DONE. Evaluated: %d | Correct: %d | Accuracy: %.1f%% | Resumed: %d",
                n_evaluated, n_correct,
                100.0 * n_correct / n_evaluated if n_evaluated else 0.0,
                n_resumed)
    logger.info("Results: %s", output_root)


# =====================================================================
# CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="Single Copilot agent — WideSearch / GAIA runner")
    parser.add_argument("--benchmark", type=str, default="widesearch",
                        choices=list(PROMPTS.keys()),
                        help="Which benchmark to run (selects system prompt + loader + evaluator)")
    parser.add_argument("--output_root", type=str, default=None)
    parser.add_argument("--model", type=str, default=MODEL)
    parser.add_argument("--timeout", type=float, default=TIMEOUT)
    parser.add_argument("--stage", type=str, default="both", choices=["infer", "eval", "both"])
    parser.add_argument("--first_n", type=int, default=None)

    # WideSearch-only
    parser.add_argument("--instance_ids", type=str, default=None,
                        help="WideSearch: comma-separated instance ids")

    # GAIA-only
    parser.add_argument("--split", type=str, default="validation",
                        choices=["validation", "test"],
                        help="GAIA split (validation has answers; test does not)")
    parser.add_argument("--level", type=int, default=None, choices=[1, 2, 3],
                        help="GAIA: filter to a single difficulty level")
    parser.add_argument("--task_ids", type=str, default=None,
                        help="GAIA: comma-separated task_id list")
    parser.add_argument("--include_unsuitable", action="store_true",
                        help="GAIA: do NOT skip image/audio/video cases")
    parser.add_argument("--resume", action="store_true",
                        help="GAIA: skip cases whose response/eval already exist")

    args = parser.parse_args()
    if args.benchmark == "widesearch":
        run_widesearch(args)
    elif args.benchmark == "gaia":
        run_gaia(args)
    else:
        raise SystemExit(f"unknown benchmark: {args.benchmark}")


if __name__ == "__main__":
    main()
