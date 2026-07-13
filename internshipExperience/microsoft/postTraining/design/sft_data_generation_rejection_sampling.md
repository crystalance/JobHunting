# SFT Data Generation & Selection — Rejection-Sampling Design

**Date:** 2026-07-07
**Status:** Design (to implement after the fixed-prompt val re-run)
**Related:** `sft_distillation_pipeline.md` (v1 pilot pipeline), `../Learning/progress/post_training_progress.html`

---

## 0. What SFT is (and is NOT) for here

> **SFT goal (this project):** teach the student the **correct code-act pattern** —
> drive the tool loop, write **valid code that runs without crashing**, and
> **always produce an output file to grade on**. Getting every cell *correct* is
> **NOT** the SFT objective; that is what the later GRPO/RL stage optimizes.

This reframes the data-selection bar. We do **not** filter for high `F1_row`.
We filter for **behavioral quality**: completion, clean execution, honest
(non-fabricated) output, and convergence. A trajectory that cleanly gathers
what it can, writes `nan` for the rest, and stops is a **great** SFT example
even if its F1 is mediocre. A trajectory that scores high but loops on errors
for 20 turns is a **poor** SFT example.

### Why (evidence from the weak first cold-start)
The 48-trajectory LoRA scored val `F1_item ≈ 0.05`, and inspection showed the
student learned the *scaffold* but not clean behavior. The three failure modes
we must train **against**:
1. **Fabrication** — when extraction fails, it invents/repeats fake rows (`ws_en_071`).
2. **Non-convergence** — searches 25 turns, never writes output (`ws_en_072`).
3. **Broken code / loops** — repeats the same failing cell ~20× (`ws_en_073`, base model).

So the training set must densely demonstrate the **opposite**: clean code, honest
`nan`, write-early, stop.

---

## 1. Core method: Rejection-Sampling Fine-Tuning (ReST / RFT)

The benchmark prompts are fixed, so we multiply **trajectories per prompt**, not
prompts: sample many teacher rollouts, keep the ones that pass a **behavioral**
quality filter.

```
for each train prompt:
    sample k rollouts from teacher @ temperature   # diversity
    score + inspect each rollout
    keep the top 2-3 that pass the behavioral filter
→ build_sft_data → retrain LoRA → re-eval on val
```

---

## 2. Prompt pool (never contaminate eval)

| Split | Instances | Use |
|-------|-----------|-----|
| **Train** | `ws_en_001–070` (70) | SFT data generation |
| Val | `ws_en_071–085` (excl. 079) | held out — never distilled |
| Test | `ws_en_086–100` | held out — never distilled |
| **ZH (optional phase 2)** | `ws_zh_001–100` (100) | untouched; adds prompts to teach language-agnostic code-act skill (eval is EN-only ⇒ low contamination risk) |

---

## 3. Generation: k samples per prompt at temperature

- **Teacher:** `gpt-5.4` only (strongest; F1 1.0 on ws_en_028). Do **not** mix in
  the weaker `gpt-4.1` (0.2/0.64) — a weak teacher injects the very noise
  (fabrication, sloppy code) we are trying to filter out.
- **k = 4–8** rollouts per prompt, **temperature ≈ 0.7** for strategy diversity
  (greedy gives one path; sampling surfaces cleaner/shorter successful paths).
- **Search:** `gpt-4.1-mini` summarizer (unchanged, per project constraint),
  throttled via `SEARCH_MAX_WORKERS`.
- **Prompt used for generation = the fixed base prompt** (with the 2026-07-07
  anti-fabrication / write-early / search-budget additions) so the teacher
  demonstrates exactly the behavior we want, and the student sees a consistent
  system prompt at train and inference time.

---

## 4. Selection filter — BEHAVIORAL, not F1-maximizing

Score every rollout with the WideSearch evaluator **and** compute cheap
behavioral stats from its trace. Apply in order:

### 4a. Hard gates (mandatory — reject if any fail)
- **Produced an output file** and returned a final answer (must be gradeable).
- **No crash / no timeout** (ran to a clean finish).
- **Fits the context window** (≤ ~28,672 tokens) so it trains without truncation.
- **Valid tool-call structure** on every assistant turn.

### 4b. Code-quality gates (the heart of this SFT goal)
- **Low execution-error rate:** fraction of tool cells that returned `[error]`
  below a threshold (e.g. **≤ 20%**). Rejects the "broken code" mode.
- **No pathological loop:** never resubmits a near-identical cell that fails the
  same way more than twice (detect by hashing failing code cells). Rejects the
  20×-loop mode.
- **Converged:** wrote output and **stopped** (final turn is a text answer, not a
  forced iteration-limit cutoff). Prefer trajectories with a **reasonable turn
  count** (e.g. ≤ 15 turns) and **bounded searches** (≤ ~60). Rejects the
  "never stops" mode.

### 4c. Anti-fabrication gate (honesty, not accuracy)
- **Modest correctness floor:** require a *low* bar such as **`F1_item ≥ 0.3`**
  — high enough that the answer is real (you cannot fabricate your way to 0.3
  against the gold judge across a table), low enough that we keep honest
  partial answers. **Do NOT require high `F1_row`** — that would over-select and
  contradict the SFT goal.
- **No constant-fill:** reject trajectories whose output repeats the identical
  non-`nan` value across many rows (the `ws_en_071` fabrication signature).
- `nan` cells are **fine** and expected — honest `nan` is a feature to teach.

### 4d. Diversity / balancing
- **Per-prompt cap:** keep the **top 2–3** distinct passers per prompt (dedup by
  output similarity) so easy prompts don't dominate.
- **Keep all passers for hard prompts** — clean trajectories on hard prompts are
  rare and the most valuable.
- **Ranking within a prompt:** among passers, prefer *fewer errors → fewer turns
  → higher F1_item* (in that priority order — behavior first, score last).

### 4e. Filter architecture — verifier gates + our own LLM judge on top
The filter is **hybrid**. The hard signals are verifier/deterministic (reliable
and cheap because we have gold labels); a **self-implemented LLM judge** is added
as a **final top layer** to catch behavioral/imitation-quality issues the
verifier cannot see.

- **Pure code (no LLM):** all hard gates (4a); all code-quality gates (4b —
  error-rate, loop detection, convergence, turn/search counts from the trace);
  the constant-fill / fabrication-signature check (4c); diversity (4d).
- **Verifier LLM (already in the loop):** the WideSearch evaluator we run to get
  F1 — `exact_match` for most columns + a `gpt-4.1 llm_judge` for free-text
  columns, scored **against gold**. This is the correctness / anti-fabrication
  *hard* signal.
- **Our own LLM judge (new — §4f):** an **offline** trajectory-quality judge run
  **only on trajectories that already passed 4a–4d**, scoring imitation-worthiness
  (clean code-act, sound reasoning, honest derivation, convergence). Applied as a
  final cheap top-layer filter — "won't hurt, can only raise quality."

> NOTE — this is NOT `search_agent/critic_agent.py`. That is an *in-loop runtime*
> critic that judges a single run's OUTPUT (coverage/schema/blank cells) and
> emits TODOs to nudge the SearchAgent mid-task. We need an *offline* judge of
> the whole TRAJECTORY for training-data selection — a different job — so we
> implement our own (§4f).

Why layered this way: with ground truth available, verification is the reliable
correctness signal (LLM-judge-only filtering is for when you *lack* gold). But
our SFT goal is **behavioral**, and correctness ≠ imitation-worthiness — so an
LLM judge adds real value on the dimensions the verifier is blind to.

### 4f. The offline trajectory-quality LLM judge (our implementation)

**Role:** a final, ablatable filter layered on top of the passing set. It does
not generate or fix anything — it reads a finished trajectory and returns a
structured quality verdict. Turning it on can only shrink/clean the set, never
enlarge it, so it is low-risk ("won't hurt much").

**Judge model:** `gpt-4.1` (strong, cheaper than gpt-5.4; the search-model
constraint does not apply — this is an offline data-tooling component, not the
agent's search summarizer). Temperature 0 for determinism.

**Input (compact trajectory rendering, NOT raw dumps):** to keep tokens small
and cost low, feed the judge:
- the task query;
- for each turn: the `thought` + the `code` cell + a **truncated** outcome tag
  (`ok` / first line of stdout / error name) — *not* the full search-result
  blobs;
- the final answer + the produced output-file head (first ~30 rows);
- the verifier score (F1_row / F1_item) as a hint.

**Rubric (each scored 1–5, with a one-line justification citing a turn):**
1. **Code-act protocol** — uses `execute_python` correctly every turn; never
   narrates code instead of calling the tool.
2. **Code quality** — idiomatic, minimal, no repeated/near-duplicate cells, no
   thrashing; extracts values sensibly.
3. **Reasoning soundness** — `thought`s are coherent and the plan is sensible
   (search → read → write → verify → stop).
4. **Honesty / no fabrication** — output values are traceable to search results;
   `nan` used where not found; no invented or constant-filled rows.
5. **Convergence / efficiency** — searches then writes and stops; no aimless
   wandering or budget-blowing.
6. **Imitation-worthiness (overall)** — "would a student that copies this
   trajectory acquire good habits?"

**Output schema (strict JSON):**
```json
{
  "scores": {"protocol":5,"code":4,"reasoning":4,"honesty":5,"convergence":3,"overall":4},
  "hard_fail": false,               // true if fabrication or protocol violation seen
  "keep": true,
  "reasons": "one-line justification per low score, citing turn numbers"
}
```

**Keep rule:** `keep = (not hard_fail) AND overall >= 4 AND honesty >= 4`.
`hard_fail` (fabrication / protocol violation) is an automatic reject regardless
of score. Thresholds are tunable after calibration.

**Cost control:** only judge the ~120–180 trajectories that already passed
4a–4d (not all 420 rollouts); compact rendering keeps each call small; batch +
throttle. Roughly one cheap gpt-4.1 call per candidate.

**Reliability / calibration (important so the judge doesn't silently gut the set):**
- Rubric-based with required per-score justification (reduces vibes).
- **Calibrate before trusting:** hand-label ~20 trajectories good/bad, measure
  judge agreement; adjust thresholds so it isn't overly harsh.
- **Ablation:** keep the judge optional (`--use_llm_judge`) and train **with and
  without** it on the first batch to measure whether it actually improves the
  student — do not assume it helps.
- Log every verdict (scores + reasons) alongside the trajectory for auditing.

**Implementation:** a small standalone module
`post_training/sft/llm_trajectory_judge.py` (reads `agent_trace.json`, renders
the compact view, calls `AOAIClient(model="gpt-4.1")`, writes a
`judge_verdict.json` per trajectory). `build_sft_data.py` gains a
`--use_llm_judge` flag that drops trajectories whose verdict has `keep=false`.

Expected yield: 70 prompts × k=6 ≈ 420 rollouts → ~40–55% pass the behavioral
gates (looser than an F1_row bar) → cap 2–3/prompt → **~130–180 trajectories**
(3–4× the current 48), densely demonstrating clean, convergent, honest behavior.

---

## 5. Pipeline & code changes

| Step | Tool | Change needed |
|------|------|---------------|
| 1. Generate k samples | `search_agent/batch_eval.py` | **ADD** `--num_samples k` + `--temperature`; loop k rollouts/instance, write `{iid}_trial{n}` traces (currently `trial_idx` is hardcoded to 0, greedy only). |
| 2. Score + behavioral stats | new small scorer | Per-trajectory: F1 (existing eval) + error-rate, loop-flag, turn/search counts, constant-fill check (from `agent_trace.json` + `search_log.json`). |
| 3. Select (verifier + deterministic) | `post_training/sft/build_sft_data.py` | Reuse; **ADD** behavioral filters (4b/4c/4d) alongside existing `--tau`/`--tau_item`. Set the F1 floor low (`--tau_item 0.3`, `--tau 0.0`). |
| 3b. LLM trajectory-quality judge (top layer) | **new** `post_training/sft/llm_trajectory_judge.py` | Offline gpt-4.1 judge (§4f) on trajectories that passed step 3; writes `judge_verdict.json`. `build_sft_data.py` gains `--use_llm_judge` to drop `keep=false`. **Ablatable.** |
| 4. Tokenize | `build_sft_data.py` | Reuse (assistant-only loss mask, ≤28k). |
| 5. Retrain | `post_training/sft/train_sft.py` | Reuse (LoRA r32). Larger set ⇒ can also revisit full-FT later. |
| 6. Re-eval | `batch_eval.py` (hardened) | Val `ws_en_071–085`; compare completion-rate, error-rate, output-rate, F1. |

**Primary success metric for the retrained model** (aligned to the SFT goal):
- **Output-produced rate** (gradeable output) → target ↑↑ (from ~64%).
- **Clean-completion rate** (no timeout/crash) → target ↑↑.
- **Mean execution-error rate per run** → target ↓.
- F1_item / F1_row → expected to rise modestly; treated as a *secondary* signal
  and the job of the subsequent GRPO stage.

---

## 6. Cost / time
`gpt-5.4` ≈ 5–7 min/rollout (reasoning). k=6 × 70 = 420 rollouts; parallelize
~4 instances with throttled search ⇒ overnight. Start with **k=4** (280
rollouts) to move faster, top up hard prompts later.

---

## 7. Later (not now): student self-sampling (STaR loop)
Once the student is competent, sample from **it** (local vLLM — cheap/fast),
keep behavioral-passers, add to the set, retrain — an on-policy self-improvement
loop that feeds naturally into GRPO. Not useful yet (student passes ~1/14).

---

## 8. Risks & fallbacks
- **Low yield on hard prompts:** if even gpt-5.4 rarely produces a *clean,
  converged* trajectory for some prompts, keep the best-behaved rollout even at
  lower F1 (behavior > score), or drop that prompt from SFT (leave it for RL).
- **Over-fitting to easy prompts:** enforced by the per-prompt cap + balancing.
- **Prompt drift:** generate with the *same* fixed base prompt the student uses
  at inference, so train/inference distributions match.
