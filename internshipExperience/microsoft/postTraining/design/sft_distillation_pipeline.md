# Design: SFT Cold-Start Distillation → GRPO

**Status:** proposed · **Date:** 2026-07-06
**Goal:** bootstrap Qwen2.5-7B-Instruct to *complete* WideSearch code-act
trajectories (drive the tool loop + write valid Python), then sharpen with RL.

---

## 1. Motivation (why SFT before RL)

RL can only sharpen skills the base already exhibits at nonzero rate. Measured:

| Model (ws_en_028) | Drives loop | Output | f1_row | f1_item | score |
|---|---|---|---|---|---|
| Qwen2.5-7B-Instruct | yes, but buggy code | ❌ none | 0.0 | 0.0 | 0.0 |
| gpt-4.1 (teacher) | ✅ completes, ~5 turns | ✅ table | 0.20 | 0.64 | 0.0 |

The 7B never completes (buggy Python: unterminated strings, apostrophe-in-single-
quote, then narrates and stops). With ~0 successful trajectories, pure GRPO has no
gradient signal. **A small SFT cold-start on teacher trajectories teaches the two
missing skills — loop-driving + valid code — so RL has something to sharpen.** This
is the DeepSeek-R1 / STaR / ReST recipe. Teacher-distilled data is model-generated,
not hand-labeled, so it stays within the "no manual labels" spirit.

---

## 2. Teacher choice

- **Primary: gpt-5.4** (available on Azure). Doc baseline: f1_row ≈ 0.518 — the
  strongest completing trajectories → best cold-start data.
- **Fallback: gpt-4.1** (verified: completes, f1_item 0.64). Use if gpt-5.4 quota/
  latency is a problem, or to augment volume.
- Both drive the loop and emit valid tool calls — exactly the behavior to distill.

---

## 3. Data splits (no leakage)

WideSearch EN = 100 instances (+100 non-EN). Split **by query**:

| Split | ~n | Use |
|---|---|---|
| train | 60–70 | teacher distillation + later GRPO rollouts |
| val | 15 | checkpoint selection / early stop |
| test | 20 | touch once for the headline number |

Distillation uses **train only**. Never generate teacher data on val/test.

---

## 4. Trajectory collection

Run the existing harness with the teacher as reasoning+search model over the train
split, capturing the full message list:

```
.venv-harness/bin/python -m search_agent.batch_eval \
  --first_n <train_n> --stage both \
  --reasoning_model gpt-5.4 --search_model gpt-5.4 \
  --prompt_variant base --max_iterations 25 \
  --widesearch_root /home/dkidna/WideSearch \
  --output_root search_agent/batch_results/teacher_gpt54_train
```

Each instance already writes `ws_XXX/agent_trace.json` with a clean
`conversation` (verified: system → user → [assistant tool_call → tool] × N →
final assistant; `tool_call_id` linkage intact). That IS the SFT source.

Optionally sample **k>1 trajectories per instance** (temperature ~0.7) to increase
the yield of high-quality, diverse trajectories (rejection sampling).

---

## 5. Filtering / rejection sampling

Keep a trajectory only if ALL hold:
1. **Completed** — produced an `output/*.csv` (or extractable table) and ended with
   a final text answer (not a truncated/iteration-limit stop).
2. **Quality gate** — `f1_by_row ≥ τ` (start τ≈0.3; for cold-start we do NOT need
   score=1.0 — we need *completing + valid-code* behavior). Tighten τ later for a
   ReST high-quality pass.
3. **No infra failure** — no `content_filter` / 429 / kernel-crash steps.
4. **Fits the student window** — total tokens (measured with the **Qwen2.5-7B
   tokenizer**) ≤ **28,672** (32k − headroom). Drop longer ones.

> §Context note: trajectory length is driven by the task + observation size, NOT
> the teacher's context capacity. Observations are already LLM-summarized JSON
> (~200–1300 tok each); ws_en_028 was only ~6.2k tokens total. Big-table cases
> (e.g. 58-row ws_en_003) may exceed 28k — those are simply excluded (the student
> couldn't run them anyway). Keep per-observation truncation on as a safety cap.

### Pilot results (measured 2026-07-06, gpt-5.4 teacher, 12 EN instances)

All 12 **completed with output**; f1_item 0.56–0.98, f1_row mean 0.32, score 0 on
all (strict gate). Token lengths 5.9k–26.4k except one at 34.7k.

| Filter | Kept | Yield |
|---|---|---|
| strict `f1_row ≥ 0.3` | 5/12 | 42% |
| loose `completed + fits 32k` | 11/12 | 92% |

- 1/12 (~8%) exceeded the 32k window → excluded (expect ~8–15% on full train set).
- The 6 that failed `f1_row ≥ 0.3` still completed with valid code + good f1_item
  (0.62–0.84) — correct *behavior*, incomplete tables.

**Refined filter decision for cold-start:** use **completed + fits window +
`f1_item ≥ 0.5`** (keeps ~all completing trajectories; all 11 here pass). Reserve
the strict `f1_row ≥ τ` gate for a later ReST high-quality pass. Rationale: cold-
start teaches loop-driving + valid code + completion; RL fixes correctness. On a
60–70 train split this yields ~55–64 usable trajectories (before k>1 sampling).

---

## 6. `thought` field — KEEP

`thought` is a **tool-call argument** (inside `tool_calls[0].function.arguments`
alongside `code`), not separate CoT/`<think>`. It costs ~50–80 tok/turn and gives
the weak model a plan-before-act scaffold. It is part of the frozen tool schema, so
keeping it makes SFT data match the serving harness exactly. **Decision: keep it.**

---

## 7. SFT data format + loss masking

Standard multi-turn agent SFT. For each kept trajectory, render the message list
with the Qwen2.5 chat template (tools included), then:

- **Loss-masked (context, no gradient):** `system`, `user`, all `tool`
  (observation) messages.
- **Loss-on (targets):** every `assistant` message — the `tool_calls`
  (`{thought, code}` serialized exactly as the template renders `<tool_call>...
  </tool_call>`) AND the final plain-text answer.

Key correctness requirements:
- Train on the **exact tokens the model must emit at inference**: the assistant
  turns rendered by the *same* chat template + hermes tool format the server uses.
  (So the model learns to output `<tool_call>{"name":...,"arguments":{...}}
  </tool_call>` natively — which also *reduces* reliance on the recovery layer.)
- Preserve `tool_call_id` linkage when re-rendering (verified present in trace).
- One training example per trajectory (full multi-turn), with an assistant-token
  loss mask. Use sample packing if throughput matters.

Emit `{messages: [...], loss_mask spec}` JSONL; a formatter converts
`agent_trace.json.conversation` → training tensors.

---

## 8. SFT training config (starting point)

- **Base:** Qwen/Qwen2.5-7B-Instruct. **Hardware:** 4×A100-80GB.
- **Method:** start with **LoRA** (rank 32–64, attn+MLP) for a fast, cheap,
  low-risk cold-start; full-param is an option if LoRA underfits.
- **Seq len:** 32768 (match serving). Gradient checkpointing on.
- **Epochs:** 1–3 over the (small) distilled set; watch val.
- **LR:** ~1e-5 (LoRA) / ~1e-6 (full); cosine, warmup 3%.
- **Framework:** TRL `SFTTrainer` or verl SFT (whichever handles the multi-turn
  tool-call template + assistant-only loss mask cleanly — verify template renders
  `<tool_call>` correctly).
- **Gate:** post-SFT, the student should **complete** ≥ most val cases and produce
  an output CSV (even at modest f1). That is the cold-start success criterion —
  not high f1.

---

## 9. Then GRPO (P3)

From the SFT checkpoint (now completes trajectories), run GRPO against the
WideSearch reward (§9 of the RL workflow doc). Reference model = the SFT checkpoint
(or the frozen instruct). The format term can be small — SFT already teaches the
tool-call format; the recovery layer remains a safety net.

---

## 10. Risks / open questions

| Risk | Mitigation |
|---|---|
| Teacher yield too low after filtering | sample k>1/instance; lower τ; add gpt-4.1 trajectories |
| Big-table trajectories exceed 28k | exclude; rely on truncation; student can't do them anyway |
| SFT overfits tiny set / loses generality | LoRA + few epochs + val early-stop; keep set diverse |
| Chat-template/tool-format mismatch train vs serve | render SFT data with the exact serving template; unit-test one example round-trips through vLLM |
| Distillation cost (Azure) | budget ~15–20 teacher calls × k × train_n; start small (e.g. 20 instances) |
| "RL-only" constraint (mentor) | data is teacher/self-generated, not hand-labeled; document as ReST-style cold-start |

---

## 11. Immediate next actions

1. Confirm **gpt-5.4** completes in-harness on 1–2 cases (like the gpt-4.1 check).
2. Small distillation run (e.g. 20 train instances, k=1) → measure yield after
   the §5 filter (how many usable trajectories, token-length distribution).
3. Build the `agent_trace.json → SFT JSONL` formatter (+ round-trip unit test
   through the Qwen chat template).
4. LoRA SFT on the distilled set; gate on val completion rate.
5. GRPO from the SFT checkpoint.
