"""
Structured event logger for HDMAS v4.

Captures every significant event (LLM calls, tool invocations, lock ops,
vote/wake signals) into a single JSONL file per run, plus per-agent JSONL
files for filtered replay.

Design goals:
  - Every event is a self-contained JSON dict on one line (JSONL)
  - Events carry enough context for full post-mortem replay
  - Thread-safe — multiple agents log concurrently
  - Zero runtime impact on agent logic (fire-and-forget)

Event schema:
  {
    "ts":        "2026-04-03T14:25:01.123",   # ISO timestamp with ms
    "seq":       42,                            # Global monotonic sequence number
    "agent":     "agent_0",                     # Which agent (or "orchestrator")
    "event":     "tool_call",                   # Event type
    "data":      { ... },                       # Event-specific payload
    "elapsed_s": 1.23                           # Optional duration
  }

Event types:
  orchestrator_start, orchestrator_done
  agent_start, agent_done
  llm_call, llm_error
  tool_call, tool_result
  lock_acquire, lock_release, lock_timeout
  vote_stop, wake_agent
  exit_reminder, context_trim
  blackboard_snapshot                          # Periodic BB state dump
"""

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Optional


class EventLogger:
    """Thread-safe JSONL event logger for deep post-mortem analysis."""

    def __init__(self, log_dir: str):
        """
        Args:
            log_dir: Directory to write log files into.
                     Creates: events.jsonl (all events), agent_<id>.jsonl (per-agent).
        """
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

        self._main_path = self._log_dir / "events.jsonl"
        self._main_file = open(self._main_path, "a", encoding="utf-8")

        self._agent_files: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._seq = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(
        self,
        agent: str,
        event: str,
        data: Optional[dict] = None,
        elapsed_s: Optional[float] = None,
    ):
        """Record a single event.

        Args:
            agent:     Originator (e.g. "agent_0", "orchestrator").
            event:     Event type string.
            data:      Arbitrary JSON-serializable payload.
            elapsed_s: Optional duration in seconds.
        """
        with self._lock:
            self._seq += 1
            seq = self._seq

        record = {
            "ts": _now_iso(),
            "seq": seq,
            "agent": agent,
            "event": event,
        }
        if data:
            record["data"] = data
        if elapsed_s is not None:
            record["elapsed_s"] = round(elapsed_s, 3)

        line = json.dumps(record, ensure_ascii=False, default=str)

        with self._lock:
            # Main log
            self._main_file.write(line + "\n")
            self._main_file.flush()

            # Per-agent log
            agent_file = self._get_agent_file(agent)
            agent_file.write(line + "\n")
            agent_file.flush()

    def log_llm_call(
        self,
        agent: str,
        call_count: int,
        elapsed_s: float,
        has_tool_calls: bool,
        content_preview: str,
        model: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ):
        """Convenience: log an LLM call with token usage."""
        self.log(agent, "llm_call", {
            "call_count": call_count,
            "model": model,
            "has_tool_calls": has_tool_calls,
            "content_preview": content_preview[:200],
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }, elapsed_s=elapsed_s)

    def log_tool_call(self, agent: str, call_count: int, tool: str, args: dict):
        """Convenience: log a tool invocation."""
        self.log(agent, "tool_call", {
            "call_count": call_count,
            "tool": tool,
            "args": _truncate_args(args),
        })

    def log_tool_result(
        self,
        agent: str,
        call_count: int,
        tool: str,
        result: str,
        elapsed_s: float,
    ):
        """Convenience: log a tool result."""
        self.log(agent, "tool_result", {
            "call_count": call_count,
            "tool": tool,
            "result_length": len(result),
            "result_preview": result[:500],
        }, elapsed_s=elapsed_s)

    def log_blackboard_snapshot(self, agent: str, snapshot: dict):
        """Log a full blackboard state for replay."""
        self.log(agent, "blackboard_snapshot", {"blackboard": snapshot})

    def close(self):
        """Flush and close all file handles."""
        with self._lock:
            self._main_file.close()
            for f in self._agent_files.values():
                f.close()
            self._agent_files.clear()

    @property
    def log_dir(self) -> Path:
        return self._log_dir

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_agent_file(self, agent: str):
        """Get or create per-agent JSONL file. Caller must hold self._lock."""
        if agent not in self._agent_files:
            safe_name = agent.replace("/", "_").replace("\\", "_")
            path = self._log_dir / f"{safe_name}.jsonl"
            self._agent_files[agent] = open(path, "a", encoding="utf-8")
        return self._agent_files[agent]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _now_iso() -> str:
    """ISO timestamp with milliseconds."""
    t = time.time()
    ms = int((t % 1) * 1000)
    base = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t))
    return f"{base}.{ms:03d}"


def _truncate_args(args: dict, max_len: int = 500) -> dict:
    """Truncate long string values in tool args for logging."""
    out = {}
    for k, v in args.items():
        if isinstance(v, str) and len(v) > max_len:
            out[k] = v[:max_len] + f"...[{len(v)} chars]"
        else:
            out[k] = v
    return out
