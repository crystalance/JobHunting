# A2A Adapter — Spoken Answers (AgentScope Runtime)

> Grounded in `agentscope_runtime/engine/deployers/adapter/a2a/`
> (`a2a_protocol_adapter.py`, `a2a_agent_adapter.py`, `a2a_adapter_utils.py`).
> 60–90s each. Pause instead of "uh". Volunteer the v1 gap before they find it.

---

## 30s opener — what it is and why it exists

> "A2A is Google's Agent-to-Agent protocol: a standard way for one agent runtime to call another without sharing a framework. LangGraph, AutoGen, AgentScope — they all have different request objects. The adapter is a **protocol boundary**. Outside, you speak A2A over JSON-RPC. Inside, you speak AgentScope's `AgentRequest` / event stream. I built the bidirectional translation and mounted it on FastAPI so a Runtime-deployed agent — including on Function Compute — can be discovered and invoked by any A2A client. Discovery is a well-known Agent Card; the call path is `POST /a2a`."

---

## Q1 — "Walk me through a request end to end"

> "Three hops: discover, translate in, run, translate out.
>
> First, the client `GET`s `/.well-known/agent-card.json`. That card is what I generate in the adapter — name, URL, skills, and capabilities. The URL points at our JSON-RPC path, `/a2a`. Preferred transport is JSON-RPC.
>
> Second, the client `POST`s a JSON-RPC body: method, params — the A2A `Message` with parts — and a request `id`. FastAPI hands it to the A2A request handler. The handler builds a `RequestContext`. My `A2AExecutor` pulls the user text, maps `context_id` to our `session_id` and `task_id` to `response_id`, and builds an `AgentRequest` with `stream=True` so the Runtime still runs as an async generator.
>
> Third, I `async for` events from the Runtime function. When the run hits `Completed`, I take the last output message, convert AgentScope content — text, image, data — into A2A `Part`s, and enqueue that as an A2A `Message` on the event queue. The handler serializes it back as a JSON-RPC **result** for that same request `id`.
>
> So the Runtime never sees A2A types, and the client never sees `AgentRequest`. The adapter is the only place those schemas meet. Task state lives in an in-memory task store keyed by `task_id` for the life of that process."

**If they ask you to draw it:**

```
A2A client
  GET  /.well-known/agent-card.json
  POST /a2a   { jsonrpc, method, params: Message, id }
        │
        ▼
  A2AFastAPIApplication + DefaultRequestHandler
        │  RequestContext (context_id, task_id, user input)
        ▼
  A2AExecutor
        │  AgentRequest(session_id, response_id, stream=True)
        ▼
  Runtime agent  ──async events──►  filter Completed
        │
        ▼
  agent_message_to_a2a_message  →  EventQueue  →  JSON-RPC result
```

---

## Q2 — "Why JSON-RPC? Why not REST?"

> "Because A2A **specified** JSON-RPC as the default transport, and I wanted any standard client to work without a custom REST dialect.
>
> Three properties that fit agents better than `POST /v1/chat`.
>
> First, **one URL, many methods**. Discover, send, get-task, cancel — they all hit `/a2a`. The `method` field is the verb. I don't version a tree of paths every time the spec adds `tasks/cancel`.
>
> Second, **correlation**. Every call has a JSON-RPC `id`. The result or error comes back with the same id. That's how you tell a retry from a new task, and how a gateway multiplexes several in-flight calls on one connection.
>
> Third, **the envelope doesn't change when you add streaming**. Params stay `Message` + `task_id`. You switch the method — send versus send-subscribe — and the server may reply with SSE of the same result types. REST usually invents a second resource and a second schema.
>
> REST is nicer for CRUD. This is an **RPC to a long-running task**, so method-plus-id-plus-error-object is the right shape. We advertise `preferred_transport: JSONRPC` on the Agent Card so clients don't have to guess."

---

## Q3 — "How does streaming work?"

Be precise — **internal stream ≠ A2A wire stream**.

> "There are two streams, and v1 only closes one of them.
>
> **Inside** the Runtime, the agent is already a generator. I always construct `AgentRequest` with `stream=True` and `async for` every event — deltas, in-progress, completed. That keeps Time-to-first-token cheap **inside** our process and matches how FC/FastAPI already run agents.
>
> **On the A2A wire**, the Agent Card I publish sets `capabilities.streaming=false`. I only `enqueue` when status is `Completed`, and I send the **last** output message. So an A2A client sees a request-response JSON-RPC call, not token-by-token SSE. The conversion helpers for `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent` — append, last_chunk — are already in `a2a_adapter_utils`; they are the mapping I'd use for `message/stream` or `tasks/sendSubscribe`.
>
> Why ship that first? Interop first: a LangGraph caller can invoke us without implementing SSE. The honest cost is latency-to-first-token on the A2A side equals the full run. The next increment is flip the card to streaming true, enqueue artifact-update events as deltas arrive, and mark `final` on completed or failed. Until then I refuse to advertise a capability the wire doesn't implement — the runtime **overrides** user-supplied capability flags for that reason."

---

## Q4 — "Partial failure? What about retries?"

> "I separate three failures, because they need different answers.
>
> **1. Agent throws mid-run.** The executor wraps the generator in try/except, logs the traceback, and does **not** enqueue a completed message. The client should see a JSON-RPC **error** or a task in `failed` — not a half-success. What I would tighten: map that exception to `TaskState.failed` via the status-update helper we already wrote, instead of only logging. Silent swallow is the bug I'd name myself.
>
> **2. Cancel.** `cancel()` raises `UnsupportedOperationError`. That's honest: we don't have cooperative cancellation through the Runtime loop yet. A client that sends `tasks/cancel` gets a protocol error, not a fake canceled task. Next step is a cancellation token on `AgentRequest` and mapping `Canceled` to A2A `canceled`.
>
> **3. Retry / double submit.** JSON-RPC `id` plus A2A `task_id` — which I store as `response_id` — are the idempotency keys. A client should retry the **same** task id. The task store is **in-memory**, so if the FC instance dies, that store is gone — the retry looks like a new run. That's acceptable for a stateless custom runtime if the agent itself is idempotent; it's not acceptable if 'send the email' already happened. At platform scale I'd persist tasks — Redis or the same metadata DB as deploy — and return the stored result when `task_id` is seen again. I would **not** retry on the server just because the client disconnected; generation is not safe to double.
>
> **Partial output:** because I only emit on `Completed`, a crash does not publish a truncated A2A artifact. The user sees failure, not a lie. That's the conservative choice until we stream artifacts with `last_chunk=false`.
>
> Registry register failing is the one failure I **do** swallow: Nacos down must not block process start. We log and serve; discovery is degraded, the JSON-RPC endpoint still works if the client already has the URL."

---

## Q5 — "What's hard about bidirectional translation?"

> "The hard part is not field rename — it's **unequal type systems** and **who owns identity**.
>
> A2A messages are `Part`s: text, file, data. AgentScope is `Content`: text, image, data. File-to-image is a lossy guess — I map `FilePart.uri` to `ImageContent`. Unknown parts raise; I don't silently drop, because a dropped tool payload is a silent correctness bug.
>
> Roles: we say `assistant`, A2A says `agent`. Status: our `Delta` / `InProgress` both become A2A `working`; `Completed` / `Failed` / `Canceled` have 1:1 maps. Get that wrong and a client spins forever waiting for `completed`.
>
> Identity: A2A `context_id` is the conversation; `task_id` is this run. I map those to `session_id` and `response_id`. If I swapped them, retries would fork sessions. Streaming flags disagree on purpose: we stream internally, we don't claim A2A streaming until the wire does.
>
> So bidirectional means two functions per object — message, part, task, status event — and a rule: **never invent a field the other side will treat as authority.** Missing optional fields stay None. User-supplied Agent Card capabilities are ignored so we can't advertise streaming we don't implement."

---

## Q6 — "How does this sit on FC / one-click deploy?"

> "The adapter is just more FastAPI routes on the same app the deployer packages. After wheel-plus-zip lands on FC, the process listens on 8090; `/a2a` and the well-known card are in that process. Session affinity — `x-agentscope-runtime-session-id` — still matters, because the A2A task store is in memory. Two POSTs for the same `context_id` hitting two instances do not share task state. That's the same stateless-chat lesson: either pin the session or externalize the task store. Discoverability is optional Nacos; the card URL is host-plus-`/a2a` from the runtime config."

---

## Numbers / constants to have ready

| Item | Value |
|---|---|
| JSON-RPC path | `/a2a` |
| Agent Card | well-known agent-card path (A2A default) |
| Transport | `JSONRPC` |
| Task timeout / event timeout | 60s / 10s (config defaults) |
| Card capabilities (v1) | `streaming=false`, no push, no state-transition history |
| Task store | `InMemoryTaskStore` |
| Cancel | unsupported (explicit error) |
| I/O modes default | `["text"]` |

---

## Delivery notes

- Lead with **boundary**, not "I wrote a converter." Interviewers score request-flow and failure modes.
- On streaming, say **"two layers"** in the first sentence so you don't get trapped advertising SSE you don't ship.
- Partial-failure closer: "I fail closed on the wire — no completed event if the run dies — and I'd persist `task_id` before I add server-side retries."
- Tie to ChatGPT/Redis-stream SD if they just asked that: "A2A task store is the in-memory version of that run log; same bug if two FC instances own one `context_id`."
