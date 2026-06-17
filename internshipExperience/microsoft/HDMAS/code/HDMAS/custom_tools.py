"""
Custom tool definitions for HDMAS Copilot edition.

These tools are registered with each Copilot session. Built-in Copilot tools
handle file I/O and shell/Python execution. We define custom tools for:
  - web_search: Bing Grounding + LLM summarization
  - lock_file / unlock_file: advisory blackboard locks
  - vote_stop: agent sleep signal
  - wake_agent: wake a sleeping agent
"""

import json
import logging
from typing import Optional

from pydantic import BaseModel, Field
from copilot import define_tool
from copilot.tools import Tool, ToolInvocation, ToolResult

logger = logging.getLogger(__name__)


# ======================================================================
#  Pydantic models for tool parameters
# ======================================================================

class WebSearchParams(BaseModel):
    query: str = Field(description="Search query")


class LockFileParams(BaseModel):
    path: str = Field(description="File path to lock (relative to workspace)")


class UnlockFileParams(BaseModel):
    path: str = Field(description="File path to unlock (relative to workspace)")


class VoteStopParams(BaseModel):
    reason: str = Field(description="Why you believe the task is complete")


class WakeAgentParams(BaseModel):
    agent_id: str = Field(description="The agent to wake (e.g. 'agent_0')")
    reason: str = Field(description="Why this agent needs to wake up")


# ======================================================================
#  Tool factory — creates tool instances bound to runtime context
# ======================================================================

def create_custom_tools(
    agent_id: str,
    lock_manager,
    vote_callback=None,
    wake_callback=None,
    event_logger=None,
) -> list[Tool]:
    """Create tool instances for one agent session.

    Returns a list of copilot.tools.Tool objects ready to pass to
    create_session(tools=[...]). Web search is handled by Copilot's
    built-in tools — we only register HDMAS coordination tools here.
    """

    # ---- lock_file ----
    async def _lock_file(invocation: ToolInvocation) -> ToolResult:
        path = invocation.arguments.get("path", "")
        if event_logger:
            event_logger.log_tool_call(agent_id, 0, "lock_file", {"path": path})
        result = lock_manager.acquire(path, agent_id)
        return ToolResult(text_result_for_llm=json.dumps(result), result_type="success")

    # ---- unlock_file ----
    async def _unlock_file(invocation: ToolInvocation) -> ToolResult:
        path = invocation.arguments.get("path", "")
        if event_logger:
            event_logger.log_tool_call(agent_id, 0, "unlock_file", {"path": path})
        result = lock_manager.release(path, agent_id)
        return ToolResult(text_result_for_llm=json.dumps(result), result_type="success")

    # ---- vote_stop ----
    async def _vote_stop(invocation: ToolInvocation) -> ToolResult:
        reason = invocation.arguments.get("reason", "")
        if event_logger:
            event_logger.log(agent_id, "vote_stop", {"reason": reason})
        if vote_callback:
            vote_callback(agent_id, reason)
        return ToolResult(
            text_result_for_llm=json.dumps({"status": "voted_stop", "agent": agent_id, "reason": reason}),
            result_type="success",
        )

    # ---- wake_agent ----
    async def _wake_agent(invocation: ToolInvocation) -> ToolResult:
        target = invocation.arguments.get("agent_id", "")
        reason = invocation.arguments.get("reason", "")
        if event_logger:
            event_logger.log(agent_id, "wake_agent", {"target": target, "reason": reason})
        if wake_callback:
            result = wake_callback(agent_id, target, reason)
            return ToolResult(text_result_for_llm=json.dumps(result), result_type="success")
        return ToolResult(text_result_for_llm='{"error": "wake_agent not available"}', result_type="success")

    # ---- Build tool list ----
    tools = [
        Tool(
            name="lock_file",
            description=(
                "Acquire an exclusive advisory lock on a file. "
                "Required before modifying blackboard.json or answer/ files."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to lock"},
                },
                "required": ["path"],
            },
            handler=_lock_file,
            skip_permission=True,
        ),
        Tool(
            name="unlock_file",
            description="Release an advisory lock you previously acquired on a file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to unlock"},
                },
                "required": ["path"],
            },
            handler=_unlock_file,
            skip_permission=True,
        ),
        Tool(
            name="vote_stop",
            description=(
                "Vote to stop the task and enter sleep mode. "
                "BEFORE calling this, verify blackboard.json tasks are complete "
                "and answer/ is non-empty."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Why the task is complete"},
                },
                "required": ["reason"],
            },
            handler=_vote_stop,
            skip_permission=True,
        ),
        Tool(
            name="wake_agent",
            description="Wake a sleeping agent when you discover unfinished work.",
            parameters={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent to wake (e.g. 'agent_0')"},
                    "reason": {"type": "string", "description": "Why waking"},
                },
                "required": ["agent_id", "reason"],
            },
            handler=_wake_agent,
            skip_permission=True,
        ),
    ]

    return tools
