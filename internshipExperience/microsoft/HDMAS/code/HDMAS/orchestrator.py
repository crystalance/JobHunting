"""
Orchestrator for HDMAS Copilot edition.

Same responsibilities as HDMAS v4:
  - Create workspace directory structure
  - Initialize blackboard.json
  - Spawn N agent tasks (async)
  - Manage vote_stop / wake_agent state machine
  - Detect termination and collect results
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from copilot import CopilotClient, SubprocessConfig

from . import config
from .agent import Agent
from .lock_manager import LockManager
from .event_logger import EventLogger

logger = logging.getLogger(__name__)


class Orchestrator:
    """Top-level async runtime that manages workspace, agents, and termination.
    
    Owns a single CopilotClient (one CLI process). Each agent creates its
    own session on this shared client.
    """

    def __init__(
        self,
        query: str,
        n_agents: int = None,
        workspace: str = None,
        log_dir: str = None,
        model: str = None,
        timeout: float = 1800.0,
        task_prompt: str = "",
        attachments: Optional[list] = None,
    ):
        self.query = query
        self.n_agents = n_agents or config.N_AGENTS
        self.model = model or config.MODEL
        self.timeout = timeout
        self.task_prompt = task_prompt
        # Attachments shared by all agents (e.g. an image referenced by the query).
        # Each item is a Copilot SDK Attachment dict.
        self.attachments = attachments or None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.workspace = workspace or os.path.join("workspaces", f"ws_{timestamp}")
        self.log_dir = log_dir or os.path.join(self.workspace, "logs")

        self._agents: dict[str, Agent] = {}
        self._agent_tasks: dict[str, asyncio.Task] = {}
        self._lock_manager: Optional[LockManager] = None
        self._event_logger: Optional[EventLogger] = None
        self._copilot_client: Optional[CopilotClient] = None
        self._woke_for_output = False

    async def run(self) -> dict:
        """Execute the full pipeline. Returns a result dict."""
        t_start = time.time()

        # 1. Setup
        self._setup_workspace()
        self._lock_manager = LockManager(self.workspace)
        self._event_logger = EventLogger(self.log_dir)
        self._event_logger.log("orchestrator", "orchestrator_start", {
            "query": self.query,
            "n_agents": self.n_agents,
            "model": self.model,
            "workspace": self.workspace,
        })

        # 2. Initialize blackboard
        self._init_blackboard()

        # 3. Start single shared CopilotClient (one CLI process)
        self._copilot_client = CopilotClient(
            SubprocessConfig(cwd=self.workspace),
            auto_start=True,
        )
        await self._copilot_client.start()

        try:
            # 4. Spawn agents (each creates a session on the shared client)
            await self._spawn_agents()

            # 5. Monitor loop
            await self._monitor_loop()
        finally:
            # 6. Cleanup
            await self._copilot_client.stop()

        elapsed = round(time.time() - t_start, 2)
        result = self._collect_results(elapsed)

        self._event_logger.log("orchestrator", "orchestrator_done", {
            "elapsed_s": elapsed,
        })
        self._event_logger.close()

        return result

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_workspace(self):
        ws = Path(self.workspace)
        ws.mkdir(parents=True, exist_ok=True)
        (ws / "answer").mkdir(exist_ok=True)
        for i in range(self.n_agents):
            (ws / "agents" / f"agent_{i}").mkdir(parents=True, exist_ok=True)
        logger.info("Workspace created: %s", self.workspace)

    def _init_blackboard(self):
        bb = {
            "query": self.query,
            "task_log": [],
            "agents": {
                f"agent_{i}": {"status": "active"}
                for i in range(self.n_agents)
            },
        }
        bb_path = Path(self.workspace) / "blackboard.json"
        bb_path.write_text(json.dumps(bb, indent=2, ensure_ascii=False), encoding="utf-8")
        self._event_logger.log_blackboard_snapshot("orchestrator", bb)

    # ------------------------------------------------------------------
    # Agent management
    # ------------------------------------------------------------------

    async def _spawn_agents(self):
        case_start_time = time.time()
        for i in range(self.n_agents):
            agent_id = f"agent_{i}"
            agent = Agent(
                agent_id=agent_id,
                workspace=self.workspace,
                copilot_client=self._copilot_client,
                lock_manager=self._lock_manager,
                event_logger=self._event_logger,
                query=self.query,
                agent_count=self.n_agents,
                vote_callback=self._handle_vote,
                wake_callback=self._handle_wake,
                task_prompt=self.task_prompt,
                model=self.model,
                case_start_time=case_start_time,
                total_budget=self.timeout,
                attachments=self.attachments,
            )
            self._agents[agent_id] = agent
            task = asyncio.create_task(self._run_agent(agent), name=agent_id)
            self._agent_tasks[agent_id] = task

    async def _run_agent(self, agent: Agent):
        try:
            await agent.run()
        except Exception as e:
            logger.error("Agent %s crashed: %s", agent.agent_id, e, exc_info=True)
            self._event_logger.log(agent.agent_id, "agent_crash", {"error": str(e)})

    # ------------------------------------------------------------------
    # Monitor loop
    # ------------------------------------------------------------------

    async def _monitor_loop(self):
        t_start = time.time()

        while True:
            await asyncio.sleep(2.0)

            elapsed = time.time() - t_start

            # Hard timeout
            if elapsed > self.timeout:
                logger.warning("Hard timeout (%.0fs). Stopping all agents.", elapsed)
                self._event_logger.log("orchestrator", "hard_timeout", {"elapsed_s": elapsed})
                for agent in self._agents.values():
                    agent.stop()
                # Wait a bit for agents to stop
                await asyncio.sleep(2.0)
                break

            # Check if all tasks are done
            all_done = all(t.done() for t in self._agent_tasks.values())
            if all_done:
                logger.info("All agents finished.")
                break

            # Check if all agents are either sleeping or finished
            # (not just "all sleeping" — some may have exited their run() naturally)
            all_inactive = all(
                a.is_sleeping or self._agent_tasks[aid].done()
                for aid, a in self._agents.items()
            )

            if all_inactive:
                answer_dir = Path(self.workspace) / "answer"
                has_answer = any(answer_dir.iterdir()) if answer_dir.exists() else False

                if not has_answer and not self._woke_for_output:
                    # Wake a sleeping agent to compile answer
                    self._woke_for_output = True
                    for aid, a in self._agents.items():
                        if a.is_sleeping:
                            a.wake("All agents inactive but answer/ is empty. Please compile the final answer.")
                            self._event_logger.log("orchestrator", "wake_for_output", {
                                "target": aid,
                            })
                            break
                elif has_answer:
                    # Answer exists, all inactive → terminate
                    logger.info("All agents inactive, answer exists. Terminating.")
                    for agent in self._agents.values():
                        agent.stop()
                    await asyncio.sleep(1.0)
                    break
                else:
                    # No sleeping agents to wake and no answer → nothing more we can do
                    logger.warning("All agents inactive, no answer, no one to wake. Terminating.")
                    for agent in self._agents.values():
                        agent.stop()
                    await asyncio.sleep(1.0)
                    break

    # ------------------------------------------------------------------
    # Vote / Wake callbacks
    # ------------------------------------------------------------------

    def _handle_vote(self, agent_id: str, reason: str):
        self._event_logger.log(agent_id, "vote_stop", {"reason": reason})
        self._update_bb_status(agent_id, "sleeping")

    def _handle_wake(self, caller_id: str, target_id: str, reason: str) -> dict:
        target = self._agents.get(target_id)
        if not target:
            return {"error": f"Agent {target_id} not found"}
        if not target.is_sleeping:
            return {"error": f"Agent {target_id} is not sleeping"}

        target.wake(reason)
        self._update_bb_status(target_id, "active")
        self._event_logger.log(caller_id, "wake_agent", {
            "target": target_id,
            "reason": reason,
        })
        return {"status": "woken", "agent_id": target_id}

    def _update_bb_status(self, agent_id: str, status: str):
        try:
            bb_path = Path(self.workspace) / "blackboard.json"
            result = self._lock_manager.acquire("blackboard.json", "orchestrator", timeout=5)
            if result.get("status") != "locked":
                return
            try:
                bb = json.loads(bb_path.read_text(encoding="utf-8"))
                bb.setdefault("agents", {})[agent_id] = {"status": status}
                bb_path.write_text(json.dumps(bb, indent=2, ensure_ascii=False), encoding="utf-8")
            except (json.JSONDecodeError, Exception) as e:
                logger.warning("BB corrupted, skipping status update: %s", e)
            finally:
                self._lock_manager.release("blackboard.json", "orchestrator")
        except Exception as e:
            logger.warning("BB status update failed: %s", e)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def _collect_results(self, elapsed_s: float) -> dict:
        answer_dir = Path(self.workspace) / "answer"
        answer_files = {}
        if answer_dir.exists():
            for f in answer_dir.rglob("*"):
                if f.is_file():
                    try:
                        rel = str(f.relative_to(Path(self.workspace))).replace("\\", "/")
                        answer_files[rel] = f.read_text(encoding="utf-8")
                    except Exception:
                        pass

        bb_path = Path(self.workspace) / "blackboard.json"
        blackboard = {}
        try:
            blackboard = json.loads(bb_path.read_text(encoding="utf-8"))
        except Exception:
            pass

        return {
            "workspace": self.workspace,
            "log_dir": self.log_dir,
            "elapsed_s": elapsed_s,
            "n_agents": self.n_agents,
            "blackboard": blackboard,
            "answer_files": answer_files,
        }
