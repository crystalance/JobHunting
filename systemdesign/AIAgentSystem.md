# Agent system (index)

Full interview write-ups: [`agent_runtime.md`](./agent_runtime.md) (HITL / MCP / sandbox / memory), [`enterprise_agent_tasks.md`](./enterprise_agent_tasks.md) (long-running jobs), [`engineering_knowledge_base.html`](./engineering_knowledge_base.html) (RAG over code).

## Core (knowledge for agents)

How to process large-scale information in a limited context window: for one task the agent does not need the whole codebase, only what that task touches. That is the knowledge base. Hard part: a lot of the knowledge lives in people’s heads (one trace spans dozens of services) and is not in the repo.

## MCP / sandbox / HITL / memory

See `agent_runtime.md`. Short map:

| Topic | One line | Your system |
|---|---|---|
| **HITL** | Pause the loop; human does gated work; resume on new env state | BrowserUse noVNC login; same pattern for deploy/send |
| **MCP** | Host JSON-RPC to tool servers; model only sees function schemas | Same dispatch as `execute_python`; A2A is agent↔agent |
| **Sandbox** | Untrusted code in kernel/container; stdout only | IPython per `session_id`; CDP JS; FC container |
| **Memory** | Window + files + traces + RAG; not one Redis | Kernel/WORKSPACE, Langfuse, HDMAS blackboard, KB |
