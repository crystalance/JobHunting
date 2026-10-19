# AgentScope source for the Alibaba interview

Two shallow clones of `main`, taken 2026-10-18. The clones are gitignored so they stay local.

| Checkout | Commit | Remote |
|---|---|---|
| `agentscope/` | `976e2ff` | https://github.com/agentscope-ai/agentscope |
| `agentscope-runtime/` | `22072fd` | https://github.com/agentscope-ai/agentscope-runtime |

The internship was on **Runtime**, not on the framework loop. The spoken answers in `internshipExperience/AlibabaCloud/a2a_adapter_spoken.md` still match the adapter directory. `main` has moved since the internship, so treat class names below as this checkout, and re-read a function before quoting a line in an interview.

## Read this first: the A2A adapter

All under `agentscope-runtime/src/agentscope_runtime/engine/deployers/adapter/a2a/`.

| File | What it is | What you say in the interview |
|---|---|---|
| `a2a_protocol_adapter.py` | `A2AFastAPIDefaultAdapter`. Mounts the A2A routes on the existing FastAPI app and builds the Agent Card. `get_agent_card` sets `streaming=False`. | The adapter is a plugin, not a second service. The card must not advertise streaming the wire does not serve. |
| `a2a_agent_adapter.py` | `A2AExecutor.execute` / `cancel`. Maps `context.context_id` → `session_id` and `context.task_id` → `response_id`. `cancel` raises `UnsupportedOperationError`. | Identity mapping. Cancel is an honest protocol error, not a fake canceled task. |
| `a2a_adapter_utils.py` | Both directions: `a2a_message_to_agent_message`, `agent_message_to_a2a_message`, `a2a_part_to_agent_content`, `runstatus_to_a2a_taskstate`, plus the status-update and artifact-update helpers. | Parts ↔ Content, run status ↔ TaskState. Unknown parts raise. Only a completed run is published. |
| `a2a_registry.py` | `A2ARegistry` interface. | Discovery is optional. The JSON-RPC endpoint still works if the client already has the URL. |
| `nacos_a2a_registry.py` | `NacosRegistry`. | Nacos down must not block process start. |

Tests that lock the behavior: `agentscope-runtime/tests/unit/test_a2a_protocol_adapter.py`, `test_a2a_registry.py`, `test_nacos_a2a_registry.py`, and `tests/deploy/test_local_deployer_a2a.py`.

Call path, same as the spoken note:

```text
GET  /.well-known/agent-card.json     a2a_protocol_adapter.get_agent_card
POST /a2a                             A2A JSON-RPC
        A2AExecutor.execute           a2a_agent_adapter.py
        AgentRequest(session_id, response_id, stream=True)
        async for events              only enqueue on Completed
        agent_message_to_a2a_message  a2a_adapter_utils.py
        JSON-RPC result for the same request id
```

## Deploy path (the other half of the internship)

| File | Why it matters |
|---|---|
| `agentscope-runtime/src/agentscope_runtime/engine/deployers/local_deployer.py` | How the adapter is mounted on the local app. Start here before Function Compute. |
| `agentscope-runtime/src/agentscope_runtime/engine/deployers/fc_deployer.py` | Function Compute packaging and deploy. One process serves `/a2a` after the zip lands. |
| `agentscope-runtime/src/agentscope_runtime/engine/deployers/cli_fc_deploy.py` | The CLI in front of that deployer. |
| `agentscope-runtime/src/agentscope_runtime/engine/deployers/base.py` | Shared deployer contract. |
| `agentscope-runtime/src/agentscope_runtime/engine/runner.py` | Runtime owns the agent lifecycle and the event stream the executor consumes. |
| `agentscope-runtime/src/agentscope_runtime/engine/schemas/session.py` | Session identity. Pair with the `session_id` / `response_id` mapping above. |

Bailian platform stories (OSS bucket ownership, least-privilege RAM, the management console) are **not** in these repos. Those lived in the internal platform. The open-source half is this deployer plus the adapter.

## Framework loop, if they ask what AgentScope itself is

Current `main` folded the old `ReActAgent` into one class. The loop is still reasoning then acting.

| File | What to read |
|---|---|
| `agentscope/src/agentscope/agent/_agent.py` | `Agent.reply` (line 332), `observe` (381), `_reasoning` (1641), `_acting` (2714). This is the ReAct loop. |
| `agentscope/src/agentscope/agent/_a2a_agent.py` | Framework-side A2A agent. This is a client/peer, not the Runtime adapter you shipped. Do not mix the two in an answer. |
| `agentscope/src/agentscope/pipeline/` | Multi-agent pipelines (`_team_pipeline.py`, `_goal_pipeline.py`). |
| `agentscope/examples/a2a/` | Small examples. Use them after the Runtime adapter, not instead of it. |

## Asyncio, because the adapter is an async generator

`asyncio.md` walks `execute` → `stream_query` → `_call_model` and separates the three parks: a coroutine on the heap (`await` / `yield`), the one server thread inside `kevent` or `epoll_wait`, and a real child process from `subprocess.Popen`. The Java column is virtual threads and Netty versus platform threads versus `ProcessBuilder`. The state diagram and the loop flowchart are in “One coroutine, as a graph,” with the Python docs link.

## Suggested pass

1. `a2a_agent_adapter.py` `execute` and `cancel` — one sitting.
2. `a2a_adapter_utils.py` `runstatus_to_a2a_taskstate` and the two message converters.
3. `a2a_protocol_adapter.py` `get_agent_card` and `add_endpoint`.
4. `runner.py` only far enough to see where the async event stream comes from.
5. `fc_deployer.py` only far enough to see that `/a2a` is routes on the packaged app.
6. `_agent.py` `_reasoning` / `_acting` if the question is the framework, not the adapter.
