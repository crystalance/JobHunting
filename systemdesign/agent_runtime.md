# Agent runtime: HITL, MCP, sandbox, memory

> Interview chunks (~20 min each). Tie every box to **your** systems: BrowserUse noVNC handoff, Microsoft `execute_python` kernel, HDMAS blackboard, Alibaba A2A/FC.
>
> Pattern: the model only **emits text**. Tools, humans, files, and retrieval are **outside** the weights. The harness is the product.

---

## 1. Human-in-the-loop (HITL)

HITL is not “the user chats with the bot.” It is: **the agent loop pauses on a gated action, a human does something the model must not (or cannot) do, then the loop resumes with new environment state.**

Same skeleton as long-running tasks: persist a run, do not hold HTTP, **status = `AWAIT_HUMAN`**, resume is another event.

### Why you need it

| Gate | Example | If you skip HITL |
|---|---|---|
| **Secret the model must never see** | Password, 2FA, bank OTP | Prompt injection / logs leak credentials |
| **Irreversible / spend** | Deploy to prod, send email, pay | Double-click deploy; last-writer-wins on FC |
| **Policy** | Delete data, scrape behind login | Legal / ToS |
| **Capability** | CAPTCHA, “are you human” | Agent cannot complete |

BrowserUse is the first row. Alibaba deploy *should* be the second (you did not lock `agent_id` in v1 — say that). Coding agents merging to `main` is the same gate.

### Your project: BrowserUse login handoff

Naive agent: Playwright types the password. That fails 2FA, dumps secrets into traces, and breaks when the site fingerprints bots.

What you built (resume + `CICDdivedeep.md`):

- Headful Chromium on **Xvfb `:99`** + fluxbox — the **same** browser the agent drives.
- **noVNC** streams that display; Telegram sends a **one-tap URL**.
- Human logs in **in the agent’s browser**. Cookies land in a **persistent Chromium profile** (gitignored; survives deploys).
- Agent resumes on an already-authenticated session.

```text
Telegram "do X on site Y"
        │
        v
  Runner starts task, browser on :99
        │
        │  needs login? (cookie miss / 401 / login URL)
        v
  state = AWAIT_HUMAN
  send noVNC link  ──►  user opens phone/laptop, types password + 2FA
  poll / webhook: "done" or session cookie present
        │
        v
  state = RUNNING
  CodeAct JS / browser-use actions on the live DOM
        │
        v
  DONE  (Langfuse trace: steps, tokens, cost)
```

**State machine** (this is what you’d unit-test — you already named `core.handoff`):

```text
IDLE → RUNNING ⇄ AWAIT_HUMAN → RUNNING → SUCCEEDED | FAILED | CANCELLED
```

Resume condition (pick one, say it): user taps **Continue**; or runner sees **non-login URL + cookie jar**; or timeout → `FAILED`.

**Why noVNC, not a screenshot to Telegram:** login is multi-step (password, SMS, passkey). Screenshots are observation-only. noVNC is **input into the same process** that owns CDP. CDP screenshot is fine for *showing* a step; it is the wrong channel for *typing a password*.

**What is *not* HITL:** the agent asking “should I click submit?” on every step. That is a slow human. Gate **only** secrets and irreversible writes.

### Generic HITL (if they don’t care about the browser)

Same as `enterprise_agent_tasks.md`:

1. Tool layer: `if tool.requires_approval: do not execute`.
2. Write `approval_request` (run_id, tool, args digest — **not** raw password).
3. Push Slack/Lark/Telegram.
4. Human approve / deny / edit args.
5. Worker wakes, executes **once**, audit log.

Do not put the approval bit only in the prompt. The **tool sandbox** refuses until the row says `approved`.

Spoken (~40s):

> HITL is a pause in the agent loop, not a chat. In BrowserUse the gated action is login: the agent cannot hold the password. I pause the run, stream the agent’s own Xvfb browser over noVNC, the user authenticates, cookies stay in a persistent profile, then the loop continues. High-risk tools — deploy, send, delete — should be the same state: `AWAIT_HUMAN`, then the tool host executes. v1 of Bailian deploy did *not* serialize clicks; that’s the gap I’d close with a lease.

---

## 2. MCP — how it is actually implemented

**MCP (Model Context Protocol)** is a **tool/resource bus** between a **host** (Cursor, Claude Desktop, *your* agent runtime) and **servers** (GitHub, filesystem, Slack). It is **not** the LLM. It is **not** A2A (A2A is agent-to-agent; MCP is agent-to-tools).

You already built the cousin: **A2A adapter** = JSON-RPC in front of AgentScope. MCP is JSON-RPC in front of **tools**.

### Roles

| Piece | Job |
|---|---|
| **Host** | Owns the agent loop, UI, permissions, which servers to spawn |
| **MCP client** (in the host) | JSON-RPC session to one server |
| **MCP server** | Process that exposes `tools`, `resources`, `prompts` |
| **LLM** | Sees **host-translated** function schemas; never speaks MCP on the wire |

### Wire (stdio is the default)

```text
Host  --stdin/stdout JSON-RPC-->  Server process
      (or Streamable HTTP / SSE for remote)
```

Handshake:

```text
1. Host spawns 　
2. initialize { protocolVersion, capabilities, clientInfo }
3. initialized ack
4. tools/list  →  [{ name, description, inputSchema }]
5. Host maps each tool → OpenAI/Hermes `tools` array in the next chat completion
```

### Call path (one tool round)

```text
Model emits tool_call: github.create_issue({ title })
        │
        v
Host policy: allowed? HITL?  ── deny → tool result = error string
        │
        v
MCP client:  tools/call { name, arguments }
        │
        v
Server: does the GitHub HTTP, returns content[] (text / json)
        │
        v
Host appends role=tool to messages, next LLM turn
```

That is the **same five stages** as your Microsoft harness (`tool_call_flow.md`): schema in the prompt → model text → parser → **host executes** → tool message. MCP only replaces “hard-coded `execute_python`” with “any server that speaks `tools/call`.”

### What the server must implement

Minimum: `initialize`, `tools/list`, `tools/call`. Optional: `resources/list` + `resources/read` (files, tickets), `prompts/get` (canned templates).

Security is **in the host**: allowlist servers, per-tool HITL, no mounting the production DB server into a random chat. The server process is already a **weak sandbox** (separate process); still wrap filesystem servers in a directory jail.

### MCP vs your A2A adapter

| | MCP | Your A2A |
|---|---|---|
| Speaks to | Tools / data | Another **agent** |
| Discovery | Server capabilities on init | Agent Card `/.well-known` |
| Call | `tools/call` | `POST /a2a` JSON-RPC `message/send` |
| State | Usually stateless per call | `task_id` + (your v1) in-memory store |

Spoken:

> MCP is how the host hydrates the tool list and dispatches `tools/call` over JSON-RPC. The model never sees MCP; it sees the same function-calling text I used for `execute_python`. I would register `execute_python` and `browser` as MCP servers under the host’s permission gate. A2A is the other direction — agents calling agents — which is the adapter I shipped on Bailian.

---

## 3. Sandbox — detailed interaction (your `execute_python`)

A sandbox is **where untrusted code runs**, with **CPU / RAM / wall clock / network / FS** caps. The model only receives **stdout** (or a truncated view).

You had two sandboxes in practice:

1. **Microsoft:** IPython kernel via `jupyter_client` (`python_executor.py`).
2. **BrowserUse:** Chromium + CDP (JS in page) — a *browser* sandbox, not a Python VM.
3. **Alibaba:** user code on **Function Compute** (container). Platform sandbox is the cloud’s.

### Microsoft code-act: step by step

**A. Create (once per trajectory)**

```text
SearchAgent.run()
  session_id = search_agent_<uuid>
  jupyter_client.start_kernel()     →  ipykernel_launcher process
  inject into kernel:
      search_client   # Bing + gpt-4.1-mini
      WORKSPACE       # per-run directory
  persist kernel client in executor map[session_id]
```

Kernel is **persistent across cells** (notebook semantics). Different rollouts **never** share a kernel (RL isolation).

**B. One `execute_python` turn**

```text
1. LLM returns <tool_call>{ thought, code }</tool_call>
2. Harness json.loads arguments
3. executor.run(code):
     Jupyter execute_request on shell channel
     Kernel runs the cell
     IOPub: stdout / stderr / execute_result / error
4. Harness:
     timeout → abort cell
     kernel dead → KernelDied (you added this after the silent crash)
     stdout bounded (you capped IOPub accumulation)
5. Only formatted stdout goes back as role=tool
6. Loop until no tool_call or step/search budget
```

**C. Tear down**

```text
shutdown_executor(session_id)  →  kill ipykernel
if parent dies first → orphaned kernel (your pgrep lesson)
```

**D. What the kernel is *not***

- Not `eval()` in the harness process (one bad `os.system` owns the trainer).
- Production: kernel inside **Docker / gVisor / nsjail**, no host secrets, network allowlist (search API only). You listed this as design change #5 — say “not in the research harness; required to ship.”

### Browser sandbox (BrowserUse CodeAct)

```text
Agent writes JS
  → CDP Runtime.evaluate in the page (or isolated world)
  → DOM mutations, queryAll in one round-trip
  → result JSON back to the model
```

Isolation: **site origin + Chromium process**, not your EC2 root. Still: no `page.evaluate` that reads `file://`, download dir jailed, HITL for login.

### Generic sandbox sequence (whiteboard)

```text
claim task
  → create sandbox (container / kernel / VM)
  → mount only WORKSPACE
  → drop caps, set timeout 1–9 min
  → loop: LLM → tool → sandbox exec → truncated observe
  → HITL if gated
  → destroy sandbox (or snapshot for debug)
```

Spoken:

> The model never executes. I start one IPython kernel per episode, inject search_client, run cells, return stdout, then kill the kernel. Persistence is so the agent can fetch once and loop; isolation is per session_id. BrowserUse is the same idea with CDP instead of a kernel. FC is the same idea at deploy time: user code in a cloud container, not on the control plane.

---

## 4. Memory system

“Memory” is **not one Redis**. Split by **lifetime and who is allowed to read it**.

| Layer | Lifetime | Store | Your analogue |
|---|---|---|---|
| **Working** | This context window | `messages[]` | Chat template + tool traces |
| **Scratch** | This run | Kernel vars, `WORKSPACE` files | IPython persistence; browser profile |
| **Episodic** | This / last N runs | Trace DB (Langfuse), `agent_trace.json` | Debug + GRPO trajectories |
| **Semantic** | Org / product | Vector + ACL knowledge base | TikTok JD “knowledge management”; RAG HTML |
| **Procedural** | How to do X | Skills / MCP prompts / playbooks | BrowserUse skills; CodeAct patterns |
| **Shared plan** | Multi-agent run | Blackboard / feature_list.json | HDMAS `task_log`; Anthropic progress file |

### Design (20 min)

**1. Working memory — the window is a cache, not the archive**

- System + tool schemas **prefix-stable** (KV cache).
- Tool output: **truncate / summarize into messages**, full blob in `WORKSPACE/tool/{id}.txt`, model can `read` if needed.
- Hard caps: max turns, max tokens; remind to answer before empty.

**2. Scratch — externalize mid-run state**

Same as Anthropic long-running harness: **files + git**, not “remember in the prompt.”

- `progress.md` / `feature_list.json` (only `passes` flips).
- HDMAS: append-only blackboard under a lock — **protocol instead of hope**.

**3. Episodic — traces for humans and RL, not for every token in the next prompt**

- Langfuse: request-id → steps, tokens, cost.
- Retrieve **summaries** of similar past tasks if you want “memory,” not raw 80-turn dumps.

**4. Semantic — RAG with ACL**

- Index code / docs / tickets; retrieve **for this task**, not the whole monorepo.
- Agent gets **chunks + citations**; humans may get generate. (Your knowledge-base design.)

**5. Write path (who may write memory)**

| Writer | Allowed |
|---|---|
| Tool sandbox | `WORKSPACE` only |
| Agent | progress fields the protocol allows |
| Human HITL | credentials in **browser profile / secret store**, never in messages |
| Retriever | read-only into context, tagged as **data not instructions** |

### Read path on a new session (long-horizon)

```text
1. pwd / smoke test
2. read progress + git log   ← episodic/scratch
3. retrieve KB for this ticket  ← semantic
4. load skills                 ← procedural
5. then first LLM call
```

Do **not** reload the entire previous `messages[]`. That is how you blow the window and still miss the goal.

### What not to do

- One vector DB of “everything the agent ever said” as the memory product.
- Store passwords in retrieval.
- Multi-agent sharing one giant context (HDMAS: share **blackboard**, not tokens).

Spoken:

> Memory is layered. The context window is working memory — I truncate tool output and keep the prefix stable. Run state lives in the kernel and files, which is why execute_python is persistent per session. Across sessions I externalize a progress artifact, same idea as the HDMAS blackboard and Anthropic’s feature list. Long-term org knowledge is RAG with ACL, not more tokens. Credentials never enter memory — that’s the HITL profile on disk.

---

## 5. How the four fit in one picture

```text
User / Telegram / Lark
        │
        v
Host (agent loop + HITL state machine + MCP client)
        │
        ├── LLM  (working memory = messages)
        ├── MCP servers / native tools
        │         └── sandbox: kernel | CDP | FC
        ├── scratch: WORKSPACE, browser profile
        ├── traces: Langfuse
        └── RAG / KB
```

If they only give you 20 minutes, pick **HITL + sandbox** (you have code). MCP is “tools become RPC.” Memory is “don’t put it all in the prompt.”
