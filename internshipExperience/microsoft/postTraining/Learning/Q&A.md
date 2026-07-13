# QA

## questions 
1. what's KL in GRPO?
2. why my mentor says we dont have labled data to do SFT? Why need labled data? What's the cost of getting labled data? since it is impossible for us to lable manually, cant we just generate it using a more capable model?
3. how post training works? how RL works? how RL on llm works? i dont have a concrete sense of how this changes every parameter in a llm?
4. there's so much parameters in LLM, so many layers, how does the backward forward change each parameter?

5. base on current situation, why should we choose GRPO? 
6. choose what model for training?


## Why we dropped Qwen2.5-Coder-7B-Instruct (2026-07-06)

**Short version:** for our code-act agent, the bottleneck is *driving the tool
loop*, not *writing code*. Coder-7B is better at code but refuses to play the
agentic protocol, so it performs worse than the plain instruct model.

### The task needs TWO separate skills
Our harness is a **code-act loop** (not a one-shot coding question). Each turn the
model must:
1. emit a **structured tool call** — `execute_python({thought, code})` via the
   function-calling channel (rendered as `<tool_call>...</tool_call>`),
2. wait for the execution result (stdout/traceback) as a tool message,
3. emit the NEXT tool call based on that result,
4. repeat ~10 turns until the output CSV is complete, then give a plain-text
   final answer.

| Skill | What it is | Coder-7B | 7B-Instruct |
|-------|------------|----------|-------------|
| **Code knowledge** | writing correct Python | strong | buggy |
| **Agent protocol** | emitting *tool calls* (not prose), iterating turn-by-turn, driving the loop to completion | poor | ok |

### What Coder-7B actually does
Coder models are trained mostly on code completion / coding Q&A, so their instinct
is to *answer like a coding question*: write a plan plus a whole script inside a
```python``` markdown block **in one message, then stop**. It never emits a tool
call and never iterates.

Measured head-to-head on `ws_en_028` (same prompt, same case):
- **Coder-7B**: 1 turn, `has_toolcall_tag=False`, `has_python_fence=True`, no
  output CSV, score 0 — it narrated a plan + a ```python``` block and quit.
- **7B-Instruct**: ~5-8 turns, emits `<tool_call>`s and drives the loop, no CSV
  (buggy code), score 0 — but it at least *plays the protocol*.

### Why the recovery layer doesn't rescue it
The tool-call recovery layer fixes a *malformed tool call* — e.g. single-quoted
JSON **inside** a `<tool_call>` block. Coder-7B produces **no tool-call attempt at
all** (just a ```python``` narration), so there is nothing to recover. Its failure
is a *behavioral choice* (narrate vs. act), which a parser cannot fix. It emits
```python``` (loose code), not ```json``` or `<tool_call>` (a tool call).

### First time we saw it (2026-07-03)
Zero-shot tool-call format compliance with the harness system prompt:
- Coder-7B: 0/6 (even 0/6 with a strong "use the tool" directive) — emits
  markdown/`<tool>` instead of `<tool_call>`.
- 7B-Instruct: 6/6 with the raw prompt.
- 3B-Instruct: 3/4 with a directive.

### Conclusion
Coder-7B's strong code prior does **not** help, because the wall is
loop-driving + completion, not raw code knowledge. Swapping to Coder is the wrong
lever. The right levers are: (a) SFT cold-start to teach loop-driving + correct
code (distill from a strong teacher, e.g. gpt-5.4), then GRPO; or (b) a stronger
base model. We standardize on **Qwen2.5-7B-Instruct** for now.


## SFT loss masking — "context" vs "targets" (2026-07-06)

SFT trains by **next-token prediction**: at each position the model predicts the
next token and a loss grades how wrong it was. In a multi-turn agent conversation,
some tokens are things the model must *produce*, others are just *given* to it. Loss
masking = grade the model ONLY on the tokens it is responsible for producing.

Analogy: a fill-in-the-blank exam — the model reads the whole conversation but is
graded only on the blanks *it* must write.

| Message | Produced at inference by | Grade it? |
|---|---|---|
| `system` (prompt) | us (fixed) | ❌ masked |
| `user` (query) | environment | ❌ masked |
| `tool` (search results / stdout) | the kernel/environment | ❌ masked |
| `assistant` (tool_calls + final answer) | **the model** | ✅ loss-on |

Why mask the rest:
- Grading on `tool` tokens would teach the model to **hallucinate search results** —
  but those come from the real environment; it should *react* to them, not produce them.
- Grading on `user`/`system` is pointless (it doesn't write those).

Mechanics: masked tokens get label `-100` (PyTorch `ignore_index`) so cross-entropy
skips them. The whole sequence still goes through the forward pass (model reads
everything), but **gradients flow only from assistant-token positions**.

```
<system ...>            ▁▁▁▁▁▁   masked
<user: compile table>   ▁▁▁▁     masked
<assistant tool_call>   ✔✔✔✔     loss-on  (model must learn to emit this)
<tool: "142,976 km">    ▁▁▁      masked   (environment gave it)
<assistant tool_call>   ✔✔✔✔     loss-on
<tool: ...>             ▁▁       masked
<assistant final text>  ✔✔✔✔     loss-on
```

"Serialized exactly as the template renders `<tool_call>...</tool_call>`": at
inference the model must output the tool call in the *exact text form the vLLM
parser reads* (`<tool_call>\n{"name":"execute_python","arguments":{"thought":...,
"code":...}}\n</tool_call>`). So SFT targets must be those exact tokens (same chat
template the server uses). Bonus: training on the native format teaches the model to
emit valid `<tool_call>`s itself → less reliance on the recovery layer.


## Why LoRA for the SFT cold-start (2026-07-06)

LoRA (Low-Rank Adaptation): **freeze the base weights**, insert small trainable
low-rank adapter matrices (rank 32–64) into attention/MLP; only adapters train
(<1–2% of params). Why it fits this cold-start:

1. **Memory** — full FT needs weights + grads + Adam states (m,v fp32 ≈ 4× model) +
   activations; at 32k seq on 4×A100 that's tight. LoRA shrinks grad/optimizer state
   ~10× → fits with room for long context.
2. **Anti-overfit** — the distilled set is small (tens of trajectories); full FT of a
   7B on so little data overfits / forgets. LoRA's limited capacity regularizes.
3. **We teach behavior, not knowledge** — goal is "drive the loop + valid tool calls +
   valid code", which LoRA handles well.
4. **Cheaper/faster/reversible** — tiny checkpoints, swappable adapters, easy iteration.

Escalate to full FT only if LoRA underfits (student still can't complete val cases).


## Is the IPython kernel persistent? Does it matter? How do others cope? (2026-07-06)

**Yes — persistent per trajectory.** `python_executor.py` spawns a Jupyter/IPython
kernel (`jupyter_client`) and keeps it alive across `execute_python` calls (notebook
cell semantics: variables/imports/data survive between cells). Kernels are keyed by
`session_id`; `SearchAgent.run` makes one per run (`search_agent_<uuid>`) and calls
`shutdown_executor` at the end. Different trajectories → independent kernels.

**Why it matters:** state builds up across turns (search → store in var → process →
write file). Without persistence the model would re-fetch/re-declare every cell →
wasted searches (quota), longer code, more tokens, worse on long tasks. It also
matches what the prompt promises ("kernel persists; reuse variables").

**Why it's non-trivial / how the field copes:**
| Concern | Standard handling |
|---|---|
| Isolation at RL scale (G parallel rollouts) | one kernel per session/rollout (our `session_id`); never share |
| Security (arbitrary model code) | kernel in Docker/gVisor/nsjail/firejail, no host FS/secrets (design change #5) |
| Runaway cells (loops/OOM) | per-cell timeouts + CPU/mem/wall-clock caps; restart on crash |
| Kernel/process leaks | explicit teardown; kernel pooling/recycling |
| Replay/determinism for RL | isolated workspace + cached search + optional state snapshot |

**Stateful (persistent) vs stateless:** code-act frameworks (OpenHands, SWE-agent,
the CodeAct paper, Qwen-Agent, OpenAI Code Interpreter) all use a **persistent
per-session kernel** because it mirrors a data analyst's notebook workflow (fetch
once, iterate). Stateless (fresh process per cell) gives trivial isolation +
determinism but forces state rebuild every cell — bad for our fetch-once/process-many
task. Consensus: **persistent kernel + strict per-session isolation + sandboxing**.
Concrete implication for us: RL needs **per-rollout kernel isolation** (design change
#6), which the `session_id` mechanism already supports.


## DPO
