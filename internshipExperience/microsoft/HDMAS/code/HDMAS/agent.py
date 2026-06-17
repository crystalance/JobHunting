"""
Agent for HDMAS Copilot edition.

Each agent owns an independent CopilotClient (its own CLI process) and
Copilot session. This provides maximum isolation between agents:
  - Separate CLI process per agent
  - Independent context window and compaction
  - No shared state except the filesystem workspace

The Agent class manages:
  - CopilotClient lifecycle (start → create session → send → idle → stop)
  - Vote/wake state machine
  - Event logging
"""

import asyncio
import json
import logging
import time
from typing import Optional, Callable

from copilot import CopilotClient, SubprocessConfig
from copilot.generated.session_events import SessionEvent, SessionEventType
from copilot.session import PermissionHandler

from . import config
from .custom_tools import create_custom_tools
from .prompts import build_system_prompt
from .event_logger import EventLogger

logger = logging.getLogger(__name__)


class Agent:
    """A single autonomous agent backed by its own CopilotClient + session."""

    def __init__(
        self,
        agent_id: str,
        workspace: str,
        copilot_client: CopilotClient,
        lock_manager,
        event_logger: EventLogger,
        query: str,
        agent_count: int,
        vote_callback: Optional[Callable] = None,
        wake_callback: Optional[Callable] = None,
        task_prompt: str = "",
        model: str = None,
        case_start_time: Optional[float] = None,
        total_budget: Optional[float] = None,
        warn_fractions: tuple = (0.70, 0.90),
        attachments: Optional[list] = None,
    ):
        self.agent_id = agent_id
        self.workspace = workspace
        self.copilot_client = copilot_client
        self.lock_manager = lock_manager
        self.event_logger = event_logger
        self.query = query
        self.agent_count = agent_count
        self.task_prompt = task_prompt
        self.model = model or config.MODEL
        # Attachments (e.g. images, PDFs) sent with the first user message
        # of every fresh session. Each item is a Copilot SDK Attachment dict
        # (FileAttachment / BlobAttachment / DirectoryAttachment).
        self.attachments = attachments or None

        # Deadline-warning bookkeeping (case-level: shared across all sessions)
        self.case_start_time = case_start_time if case_start_time is not None else time.time()
        self.total_budget = total_budget
        self.warn_fractions = warn_fractions
        self._warned_t1 = False
        self._warned_t2 = False

        self._vote_callback = vote_callback
        self._wake_callback = wake_callback

        self._stop_event = asyncio.Event()
        self._sleep_event = asyncio.Event()
        self._wake_event = asyncio.Event()
        self._wake_reason: Optional[str] = None
        self._voted_stop = False
        self._tool_call_count = 0

        # Build system prompt
        self._system_prompt = build_system_prompt(
            agent_id, agent_count, query, task_prompt=task_prompt,
        )

        # Create custom tools (coordination only — no web_search)
        self._custom_tools = create_custom_tools(
            agent_id=agent_id,
            lock_manager=lock_manager,
            vote_callback=self._on_vote_stop,
            wake_callback=wake_callback,
            event_logger=event_logger,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def stop(self):
        """Signal the agent to terminate."""
        self._stop_event.set()
        self._wake_event.set()

    def wake(self, reason: str):
        """Wake this agent from vote_stop sleep."""
        self._wake_reason = reason
        self._sleep_event.clear()
        self._voted_stop = False
        self._wake_event.set()

    @property
    def is_sleeping(self) -> bool:
        return self._sleep_event.is_set()

    async def run(self):
        """Main agent loop. Creates a session on the shared CopilotClient."""
        logger.info("[%s] Starting Copilot agent (shared CLI)", self.agent_id)
        self.event_logger.log(self.agent_id, "agent_start", {
            "model": self.model,
        })

        try:
            while not self._stop_event.is_set():
                await self._run_session(self.copilot_client)

                if self._voted_stop and not self._stop_event.is_set():
                    await self._enter_sleep()
                    if self._stop_event.is_set():
                        break
                    continue
                else:
                    break
        except Exception as e:
            logger.error("[%s] Agent error: %s", self.agent_id, e, exc_info=True)
            self.event_logger.log(self.agent_id, "agent_error", {"error": str(e)})
        finally:
            self._cleanup()
            self.event_logger.log(self.agent_id, "agent_done", {
                "reason": "stopped" if self._stop_event.is_set() else "completed",
                "tool_call_count": self._tool_call_count,
            })
            logger.info("[%s] Agent finished", self.agent_id)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _run_session(self, client: CopilotClient):
        """Create a Copilot session on this agent's client, send the query, wait for completion."""
        session_config = {
            "on_permission_request": PermissionHandler.approve_all,
            "model": self.model,
            "tools": self._custom_tools,
            "system_message": {"content": self._system_prompt},
        }

        if config.INFINITE_SESSIONS_ENABLED:
            session_config["infinite_sessions"] = {"enabled": True}

        async with await client.create_session(**session_config) as session:
            done = asyncio.Event()
            self._voted_stop = False

            def on_event(event: SessionEvent):
                etype = event.type
                if etype == SessionEventType.ASSISTANT_MESSAGE:
                    content = getattr(event.data, "content", "") or ""
                    self.event_logger.log(self.agent_id, "assistant_message", {
                        "content_preview": content[:200],
                    })
                elif etype == SessionEventType.SESSION_IDLE:
                    done.set()
                elif etype == SessionEventType.TOOL_EXECUTION_START:
                    self._tool_call_count += 1
                elif etype == SessionEventType.SESSION_ERROR:
                    error_msg = getattr(event.data, "message", "") or ""
                    self.event_logger.log(self.agent_id, "session_error", {
                        "error": error_msg[:500],
                    })

            session.on(on_event)

            # Send the user query (or wake reason for resumed sessions)
            message = self.query
            if self._wake_reason:
                message = (
                    f"[System] You were woken up by another agent. "
                    f"Reason: {self._wake_reason}. "
                    f"Re-read blackboard.json and answer/, then pick work."
                )
                self._wake_reason = None

            if self.attachments:
                await session.send(message, attachments=self.attachments)
            else:
                await session.send(message)

            # Wait for session to go idle or stop signal
            stop_task = asyncio.create_task(self._wait_for_stop())
            done_task = asyncio.create_task(done.wait())
            warner_task = asyncio.create_task(self._deadline_warner(session))

            finished, pending = await asyncio.wait(
                [stop_task, done_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            warner_task.cancel()
            for task in pending:
                task.cancel()

    async def _wait_for_stop(self):
        """Wait until the stop event is set."""
        while not self._stop_event.is_set():
            await asyncio.sleep(0.5)

    async def _deadline_warner(self, session):
        """Inject [USER REMINDER] messages as the case deadline approaches.

        Two one-shot warnings per agent (per whole case, not per session):
          - T1 (default 70% of total_budget): "start wrapping up"
          - T2 (default 90% of total_budget): "stop, dump partial answer, vote_stop"

        If the warner is cancelled (session ended) before a threshold, the flag
        stays unset and the next session will continue waiting from where we are.
        """
        if not self.total_budget or self.total_budget <= 0:
            return
        try:
            t1_frac, t2_frac = self.warn_fractions
            t1_abs = self.case_start_time + self.total_budget * t1_frac
            t2_abs = self.case_start_time + self.total_budget * t2_frac

            async def _wait_until(abs_time: float):
                delay = abs_time - time.time()
                if delay > 0:
                    await asyncio.sleep(delay)

            if not self._warned_t1:
                await _wait_until(t1_abs)
                if self._stop_event.is_set():
                    return
                msg = (
                    f"[USER REMINDER] You have used ~{int(t1_frac * 100)}% of the time budget "
                    f"({int(self.total_budget * t1_frac)}s of {int(self.total_budget)}s). "
                    f"Stop expanding scope. Finish the subtask you are currently on, then in your NEXT "
                    f"Step 1 prefer (c)/(d) over (a) — i.e. compile or fix answer/ rather than claim new "
                    f"unclaimed work. Make sure answer/ contains the best partial answer you can produce "
                    f"from what is already in task_log."
                )
                try:
                    await session.send(msg)
                    self._warned_t1 = True
                    self.event_logger.log(self.agent_id, "deadline_warning_t1", {
                        "elapsed_s": round(time.time() - self.case_start_time, 1),
                        "budget_s": self.total_budget,
                    })
                    logger.info("[%s] T1 deadline reminder sent", self.agent_id)
                except Exception as e:
                    logger.warning("[%s] Failed to send T1 reminder: %s", self.agent_id, e)

            if not self._warned_t2:
                await _wait_until(t2_abs)
                if self._stop_event.is_set():
                    return
                msg = (
                    f"[USER REMINDER — URGENT] {int(t2_frac * 100)}% of the time budget is gone. "
                    f"Do NOT start any new web search, file fetch, or new subtask. Immediately consolidate "
                    f"everything you currently have into answer/final.md (lock answer/final.md → write → unlock), "
                    f"then call vote_stop. The orchestrator will hard-kill the run shortly. A partial answer "
                    f"saved now is worth far more than a complete answer that never gets written."
                )
                try:
                    await session.send(msg)
                    self._warned_t2 = True
                    self.event_logger.log(self.agent_id, "deadline_warning_t2", {
                        "elapsed_s": round(time.time() - self.case_start_time, 1),
                        "budget_s": self.total_budget,
                    })
                    logger.info("[%s] T2 deadline reminder sent", self.agent_id)
                except Exception as e:
                    logger.warning("[%s] Failed to send T2 reminder: %s", self.agent_id, e)
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.warning("[%s] Deadline warner crashed: %s", self.agent_id, e)

    async def _enter_sleep(self):
        """Enter sleep mode after vote_stop."""
        self._sleep_event.set()
        self._wake_event.clear()
        self.event_logger.log(self.agent_id, "agent_sleep", {})
        logger.info("[%s] Sleeping (voted stop)", self.agent_id)

        # Wait for wake or stop
        while not self._stop_event.is_set() and not self._wake_event.is_set():
            await asyncio.sleep(0.5)

        if self._wake_event.is_set() and not self._stop_event.is_set():
            self._sleep_event.clear()
            self._wake_event.clear()
            self.event_logger.log(self.agent_id, "agent_wake", {
                "reason": self._wake_reason,
            })
            logger.info("[%s] Woken: %s", self.agent_id, self._wake_reason)

    def _on_vote_stop(self, agent_id: str, reason: str):
        """Callback when this agent calls vote_stop tool."""
        self._voted_stop = True
        if self._vote_callback:
            self._vote_callback(agent_id, reason)

    def _cleanup(self):
        """Release all held locks."""
        try:
            self.lock_manager.release_all(self.agent_id)
        except Exception:
            pass
