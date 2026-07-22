#Q&F


---
## 7/5/2026
1. situation: successfully deployed qwen2.5-7B-Instruct
2. The one real bug to fix: the agent stops the moment an assistant turn has no parsed tool_call. Qwen2.5-7B sometimes emits a <tool_call> block inside message content with slightly malformed JSON; vLLM's parser drops it → the loop ends after 2 turns with no CSV. This is a P0 harness-robustness item (open models need a fallback that recovers content-embedded tool calls), independent of model quality.
    1. i want to see the workflow or the protocal detail on how llm generate the tool_call, and how vLLM parse it, and what passed to our agent? 
    2. how to cope with this malformed json problem, do we need to do SFT(RFT) now? or we should change to qwen3-8B?
        1. Harness fragility (engineering): SearchAgent treats "no parsed tool_calls" as "the model is done" and terminates. That's an unconditional assumption that's simply wrong for open models.
        2. Model format reliability (model quality): Qwen2.5-7B occasionally emits a malformed <tool_call> (stray "}}).
        3. fix: see WebSearchResearch/post_training/design/tool_call_robustness_fix.md
3. for RL,(GRPO) what infomation do we need for training(like reward)
4. why do we need Observability — format_recovered / json_repaired / malformed_unrecoverable flags feeding the P1 metric and RL format_ok reward?
5. so the base model: cant output the right tool call format, 2. little context window(32678) that wont be enough, how do mainsteam in academic/industry to cope with this 
6. how to design the reward function, what rubric should we consider?
7. what's the boardline of improving the prompts vs fine-tuning?

8. base model choosing?
---
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
---
9. gpt5.4 is available, but before that, i want to confirm few things, if we use gpt 5.4 or other better model , they normally comes with a bigger context window, which means the trajetory may exceed the context window? then what to do?, second, in our original implementation, we told the model to generate the thinking path, is it necessary? in what form does it return the thinking info? in myunderstanding, tool call would be enough maybe we should look deep into the whole message list,design carefully before we actually proceed to SFT/RFT
---
Q1: Context window — teacher size ≠ trajectory length
Your worry is that a bigger-context teacher produces trajectories the 32k student can't hold. The data says otherwise, and here's the precise reasoning:

This whole trajectory was 6.2k tokens — nowhere near 32k. Trajectory length is driven by the task and how compact observations are, not the teacher's context capacity. gpt-5.4 won't emit longer trajectories just because it can — it takes as many turns as the task needs.
Observations are already compact (174–1255 tokens each) because your search returns LLM-summarized JSON (answer + sources_url), not raw web dumps. That's the single biggest context saver, and it's already in place.
When a trajectory does exceed the student's window (big tables like ws_en_003's 58 rows), the standard practice is simple: filter the SFT set to trajectories that fit (e.g. ≤ ~28k, leaving headroom). You measure every teacher trajectory's token length with the student's tokenizer and drop/exclude the ones that don't fit. A student that can't hold a 40k trajectory can't learn or run it anyway — so excluding those is correct, not a loss.
Extra levers if needed: cap per-observation tokens (truncation with a marker), and cap max_iterations.
So the plan: during distillation, log each trajectory's student-token length; keep those under budget. No special handling of the teacher's large context is required.

Q2: The thought field — where it lives, and whether to keep it
Where/what form: thought is not separate "thinking" text. It's a parameter of the tool call, living inside the assistant message's tool_calls[0].function.arguments JSON alongside code. The assistant message's content is None; the entire assistant turn is the tool call {thought, code}. Example:

So it's a structured, always-visible, loggable field — not a hidden CoT or a native <think> block. It costs only ~50–80 tokens/turn.

Is it necessary? Your instinct ("tool call would be enough") is functionally correct — the code alone runs. But for a weak 7B, the thought is a cheap plan-before-act scaffold that measurably helps planning ("think, then write code"). Trade-offs:

Keep it (recommended): ~60 tokens/turn, gives the small model a reasoning channel; it's already in the frozen tool schema, so keeping it means the SFT data matches the serving harness exactly.
Drop it: slightly shorter trajectories, but you'd change the tool schema (breaks harness consistency) and remove the planning scaffold — risky for a model that already struggles with planning.
My recommendation: keep thought for SFT. It's cheap, it aids weak-model planning, and it keeps train/serve consistent.

Design implication for the SFT data format
From the message-list structure, the SFT setup is the standard multi-turn agent format:

Context (loss-masked): system, user, and all tool (observation) messages.
Training target (loss-on): the assistant messages — i.e. the tool_calls ({thought, code}) and the final text answer.
You train the student to reproduce the teacher's assistant turns given the same context. Standard "mask everything except assistant tokens" loss.
This means we should capture, per trajectory, the exact message list (not just the summary log) so we can replay it as (context → assistant target) pairs — currently agent_trace.json stores conversation, which is close, but I'd want to confirm it preserves tool_call_ids and the exact tool messages for clean formatting.

Suggested next move
Before any training, let me draft a short design doc in post_training/design/ that pins down: (1) trajectory-length filtering rule, (2) keep-thought decision, (3) the exact SFT message→target format + loss masking, (4) teacher choice (gpt-5.4) and rejection-sampling threshold, (5) how many instances. Want me to write that design doc, and separately verify agent_trace.json captures everything we need for clean SFT formatting?
----
10. how much trajectory do you think we can use for SFT to get a relatively good result? i want to have a basic concept.

11. whether the ipython kernel is persistent? is it really matter? how do others cope with this situation?
Is the IPython kernel persistent? Does it matter? How do others cope?
Yes, it's persistent — per trajectory. python_executor.py spawns a Jupyter/IPython kernel via jupyter_client and keeps it alive across execute_python calls, "mimicking notebook cell semantics." State (variables, imports, loaded data) survives across cells. Kernels are keyed by session_id: search_agent.py creates one per run() (search_agent_<uuid>) and tears it down at the end (shutdown_executor). Different trajectories → independent kernels.

Does it matter? Yes, a lot — it's the core of the code-act paradigm:

State builds up across turns: search in cell 1 → store in a variable → process in cell 2 → write file in cell 3. Without persistence the model would have to re-fetch/re-declare everything every cell → wasted searches (quota!), longer code, more tokens, and it'd struggle on long tasks.
It matches the prompt's promise ("the kernel persists; reuse variables"), which the model relies on.
Why it's non-trivial (and how the field copes):

Concern	How others handle it
Isolation at RL scale (G parallel rollouts)	one kernel per session/rollout (we do this via session_id); never share
Security (arbitrary model code)	run each kernel in Docker/gVisor/nsjail/firejail with no host FS/secrets (our design doc's change #5)
Runaway cells (infinite loop, OOM)	per-cell timeouts + CPU/mem/wall-clock caps; restart on crash
Resource leaks (kernels = processes)	explicit lifecycle/teardown, kernel pooling/recycling
Replay/determinism for RL	isolated workspace + cached search + optional state snapshot
Stateful (persistent) vs stateless — why the field picks persistent for code-act: OpenHands, SWE-agent, the original CodeAct paper, Qwen-Agent, OpenAI Code Interpreter — all use a persistent per-session kernel, because it mirrors how a data analyst works in a notebook (fetch once, iterate on the data). The alternative (fresh process per cell) gives trivial isolation and determinism but forces the model to rebuild state every cell — bad for our fetch-once-process-many task. So the consensus is: persistent kernel + strict per-session isolation & sandboxing. For us, the concrete implication is that RL needs per-rollout kernel isolation (design change #6) — which the executor's session_id mechanism already supports.

Now recording all three questions.

----
12. Progress since last check
Distillation — DONE. 57 gpt-5.4 train trajectories (ws_en_006–070) + 12 pilot = 69 total.

SFT set rebuilt — 48 kept / 18 dropped (drops: 12 too-long >28.7k-token big-table cases, 6 low f1_item). That's ~4× the pilot, many high-quality (f1_item 0.9+).

LoRA retrained — succeeded. 3 epochs on 48 examples, train_loss 0.43 (down from the pilot's 0.62). Adapter saved to post_training/sft/ckpt_train, served on GPU2:8002 as sft_train.

The problem I hit
Testing sft_train on held-out ws_en_028 (gpt-4.1-mini search, as required) crashes the harness silently — reproducibly (2×): no output, no trace, no error line, and it leaves an orphaned IPython kernel (proof the process died by a signal, not a clean exit).

Root cause: the retrained model regressed into runaway over-searching — 97–115 search queries in just 5–7 turns. It imitated gpt-5.4's aggressive multi-query fan-out but never converges to writing the output file. During that heavy in-kernel search I/O the harness's python_executor.run() dies (it only guards against a read timeout, not kernel death / unbounded output). Not memory (866GB RAM, 835 free).

So: training worked, but this checkpoint is behaviorally worse than the pilot for actually finishing, and the harness isn't crash-safe against it.

---> just the harness problem, 
----
13. full paramter SFT vs Lora?
Full SFT vs GRPO — my recommendation: skip full-FT, go to GRPO
Here's the reasoning:

1. LoRA already achieved SFT's actual job. The purpose of an SFT cold-start before RL is narrow: get the policy into a region where it completes the task and earns non-zero reward, so RL has a gradient to climb. We're there — F1_item 0.80, writes output, drives the loop. More SFT has diminishing returns for bootstrapping RL.

2. For 48 examples, LoRA is the better SFT choice, not a compromise. LoRA's low-rank constraint is itself a regularizer — it's why it resists overfitting on small data. Full-FT of a 7B on ~50 trajectories has high capacity and will tend to memorize trajectories and erode general ability (catastrophic forgetting). So full-FT would likely make things worse here, not better. Full-FT pays off when you have thousands of diverse examples.

3. The "fixed benchmark" limitation hurts SFT, not RL. This is the crux. GRPO generates its own on-policy data — every rollout is fresh training signal, scored directly by the WideSearch F1 reward. You're not data-limited in RL; you're compute-limited. And RL optimizes the actual objective (F1) rather than imitating trajectories. So given a fixed benchmark, RL is the right place to spend compute.

4. On "run multiple models to get more trajectories" — you're right, and it has a name. That's rejection-sampling fine-tuning (ReST / RFT / STaR): sample k trajectories per prompt (from gpt-5.4 at temperature, and/or a second teacher), keep the ones that pass a reward bar. 68 prompts × ~3 kept ≈ 200 trajectories — that's the correct lever if we need more SFT data. But I'd only reach for it if the cold-start proves too weak for RL. Note: mixing in weaker models adds noise to a cold-start; better to multi-sample the strong teacher.

So the trade-off answer: don't full-FT on 48 examples. Keep the LoRA cold-start, and put the compute into GRPO (self-generated data, optimizes F1 directly). Hold rejection-sampling in reserve if RL bootstrapping stalls.

But — gate this on the val numbers first. Let me run the held-out set now so we decide on evidence, not a single instance.

Let me launch the val-set evaluation on the LoRA model (held-out ws_en_071–085, skipping 079 which was distilled in the pilot).

## Training details
1. in grpo, what does this step mean? i need all training details related
---
Read [](file:///home/dkidna/WebSearchResearch/post_training/grpo/run_grpo_v3.sh#40-40), lines 40 to 88

You're looking at the handover, and "this step" = **one GRPO training step** (the `step:1 … step:21` in the logs, the `1/21` in the progress bar). Here's exactly what one step is and all the training details behind it.

## What "1 step" means

**One step = one full policy-gradient update built from a fresh batch of self-play episodes.** With our config, each step is:

$$\underbrace{8 \text{ prompts}}_{\text{train\_batch\_size}} \times \underbrace{8 \text{ rollouts each}}_{\text{rollout.n (the GRPO group)}} = \mathbf{64 \text{ rollouts / step}}$$

The run is **21 steps total** (`total_training_steps=21`). `total_epochs=100` is just a high cap so the step count is the real stopper. With 70 train prompts and 8 prompts/step, one pass over the data (an "epoch") ≈ 9 steps, so 21 steps ≈ 2.3 epochs (matches the log: `training/epoch:2` at step 21).

## Anatomy of one step (the 4 phases you see in the timing logs)

| Phase | What happens | log key (per-step time) |
|---|---|---|
| **1. Rollout / generation** | For each of the 8 prompts, sglang generates 8 full **multi-turn agent episodes** — the model reasons, emits `execute_python` tool calls, real Bing/gpt-4.1-mini search runs, kernel returns output, repeat until it writes the final table or hits a limit. | `timing_s/gen` (~340s, the bulk) |
| **2. Reward scoring** | Each of the 64 finished episodes is scored by `widesearch_reward.compute_score` (WideSearch gpt-4.1 judge → f1_item/f1_row/has_table, minus fabrication, or the −0.10 no-table floor). | `timing_s/reward` |
| **3. Advantage (GRPO)** | Within each 8-rollout group, compute the group-relative advantage $A_i=\frac{R_i-\text{mean}(R)}{\text{std}(R)}$. No critic network (that's the "G" in GRPO). | `timing_s/adv` |
| **4. Actor update** | PPO-style gradient update on the LoRA/actor params, with a KL penalty pulling toward the frozen reference (SFT-v3) policy. | `timing_s/update_actor` (~152s) |

Total ≈ **535 s/step** (`timing_s/step`), plus `timing_s/testing` (~250–300s) on the steps that validate.

Inside phase 4: the 64 samples are split into minibatches of `ppo_mini_batch_size=8` → **8 gradient updates per step**, each with `ppo_micro_batch_size_per_gpu=1` (so gradient accumulation of 8 micro-batches across the 4 GPUs).

## All the training hyperparameters (from run_grpo_v3.sh)

**Algorithm**
- `adv_estimator=grpo` — group-relative advantage, no value/critic model.
- `kl_ctrl.kl_coef=0.005` — KL penalty weight vs the reference policy (anchors to SFT-v3; between v1's 0.001 and the over-tight v2's 0.01).
- **Reward** = widesearch_reward.py (`compute_score`): `1.0·f1_item + 0.8·f1_row + 0.1·has_table − 0.1·constant_fill`, **no turn-cost**, hard `−0.10` floor when no table.

**Data / sizes**
- `train_batch_size=8` (prompts/step), `rollout.n=8` (group size) → 64 rollouts/step.
- `ppo_mini_batch_size=8` → 8 grad updates/step; `ppo_micro_batch_size_per_gpu=1`.
- `max_prompt_length=3072`, `max_response_length=20480` (tokens; long because episodes are multi-turn).
- `optim.lr=1e-6` (low, typical for RL fine-tuning).

**Rollout engine**
- `rollout.name=sglang`, `mode=async`, `tensor_model_parallel_size=1`, `gpu_memory_utilization=0.55`.
- **Multi-turn agent:** `multi_turn.enable=true`, `format=hermes`, `max_assistant_turns=25`, `max_tool_response_length=8192`, tools from `tools.yaml`, agent loop from `agent_loop_config.yaml` (the persistent-kernel `widesearch_tool_agent`).

**System / distribution**
- `strategy=fsdp2` for both actor and reference, `n_gpus_per_node=4`, `nnodes=1`.
- Init policy: `actor_init_v3` (the SFT-v3 merged model).

**Checkpointing / schedule**
- `total_training_steps=21`, `save_freq=3`, `test_freq=3` (save + validate every 3 steps: 3,6,9,…,21).
- `max_actor_ckpt_to_keep=2` (only last 2 FSDP checkpoints on disk; each ~86 GB with optimizer).
- `default_local_dir=checkpoints/train_v3`; rollouts dumped to `rollout_dumps_v3/{train,val}`.

## What each step reports (the metrics you saw)

Per step the log prints, e.g. at step 21:
- `actor/entropy:0.545` — policy randomness (healthy; ~0 would mean collapse).
- `actor/pg_loss`, `actor/ppo_kl:~0`, `actor/grad_norm:0.60` — update health.
- `critic/score` / `critic/rewards` mean/max/**min** — the reward distribution; **min = −0.10 means the no-table floor fired**.
- `critic/advantages` min/max — spread ≠ 0 → there's a learning signal (the thing v2 lost when it collapsed).
- `response_length/mean:~12.7k`, `num_turns/mean:~15` — behavior stability (halving length = collapse warning).
- On validate steps: `val-core/widesearch/reward/mean@1`, `f1_item`, `f1_row`, `has_table`, `n_turns` (the greedy val curve — noisy, trend-only).

## How a step maps to the outcome
Across the 21 steps the policy did an "unlearn-then-relearn": dipped steps 3–9, recovered from step 12, and by step 21 had higher coverage + completion than the SFT-v3 start — without collapse, because we removed the turn-cost and anchored with KL 0.005. Full curve is in 7_21_2026/grpo_v3_training_result.html.

Want me to add this "anatomy of a GRPO step" section into the handover doc (or the reward-design doc) so it's captured for the next person?
---