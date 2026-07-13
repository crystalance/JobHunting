# GRPO Training Pipeline — Design

**Date:** 2026-07-09
**Status:** Design (implementation pending)
**Target stack:** conda env `verl-multiturn-rollout` (verl 0.7.0.dev0 + sglang 0.5.5.post3 + torch 2.8, FSDP, 4×A100-80GB). No upgrade needed — 0.7 already has multi-turn tool GRPO.
**Init policy:** the SFT cold-start `post_training/sft/ckpt_train_v2` (val F1_item 0.345 / F1_row 0.176, 14/14 output, 0 timeouts).
**Related:** `sft_data_generation_rejection_sampling.md`, `../Learning/progress/progress_phase2.html`.

---

## 0. Objective & why GRPO now

Optimize the policy directly against the **WideSearch reward** (gold-verified F1)
via on-policy RL. The SFT model reliably drives the code-act loop and always
produces output, but row-level correctness is still low (F1_row 0.18). RL is the
right tool: it self-generates unlimited on-policy data and optimizes the actual
metric. The reward is now **non-sparse** (10/14 val instances have F1_row > 0),
so GRPO has a gradient to climb — the blocker that ruled it out earlier is gone.

**Algorithm = GRPO** (no critic): for each prompt, sample a group of G rollouts,
reward each, advantage = group-normalized reward, policy-gradient update with a
KL penalty to the SFT reference. Chosen over PPO because it needs no value model
(cheaper on 4 GPUs) and suits verifiable outcome rewards.

---

## 1. Architecture: who does what

```
             ┌─────────────────────────── verl (trainer / orchestrator) ───────────────────────────┐
 prompts ──▶ │  for each prompt: request G rollouts                                                  │
 (parquet)   │      ▼                                                                                 │
             │   sglang rollout engine  ──generate──▶ <tool_call>execute_python{thought,code}</...>  │
             │      ▲                                    │                                            │
             │      │  resume w/ tool result             ▼                                            │
             │      └──────────────  ExecutePythonTool.execute(code)  (OUR tool)                     │
             │                          → IPython kernel runs code → search_client.search (gpt-4.1-mini)│
             │                          → returns stdout / result                                     │
             │   ...loop until final answer or max_turns...                                           │
             │      ▼                                                                                 │
             │   reward_fn(final output CSV, gold[instance]) = WideSearch F1 + shaping                │
             │      ▼                                                                                 │
             │   GRPO: advantage = (R − mean_group)/std_group ; policy-grad + KL(actor‖SFT-ref)       │
             │      ▼   FSDP update actor  ──weights sync──▶ sglang                                    │
             └────────────────────────────────────────────────────────────────────────────────────────┘
```

- **sglang** = rollout generator; pauses on tool calls, resumes with results; weights re-synced from actor each step (on-policy).
- **ExecutePythonTool** (ours) = the "hands": wraps our existing `PythonExecutor` (IPython kernel) + injected `search_client` (Bing + gpt-4.1-mini). This is the RL-side reimplementation of the harness's kernel.
- **reward_fn** (ours) = gold-verified WideSearch F1 + shaping.
- **verl** = GRPO math, FSDP training, KL, checkpointing.

---

## 2. Components to build

### 2.1 `ExecutePythonTool` (subclass `verl.tools.base_tool.BaseTool`)
Template: `verl/tools/sandbox_fusion_tools.py`. Interface:
- `__init__(config, tool_schema)` — declare the OpenAI function schema for
  `execute_python(thought: str, code: str)` (identical to the harness tool).
- `create(instance_id, **kwargs)` — spin up a **fresh `PythonExecutor`** (own
  IPython kernel + session dir) and inject `search_client` built from
  `kwargs` (search_model=gpt-4.1-mini, budget env). One kernel per rollout.
- `execute(instance_id, parameters)` — run `parameters["code"]` in that kernel;
  return `(ToolResponse(text=formatted_stdout), step_reward=0.0, metrics)`.
  Reuse `_format_exec_result` + the hardening (per-cell + episode search cap,
  kernel-death guard, stdout bound) already in the harness.
- `calc_reward` — unused (reward is outcome-level, §3); return 0.
- `release(instance_id)` — shut the kernel, free the session dir.

**Reuse, don't rewrite:** import `PythonExecutor`, `BingGroundingSearchClient`,
`_format_exec_result`, `safe_json_parse` from the existing harness so the RL
environment is byte-identical to what SFT/eval used.

Per-trajectory config is passed via the parquet's `tools_kwargs` (workspace
path, instance_id, search settings).

### 2.2 Reward function (custom `compute_score`)
File `post_training/grpo/widesearch_reward.py`, signature per verl:
`compute_score(data_source, solution_str, ground_truth, extra_info) -> float`.

- `extra_info` carries `instance_id` (+ workspace path). Reward reads the
  produced output file from the rollout workspace (or the CSV embedded in
  `solution_str` via the harness's `_build_response_text`) and scores it with
  the **WideSearch evaluator** against the gold for `instance_id` (reuse
  `evaluate_single_query`, patched Azure judge — same as `score_trajectories.py`).
- **Reward formula (outcome, at episode end):**

  ```
  R =  w_item * f1_item          # dense partial credit (main signal)
     + w_row  * f1_row           # row-level correctness (the real target)
     + w_out  * 1[output_file_valid]
     - w_cost * min(n_searches / BUDGET, 1)      # efficiency / anti-over-search
     - w_fab  * 1[constant_fill_detected]         # weak anti-fabrication nudge
  ```
  Start: `w_item=1.0, w_row=0.5, w_out=0.1, w_cost=0.1, w_fab=0.1`.
  Rationale: `f1_item` is dense (learns early); `f1_row` pulls toward full
  correctness; the cost term trims the residual over-search; fabrication is
  mostly punished implicitly (fabricated rows tank F1). Keep R roughly in
  [−0.3, 1.6]; GRPO normalizes per group anyway.
- **Reward hacking watch:** `f1_item` can be inflated by `nan`-matching. The
  `w_row` term + monitoring mean f1_row (not just f1_item) guards against a
  policy that learns to emit empty/`nan` tables. If it games, raise `w_row`.
- Reward manager = `naive` (assigns outcome reward to the last token). Consider
  `launch_reward_fn_async=true` since scoring calls the Azure judge (slow).

### 2.3 Data (parquet)
`post_training/grpo/data/train.parquet` (+ val.parquet). One row per **prompt**
(train `ws_en_001–070`; RL reuses prompts many times):
- `prompt`: chat messages = [system = frozen SFT `_SYSTEM_PROMPT`, user = the
  WideSearch task] (verl applies the chat template).
- `data_source`: `"widesearch"` (routes to our reward).
- `reward_model.ground_truth`: `instance_id` (reward loads gold from WideSearch).
- `extra_info`: `{instance_id, need_tools_kwargs:true, tools_kwargs:{execute_python:{create_kwargs:{...workspace, search_model, budget...}}}}`.
- `agent_name`: `tool_agent` (multi-turn tool loop).

Build with a small script that pulls the 70 train queries via the existing
`load_widesearch_queries` and writes the parquet.

### 2.4 Actor init from the SFT checkpoint
`ckpt_train_v2` is a **LoRA adapter**. Two options:
- **(A) Merge → full-param actor** (recommended for a clean first run): merge the
  LoRA into Qwen2.5-7B-Instruct → a full HF checkpoint; `model.path` points to it;
  train full-param with **FSDP2** across 4 GPUs.
- **(B) verl LoRA RL** (memory-saver): keep LoRA, use verl's `ppo_lora` path.
  Lower memory but more moving parts. Defer to (B) only if (A) OOMs.
The **reference model** for KL = the same merged SFT model (frozen).

### 2.5 Run config (verl `main_ppo`, Hydra overrides)
Key settings (bash launcher `post_training/grpo/run_grpo.sh`):
```
algorithm.adv_estimator=grpo
data.train_files=.../train.parquet  data.val_files=.../val.parquet
data.max_prompt_length=2048  data.max_response_length=28672   # long agentic traj
actor_rollout_ref.model.path=<merged SFT>
actor_rollout_ref.actor.strategy=fsdp2  actor_rollout_ref.ref.strategy=fsdp2
actor_rollout_ref.rollout.name=sglang
actor_rollout_ref.rollout.multi_turn.enable=true
actor_rollout_ref.rollout.multi_turn.max_turns=25
actor_rollout_ref.rollout.multi_turn.tool_config_path=.../tools.yaml
actor_rollout_ref.rollout.n=8                 # group size G
actor_rollout_ref.rollout.gpu_memory_utilization=0.6
algorithm.kl_ctrl.kl_coef=0.001               # stay near SFT
data.train_batch_size=16                       # prompts/step (×G rollouts)
actor_rollout_ref.actor.ppo_mini_batch_size=16
actor_rollout_ref.actor.optim.lr=1e-6          # RL LR << SFT LR
custom_reward_function.path=.../widesearch_reward.py
custom_reward_function.name=compute_score
reward_model.launch_reward_fn_async=true
trainer.n_gpus_per_node=4  trainer.total_epochs=...  trainer.save_freq=...
```
`tools.yaml` registers `ExecutePythonTool` with its schema + create_kwargs.

---

## 3. The central challenge: rollout throughput & Azure cost

Each rollout runs a **real IPython kernel + real web searches** (gpt-4.1-mini),
so a rollout takes **minutes**, not milliseconds. With G=8 × batch 16 = 128
rollouts/step, each doing tens of searches, a naive setup is very slow and
Azure-expensive. Mitigations (design in from the start):

1. **Async / server-based rollout** — verl overlaps training with slow tool
   calls (`rollout.mode=async` where supported); essential here.
2. **Search cache** — dedup identical `(instance_id, query)` across the G
   rollouts of a prompt and across steps (an on-disk/Redis cache keyed by query
   hash). Same prompt's group asks near-identical queries → big hit rate.
3. **Hard episode budget** — reuse `SEARCH_EPISODE_BUDGET` (already built) to cap
   searches/rollout (e.g. 60) → bounds time, context, and cost.
4. **Small batch + grad-accum + more steps** — fewer concurrent rollouts.
5. **max_turns cap** (25) and **max_response_length** to bound trajectory length.
6. **Throttle** search concurrency (`SEARCH_MAX_WORKERS`) to respect Azure limits;
   AOAIClient backoff handles 429s.

Budget/throughput is the #1 risk — validate it on a tiny run before scaling.

---

## 4. Bring-up plan (de-risk incrementally)

| Step | Goal | Success criterion |
|------|------|-------------------|
| 0 | **Smoke-test sglang multi-turn** in the 0.7 env with Qwen2.5 + the built-in gsm8k tool | model emits tool calls, sglang parses hermes, loop runs |
| 1 | Implement `ExecutePythonTool`; unit-test `create/execute/release` standalone | code runs in kernel, search works, kernel released |
| 2 | Implement `widesearch_reward.compute_score`; run on 5 saved SFT trajectories | reproduces `score_trajectories.py` F1 within tol |
| 3 | Build `train.parquet` / `val.parquet` (70 / 14 prompts) | loads in verl data module |
| 4 | Merge SFT LoRA → actor init; **tiny GRPO run** (2 prompts, G=4, 2 steps) | end-to-end loop completes; reward logged; no crash |
| 5 | Scale (batch 16, G=8); add search cache + async rollout | throughput acceptable; reward/KL curves sane |
| 6 | Periodic eval on val (071–085); pick best ckpt | val F1 rises above SFT 0.345 |
| 7 | Final eval on untouched **test 086–100** | report vs SFT baseline |

---

## 5. What to monitor
- **mean reward**, **mean f1_row** and **mean f1_item** separately (catch
  f1_item-only gaming), **output-rate**, **mean n_searches / n_turns** (should
  fall as efficiency improves), **KL(actor‖ref)** (stay bounded), response
  length, reward std within group (GRPO needs variance — if all rollouts of a
  prompt get equal reward, no signal).
- **Entropy / collapse**: watch for the policy degenerating (repetitive code);
  KL + moderate LR guard against it.

## 6. Key risks & mitigations
| Risk | Mitigation |
|------|-----------|
| Rollout too slow / Azure cost | async rollout + search cache + episode budget + small batch (§3) |
| sglang can't parse Qwen2.5 tool calls | validate in Step 0; fall back to a content-`<tool_call>` parser if needed |
| Reward hacking (nan/fabrication inflates f1_item) | `w_row` term + monitor f1_row + constant-fill penalty |
| Context length (28k)×G OOM | max_turns cap, gpu_mem_util tuning, FSDP2 offload, grad-accum |
| Few train prompts (70) → overfit | reuse SFT rejection-sampling insight; optionally add ZH prompts for diversity |
| LoRA-merge init mismatch | verify merged model reproduces SFT val numbers before RL |
| Losing the working env | never pip-upgrade in place; clone env if changes needed |

## 7. Deliverables (files to create)
- `post_training/grpo/execute_python_tool.py` — the verl tool.
- `post_training/grpo/widesearch_reward.py` — the reward function.
- `post_training/grpo/tools.yaml` — tool registration/config.
- `post_training/grpo/build_grpo_parquet.py` — prompt→parquet.
- `post_training/grpo/merge_sft_lora.py` — LoRA→full actor init.
- `post_training/grpo/run_grpo.sh` — verl launcher with the overrides in §2.5.
