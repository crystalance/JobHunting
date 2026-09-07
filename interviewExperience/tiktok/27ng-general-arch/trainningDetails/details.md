# Post-Training — Full Training Details (reference sheet)

> Everything below is read directly from the code in
> `internshipExperience/microsoft/postTraining/code/post_training/` —
> `sft/build_sft_data.py`, `sft/train_sft.py`, `grpo/widesearch_reward.py`, `grpo/run_grpo_v3.sh` —
> plus the strategy/post-mortem docs. Use this when the interviewer drills past the spoken answers
> in `postTraining_spoken_answers.md`.

---

## 1. The environment (what a "trajectory" is)

- Agent = Qwen2.5-7B-Instruct driving **one tool**: `execute_python` — a persistent IPython kernel
  with `search_client` (`.search(query)` accepts a single query or a *list* of queries) and
  `WORKSPACE` preloaded. Only printed stdout is visible to the model.
- A trajectory = multi-turn chat: assistant emits `<tool_call>{thought, code}</tool_call>` (Hermes
  format), tool returns stdout, repeat, then a final assistant message containing the markdown
  answer table. Saved as `agent_trace.json` (full conversation).
- Task = WideSearch (EN train 001–070, val 071–085, test 086–100; + ZH splits).
- Search budget per episode: 60 searches, ≤20 queries per call, results cached
  (`SEARCH_CACHE_DIR`) so training/eval reruns are comparable and cheap.

## 2. SFT trajectory generation

Three sources, blended (strategy doc §3):

1. **Teacher distillation** — GPT-5.4 as policy + gpt-4.1-mini as the search summarizer (hard
   rule: search side stays fixed so quality differences are attributable to the policy). Teacher
   system prompt *explicitly instructs* the enumerate-then-loop pattern:
   - Phase A: one search to discover the full entity/row set;
   - Phase B: loop-construct one query per entity, batch them in one `search(queries)` call;
   - Phase C: parse into rows, write the table, re-search only rows still `nan`.
2. **Self-distillation / RFT** — mine the previous GRPO run's rollouts (step_30) that already used
   the pattern and scored high (~42% did); on-distribution and cheap.
3. **A few hand-written canonical exemplars** to seed the exact template.

**Rejection sampling:** k=4 trials per prompt, keep best-by-F1 that matches the pattern
(pattern detected by `analyze_codeact.py`-style check on the emitted code). Teacher pilot
validated at f1 0.82 with 100% pattern compliance before scaling generation.

## 3. Filtering (the exact gates, from `build_sft_data.py`)

Trial-aware selection (`--scores` path) applies, in order:

| Gate | Threshold | Why |
|---|---|---|
| `has_output` | must be true | trajectory wrote an answer file |
| `converged` | must be true | reached a final answer (didn't hit the cap mid-run) |
| `looped` | must be false | no repeated-action loops |
| `err_rate` | ≤ 0.2 (`--err_max`) | ≤20% of tool calls errored |
| `eval_err` | must be false | scoreable by the WideSearch evaluator |
| `f1_item` | ≥ 0.5 (`--tau_item`) | cold-start **quality floor** — teach correctness, not just format |
| `f1_row` | ≥ `--tau` | coverage floor (raised for v3 data) |
| LLM judge (optional) | `keep=true` in `verdicts.jsonl` | `llm_trajectory_judge.py` screens for bad behavior F1 can't see |
| final message | assistant with non-empty content | must actually end with the answer |
| length | ≤ 28,672 tokens | fits the student's window (32k minus headroom) |

Then **top-N = 2 per instance**, ranked by `(−f1_row, −f1_item, n_searches, n_turns)` —
**correctness first, efficiency as tie-break**. Balance EN/ZH.

## 4. Tokenization & loss masking (a detail interviewers like)

- Rendered with the **Qwen2.5 chat template including the tool schema**, so training format ==
  serving format exactly (what vLLM/sglang parses is what the model saw in training).
- **Assistant-only loss** via *incremental prefix rendering*: chat templates are
  prefix-consistent, so the token span of assistant message k is
  `render(messages[:k+1]) − render(messages[:k])`. Those tokens get real labels; everything else
  (system, user, tool outputs) is `-100`.
- Gotcha fixed in code: the OpenAI SDK stores `tool_calls.function.arguments` as a JSON *string*;
  the template must receive a *dict*, otherwise it renders an escaped string that doesn't match
  the model's native tool-call emission format. `build_sft_data.py` parses it back to an object.
- Self-test asserts `<tool_call>` and `execute_python` appear in the decoded loss-on span.

## 5. SFT training config (`train_sft.py`)

| Item | Value |
|---|---|
| Base | Qwen/Qwen2.5-7B-Instruct |
| Method | LoRA r=32, α=64, dropout 0.05, targets = q/k/v/o_proj + gate/up/down_proj (all-linear) |
| Precision | bf16 + flash-attention-2, gradient checkpointing |
| LR | 1e-4, cosine schedule, 3% warmup |
| Batch | per-device 1 × grad-accum 4 |
| Epochs | 3 (optional per-epoch save for val-completion gating) |
| Max len | 28,672 |
| Output | LoRA adapter → `merge_sft_lora.py` → full HF checkpoint `actor_init_v3` (the RL actor + reference) |
| Gate before RL | pattern% ≥ 80% and f1_item ≥ v2-SFT (0.35) |

## 6. GRPO reward — all three versions (the answer to "I need different versions")

Implemented in `widesearch_reward.py`; every weight is env-overridable (`GRPO_W_*`), so versions
are config, not code forks. Scoring calls the **official WideSearch evaluator** on the final
answer table (gold-verified; gpt-4.1 judge for free-text columns); `has_table` = produced
anything scoreable (`f1_item > 0 or f1_row > 0`); `constant_fill` = heuristic detector for
filler-value fabrication; `n_turns` counted from `<tool_call>` occurrences in the response
(verl never plumbs `num_turns`).

**v1 — original (stable but under-powered)**

```
R = 1.0·f1_item + 0.5·f1_row + 0.1·has_table − 0.1·turn_cost − 0.1·constant_fill
    turn_cost = min(n_turns/20, 1)   # INERT: n_turns never plumbed → always 0
```
Outcome: stable 30 steps; −48% turns as an *emergent* effect (the penalty term was dead);
no held-out F1 gain — coverage weight too weak, and ~50–60% of rollouts truncated
mid-tool-call before writing a table (the real ceiling, diagnosed in the truncation post-mortem).

**v2 — the collapse (activated turn cost)**

```
R = 1.0·f1_item + 0.8·f1_row + 0.05·has_table − 0.1·turn_cost − 0.1·constant_fill
    turn_cost = min(n_turns/12, 1)   # ACTIVE: n_turns = count("<tool_call>")
    KL 0.001 → 0.01 ; init = SFT-v2 ; keep-last-2 checkpointing
```
Outcome: val f1 0.24→0.32 by step 5, **0.000 by step 15**. Root cause: the turn penalty paid the
policy to stop early → "one search, no table" → once every rollout in a group degenerates
identically, group-relative advantage = 0 → zero gradient → absorbing state. Keep-last-2 deleted
the only good checkpoint (step 5). Full post-mortem: `rl_first_collapse_lessons.md`.

**v3 — final (shipped)**

```
if not has_table:  R = −0.1                      # hard floor: giving up is strictly worst
else:              R = 1.0·f1_item + 0.8·f1_row + 0.1·has_table − 0.1·constant_fill
# NO turn-cost term (W_COST = 0)
KL = 0.005 ; init = SFT-v3 ; best-by-val selection (save/test every 3 steps)
```
Design principles (reward-design doc): outcome terms carry the load; never let a shaping term
fight completion; guarantee ordering finish > give-up structurally (floor), don't inflate
`has_table` (a big finish bonus is farmable with junk tables); efficiency comes emergent from
KL-anchoring to the already-efficient SFT-v3, not from a penalty.

## 7. GRPO training config (`run_grpo_v3.sh`, verl `main_ppo`)

| Item | Value |
|---|---|
| Algorithm | GRPO (`algorithm.adv_estimator=grpo`), group size **G=8** (`rollout.n=8`) |
| Actor init / ref | merged `actor_init_v3` (both) |
| LR | 1e-6; train_batch_size 8; ppo_mini_batch 8; micro batch 1/GPU |
| KL | `kl_ctrl.kl_coef=0.005` |
| Rollout engine | **sglang, async mode**, multi-turn Hermes format, GPU mem util 0.55, TP=1 |
| Caps | max_prompt 3,072 · max_response 20,480 · max 25 assistant turns · tool response ≤8,192 |
| Hardware | FSDP2, 4×A100, 1 node |
| Steps | 21 total, save+validate every 3, `max_actor_ckpt_to_keep=2` (disk: verl ckpt ~86 GB) |
| Reward | `custom_reward_function.path=widesearch_reward.py`, async reward workers |
| Search | shared cache dir, 60-search episode budget, ≤20 queries/call, 4 workers |
| Runtime | ~5 h; no collapse (entropy 0.545 final, response length stable ~12.7k) |

## 8. Evaluation protocol (variance-controlled)

- Merge best-by-val checkpoint → HF; serve one vLLM per GPU (`eval_checkpoints.sh`).
- **k=4 samples @ temp 0.7** (never single greedy — greedy proved non-reproducible),
  **shared warmed search cache**, both models evaluated in the **same session** (Bing results
  drift across sessions, so cross-session numbers are not comparable — this is why SFT-v3 was
  re-run alongside GRPO-v3 for the final table).
- Report **held-out test only** (EN 086–100 + ZH 001–020); val (≥30 prompts) is for checkpoint
  selection only. Score both axes: `score_v3_eval.py` (f1) + `analyze_codeact.py`
  (turns / batching / pattern%).

## 9. Results progression (EN item-F1 unless noted)

| Stage | f1_item | f1_row | Notes |
|---|---|---|---|
| Base Qwen2.5-7B | ~0.05 | — | can't play the game (format/protocol failures) |
| SFT-v2 | 0.347 | 0.118 | pattern learned, coverage weak; 42% enumerate-then-loop |
| GRPO-v1-reward | 0.344 | — | tied on F1, −48% turns (emergent) |
| GRPO-v2-reward | **collapsed** | — | step 15 → 0.000, turn-cost reward hacking |
| SFT-v3 | 0.375 | 0.119 | enumerate-then-loop in data, pattern ≥80% |
| **GRPO-v3** | **0.408 (+9%)** | **0.138 (+16%)** | −16% reasoning calls, −14% total LLM calls, −9% latency; ZH has_table 0.72→0.82 |

## 10. Q&A — reward-scale semantics & reward hacking

**Q: Do the absolute reward values mean anything, or only proportions?**
GRPO's advantage is a per-group z-score `A = (R − mean)/std`, which is invariant to affine
transforms — so global scale/offset cancel. Three things DO carry meaning:
1. **Term ratios** (1.0 vs 0.8): how rollouts *rank* against siblings when trading item-F1 vs row-F1.
2. **Relative gaps within a group**: a huge floor (−10) would inflate group std and shrink the
   z-scored differences among *finishing* rollouts — gradient budget all goes to "avoid no-table",
   none to "make better tables". Hence −0.1: strictly worst, but doesn't drown the finisher signal.
3. **Scale vs the KL coefficient**: the KL penalty is in absolute units, so scaling reward terms up
   with `kl_coef` fixed silently weakens the KL leash. Reward scale is only free *jointly* with KL.

**Q: Is the v2 collapse "reward hacking"?**
Yes — textbook specification gaming, plus a GRPO-specific twist: the hacked behavior ("one search,
stop") isn't just bad, it's an **absorbing state** — once all G rollouts degenerate identically,
std→0 → advantage→0 → zero gradient, no escape. The full anti-hacking toolkit used in v3:
sparse outcome-carried reward · no shaping term that fights completion · structural ordering
guarantee (hard floor) instead of tunable incentives · refusal to inflate `has_table` (farmable
proxy) · a purpose-built anti-exploit term (`constant_fill` vs filler-value F1 gaming) · KL anchor
to a good reference · live collapse monitoring (entropy, response length, val has_table) ·
best-by-val checkpointing. Interview framing: "how do I prevent reward hacking? Let me tell you
how I caused it first."

**Q: What exactly is a "step", and how do the run numbers decompose?**
One step = one full GRPO iteration: draw `train_batch_size=8` prompts → roll out `n=8` (G)
complete multi-turn episodes per prompt (**64 episodes with live search**) → score each with the
reward → z-normalize within each group of 8 siblings → **one policy update** (mini-batch = full
batch). The arithmetic that follows:
- **Epoch ≈ 8.75 steps** — 70 train prompts sampled *without replacement*, so steps 1–8 are
  disjoint and cover all 70 once. Corollary: per-step train F1 compares *different prompts* each
  step → the step-to-step wiggle is prompt-difficulty noise, NOT a learning signal. Only the
  fixed val set (every `test_freq=3` steps) is comparable over time.
- **21 steps ≈ 2.4 epochs ≈ 1,344 episodes ≈ 5 h** (~14 min/step, dominated by the 64 parallel
  rollouts + search I/O, not the gradient).
- **Collapse in these units**: v2 died at step 10–15 = after ~10 policy updates, barely one pass
  over the data. RL failure is fast — hence save every 3 steps + best-by-val selection
  (keep-last-2 at this cadence deleted the only good checkpoint).
- **vs SFT**: an SFT epoch is one pass over a fixed curated dataset, no generation in the loop;
  a GRPO step pays for 64 fresh scored episodes before it can update once.

## 11. One-breath spoken summaries

**"How did you generate and filter the SFT data?"**
> "Teacher distillation plus self-distillation, then aggressive filtering. GPT-5.4 ran the task with
> a system prompt that explicitly demanded the enumerate-then-loop pattern, four samples per
> prompt. Then every trajectory passed through behavioral gates — converged, no loops, under 20%
> tool-error rate — plus an item-F1 floor of 0.5 and a pattern check on the actual code, and I kept
> the top two per instance ranked by correctness then efficiency. The point of the F1 floor: SFT
> copies everything in the data, including mistakes — so you curate correctness in, you don't hope
> RL fixes it later. Final detail: assistant-only loss masks computed by incremental prefix
> rendering, so the model learns to emit exactly the tool-call format the serving parser reads."

**"Walk me through your reward iterations."**
> "Three versions, config-switchable in one file. v1 was outcome-weighted and stable but had a dead
> efficiency term and too little coverage weight — no F1 gain. v2 activated a turn penalty to force
> efficiency; the policy hacked it — one search, stop, no table — and collapsed into a zero-gradient
> absorbing state by step 15. v3 kept v2's coverage weight, deleted the turn cost entirely, and
> added a hard −0.1 floor for producing no table, so finishing strictly dominates giving up. KL
> 0.005 anchored to the new SFT. That run was stable for all 21 steps and gave +9% F1 at −14% cost —
> and the efficiency came back on its own, without any term asking for it."
