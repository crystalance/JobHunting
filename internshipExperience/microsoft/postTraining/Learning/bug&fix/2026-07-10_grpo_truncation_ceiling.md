# Problem: GRPO reward ceiling — most rollouts never finish (truncated mid-tool-call)

**Date:** 2026-07-10
**Component:** `post_training/grpo/` (rollout caps + `widesearch_reward.py`), policy = merged SFT `actor_init_v2`
**Severity:** P2 — not a crash; caps the reward the policy can earn and hides the real learning signal
**Status:** Diagnosed; fix staged (not yet applied — would break mid-run comparability)

---

## 0. TL;DR

Under GRPO rollout, **~50–60% of trajectories hit the turn/length cap and end
mid-`<tool_call>` before ever writing the final answer table**. So `has_table`
sits at ~25% and `f1_row` ≈ 0. The reward barely rewards finishing
(`W_OUT`=0.1) and its length-cost term is **inert** (`n_turns` is always 0 in the
reward), so RL has almost no pressure to make the model converge and emit output.
This — not "wrong answers" — is the dominant failure mode right now.

---

## 1. Symptom

Scaled GRPO run (`run_grpo_train.sh`, batch=8, G=8, 30 steps), reading
`rollout_dumps/{train,val}/*.jsonl`:

- **Val (same 14 prompts, greedy):** f1_item 0.270 (step 0) → 0.245 (step 5);
  `has_table` 0.57 → 0.43.
- **Train:** f1_item bounces 0.075–0.128 across steps with no clear trend;
  `f1_row` low and declining (0.047 → ~0.005); `has_table` ~0.25 flat.

At first glance this looks like "the metric is going down / not learning."

## 2. Diagnosis (how we found the root cause)

1. **Train per-step numbers are NOT comparable.** verl samples the 70 train
   prompts *without replacement* per epoch, so each step grades a **different**
   set of 8 prompts (steps 1–8 are disjoint and cover all 70 once). The
   step-to-step f1 wiggle is mostly **prompt-difficulty noise, not degradation**.

2. **The comparable signals are mildly positive, not negative.**
   - Val (same 14 every eval): 0.270 → 0.245 is within n=14 single-sample noise.
   - **Same-prompt re-exposure** (the true within-policy learning signal): of the
     16 prompts seen at two different steps, **7 improved / 5 worsened, mean
     +0.021** (e.g. `ws_en_019` 0.15→0.50, `ws_en_001` 0.00→0.16). The policy is
     **not degrading**.

3. **Failure-mode breakdown (per 64-rollout step) exposes the ceiling:**

   | symptom | value |
   |---|---|
   | rollouts ending **mid-`<tool_call>`** (no final answer) | ~50–60% (30–41 of 64) |
   | rollouts with **no scoreable table** (`has_table=0`) | ~70% (44–49 of 64) |
   | mean output length | ~32–38k chars; **~50 of 64 exceed 18k** |
   | mean tool calls / rollout | ~7 |

   → The model **rambles / over-searches** and hits `max_assistant_turns=25` or
   `max_response_length=20480` tokens **before writing the output table**. The few
   tables that do get produced are rushed/partial → `f1_row` ≈ 0.

4. **The reward does not counter this.**
   - `W_OUT` (has_table) = 0.1 — a tiny incentive to finish.
   - Length-cost term `W_COST * min(n_turns/20, 1)` is **inert**: `n_turns` is read
     from `extra_info`, which verl never populates for the reward, so it is
     always 0. There is effectively **no penalty for not terminating**.

## 3. Root cause

Two compounding issues:
- **Behavioral:** the SFT policy's tendency to over-search/iterate (never fully
  fixed in SFT — SFT only taught "produce *a* table without crashing") now
  collides with GRPO's turn/length budget, so a majority of rollouts are
  truncated before output.
- **Reward design:** the shaping rewards *quality of a table that exists* but
  does almost nothing to reward *producing/finishing a table* or to penalize
  *running out of budget mid-action*. So the gradient can't push toward the one
  behavior that would most raise the score (converge → write the table).

## 4. Fix (staged — apply only at the step 15–20 decision point)

Do **not** change the reward mid-run (breaks cross-step comparability). If the
step 15–20 checkpoint confirms the plateau, apply:

1. **Wire termination/turns into the reward.** Either plumb verl's
   `AgentLoopOutput.num_turns` into the reward's `extra_info`, or count
   `<tool_call>` occurrences in `solution_str` inside `compute_score`.
2. **Reward finishing, penalize non-termination.** Bump `W_OUT`, and add an
   explicit penalty when a rollout ended mid-tool-call / produced no table
   (turn the currently-inert cost term into a real signal).
3. **Optional anchor:** raise `kl_coef` 0.001 → ~0.01 so RL doesn't erode the
   SFT table-writing skill while exploring.
4. **Optional prompt nudge:** instruct the policy to write a first full table
   early and refine, so a truncated rollout still leaves a scoreable answer.

## 5. Key clarification (what "14/14 outputs" actually meant)

The SFT baseline's "14/14 output" was measured on the **val** split (071–085,
excl 079) via the **harness**, and "output" means *the agent wrote some file* —
**not** that it solved the task. SFT val f1_item was only **0.345**, i.e. outputs
were ~34% item-correct on average. SFT's goal was the **code-act pattern**
(produce a table without crashing), which it achieved; it never "solved" those
problems. Under the stricter GRPO rollout env (greedy val, 25-turn / 20480-token
caps) even the "produced a scoreable table" rate drops to ~57% on val. So the
model does still fail (or only partially succeed) on most problems — and right
now the biggest lever is *finishing*, not *reasoning*.
