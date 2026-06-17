"""
Batch evaluation runner for HDMAS Copilot edition.

Usage:
    python -m HDMAS.batch_eval --first_n 5
    python -m HDMAS.batch_eval --instance_ids ws_en_001,ws_en_002
    python -m HDMAS.batch_eval --first_n 10 --output_root HDMAS/batch_results/test_run
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _widesearch_root() -> Path:
    """Resolve the WideSearch repo root.

    Priority:
      1. ``WIDESEARCH_ROOT`` environment variable (absolute path).
      2. Sibling of this repo: ``<parent-of-HDMAS>/WideSearch``.
    Raises if neither exists.
    """
    env = os.getenv("WIDESEARCH_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"WIDESEARCH_ROOT={env} does not exist")
    sibling = Path(__file__).resolve().parent.parent / "WideSearch"
    if sibling.exists():
        return sibling
    raise FileNotFoundError(
        "WideSearch repo not found. Set WIDESEARCH_ROOT in your .env or place "
        f"the repo at {sibling}."
    )


# ── Load WideSearch queries ──────────────────────────────────

def load_queries(instance_ids=None, first_n=None):
    root_str = str(_widesearch_root())
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

    queries = [loader.load_query_by_instance_id(iid) for iid in selected]
    logger.info("Loaded %d WideSearch queries", len(queries))
    return queries


# ── Single HDMAS run ─────────────────────────────────────────

async def run_single_async(query_text: str, output_dir: Path, agent_count: int,
                           model: str, timeout: float, task_prompt: str = "") -> str:
    """Run HDMAS on a single query. Returns final answer text."""
    from HDMAS.orchestrator import Orchestrator

    workspace = str(output_dir / "workspace")
    log_dir = str(output_dir / "logs")

    logger.info("  Starting HDMAS with %d agents, model=%s", agent_count, model)

    orch = Orchestrator(
        query=query_text,
        n_agents=agent_count,
        workspace=workspace,
        log_dir=log_dir,
        model=model,
        timeout=timeout,
        task_prompt=task_prompt,
    )

    result = await orch.run()
    answer_files = result.get("answer_files", {})

    # Extract answer text (prefer final.md, then any .md, then any file)
    answer_text = ""
    for priority in ["answer/final.md", "answer/result.md", "answer/answer.md"]:
        if priority in answer_files:
            answer_text = answer_files[priority]
            break
    if not answer_text:
        for path, content in sorted(answer_files.items()):
            if path.endswith(".md"):
                answer_text = content
                break
    if not answer_text and answer_files:
        answer_text = next(iter(answer_files.values()))

    return answer_text


def run_single(query_text: str, output_dir: Path, agent_count: int,
               model: str, timeout: float, task_prompt: str = "") -> str:
    """Sync wrapper for run_single_async."""
    return asyncio.run(run_single_async(
        query_text, output_dir, agent_count, model, timeout, task_prompt,
    ))


# ── Evaluation ──────────────────────────────────────────────────────

def _patch_widesearch_eval_client():
    """Patch WideSearch's eval LLM client to use Azure AD auth (same as HDMAS_v4)."""
    from dotenv import load_dotenv
    load_dotenv()
    endpoint = os.getenv("AZURE_OPENAI_EVAL_ENDPOINT", "").strip()
    if not endpoint:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").split(",")[0].strip()
    if not endpoint:
        logger.warning("AZURE_OPENAI_ENDPOINT not set; eval LLM calls may fail")
        return

    root_str = str(_widesearch_root())
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
    def _openai_complete_azure_ad(
        base_url, api_key, messages, tools=None,
        model_name="gpt-4.1", retry_if_empty=False, **kwargs
    ):
        client = AzureOpenAI(
            azure_endpoint=base_url,
            azure_ad_token_provider=token_provider,
            api_version="2025-01-01-preview",
            timeout=300,
        )
        completion = client.chat.completions.create(
            messages=messages, model=model_name, tools=tools, **kwargs
        )
        message = completion.choices[0].message
        if retry_if_empty and not message.content and not message.tool_calls:
            raise RuntimeError("empty response, retry")
        return message

    ws_llm.openai_complete = _openai_complete_azure_ad
    logger.info("Patched WideSearch eval LLM to use Azure AD auth at %s", endpoint)


_eval_patched = False


def evaluate_single(instance_id, response_text, output_dir, eval_model="gpt-4.1"):
    """Evaluate a single response against ground truth."""
    global _eval_patched
    try:
        root_str = str(_widesearch_root())
        if root_str not in sys.path:
            sys.path.insert(0, root_str)

        if not _eval_patched:
            _patch_widesearch_eval_client()
            _eval_patched = True

        from src.evaluation.data_loader import WideSearchDataLoaderHF, WideSearchResponse, WideSearchResponseLoader
        from src.evaluation.evaluation import evaluate_single_query

        loader = WideSearchDataLoaderHF()
        query = loader.load_query_by_instance_id(instance_id)

        # Load response via WideSearchResponseLoader for proper parsing
        resp_path = output_dir / f"{instance_id}_response.jsonl"
        response_list = WideSearchResponseLoader.load_response(str(resp_path))
        response = response_list[0] if response_list else WideSearchResponse(
            instance_id=instance_id, response=response_text,
        )

        result_save_path = output_dir / f"{instance_id}_eval_result.csv"
        result = evaluate_single_query(query, response, str(result_save_path))

        import dataclasses
        result_path = output_dir / f"{instance_id}_eval_result.json"
        result_dict = dataclasses.asdict(result)
        result_path.write_text(json.dumps(result_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("  Eval %s: score=%.3f, item_f1=%.3f, row_f1=%.3f",
                     instance_id, result.score, result.f1_by_item, result.f1_by_row)
        return result_dict

    except Exception as e:
        logger.error("Evaluation failed for %s: %s", instance_id, e, exc_info=True)
        err_result = {
            "instance_id": instance_id,
            "score": 0, "precision_by_row": 0, "recall_by_row": 0, "f1_by_row": 0,
            "precision_by_item": 0, "recall_by_item": 0, "f1_by_item": 0,
            "msg": f"evaluation error: {e}",
        }
        result_path = output_dir / f"{instance_id}_eval_result.json"
        result_path.write_text(json.dumps(err_result, indent=2, ensure_ascii=False), encoding="utf-8")
        return err_result


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="HDMAS Copilot batch evaluation")
    parser.add_argument("--instance_ids", type=str, default=None,
                        help="Comma-separated instance IDs")
    parser.add_argument("--first_n", type=int, default=None,
                        help="Run first N queries")
    parser.add_argument("--output_root", type=str, default=None,
                        help="Output directory root")
    parser.add_argument("--agent_count", type=int, default=3)
    parser.add_argument("--model", type=str, default="gpt-4.1")
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument("--stage", type=str, default="both",
                        choices=["infer", "eval", "both"])
    parser.add_argument("--eval_model", type=str, default="gpt-4.1")
    parser.add_argument("--resume", action="store_true",
                        help="Skip cases that already have results in output_root")
    args = parser.parse_args()

    instance_ids = args.instance_ids.split(",") if args.instance_ids else None
    output_root = Path(args.output_root) if args.output_root else Path(
        f"HDMAS/batch_results/{time.strftime('%Y%m%d_%H%M%S')}"
    )
    output_root.mkdir(parents=True, exist_ok=True)

    queries = load_queries(instance_ids, args.first_n)

    # Import task prompts
    try:
        from HDMAS.task_prompts import WIDESEARCH_GLOBAL, WIDESEARCH_PER_CASE
    except ImportError:
        WIDESEARCH_GLOBAL = ""
        WIDESEARCH_PER_CASE = {}

    skipped = 0
    for query in queries:
        iid = query.instance_id
        case_dir = output_root / iid
        case_dir.mkdir(parents=True, exist_ok=True)

        # --resume: skip cases that already have results
        if args.resume:
            resp_path = output_root / f"{iid}_response.jsonl"
            eval_path = output_root / f"{iid}_eval_result.json"
            if args.stage == "infer" and resp_path.exists():
                logger.info("Skipping %s (response exists, --resume)", iid)
                skipped += 1
                continue
            if args.stage == "eval" and eval_path.exists():
                logger.info("Skipping %s (eval exists, --resume)", iid)
                skipped += 1
                continue
            if args.stage == "both" and resp_path.exists() and eval_path.exists():
                logger.info("Skipping %s (response+eval exist, --resume)", iid)
                skipped += 1
                continue

        logger.info("Processing %s ...", iid)

        task_prompt = WIDESEARCH_GLOBAL
        if iid in WIDESEARCH_PER_CASE:
            task_prompt += "\n" + WIDESEARCH_PER_CASE[iid]

        # Infer
        if args.stage in ("infer", "both"):
            response_text = run_single(
                query_text=query.query,
                output_dir=case_dir,
                agent_count=args.agent_count,
                model=args.model,
                timeout=args.timeout,
                task_prompt=task_prompt,
            )

            # Save response
            resp_path = output_root / f"{iid}_response.jsonl"
            resp_data = {
                "instance_id": iid,
                "response": response_text,
                "messages": None,
                "trial_idx": 0,
            }
            resp_path.write_text(
                json.dumps(resp_data, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        # Eval
        if args.stage in ("eval", "both"):
            resp_path = output_root / f"{iid}_response.jsonl"
            if resp_path.exists():
                resp_data = json.loads(resp_path.read_text(encoding="utf-8").strip())
                response_text = resp_data.get("response", "")
            evaluate_single(iid, response_text, output_root, eval_model=args.eval_model)

    if args.resume and skipped:
        logger.info("Resumed run: skipped %d already-completed case(s)", skipped)


if __name__ == "__main__":
    main()
