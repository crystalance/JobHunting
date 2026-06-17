# GAIA Benchmark: BARE Copilot vs HDMAS 3-agent

> Companion note to `HDMAS_blog_outline.md`. Captures the GAIA cross-benchmark
> result (validation split, all three levels) without inlining it into the
> main article.

## TL;DR

On **GAIA validation (159 cases across L1/L2/L3)**, HDMAS 3-agent **does not
beat** a single Copilot agent. Accuracy is essentially tied (72.3% vs 73.6%),
but HDMAS pays **1.7-3.4× wall-time** and **3.6-6.1× tool-calls**. This is the
expected outcome from §4.4's "centralized-friendly regime" criteria, and we
record it as a *negative* result that complements the WideSearch wins.

## 1. Setup

- **Benchmark**: GAIA (`gaia-benchmark/GAIA`, config `2023_all`), validation
  split, all answers known.
- **Scorer**: official GAIA exact-match after normalization (numbers strip
  `$`/`%`/comma; strings lowercase + strip punct; lists element-wise),
  implemented in `COPILOT_FOR_Widesearch/run.py::gaia_scorer`.
- **Answer protocol**: `FINAL ANSWER: <value>` line, extracted by
  `gaia_extract_final_answer`.
- **Model**: `gpt-5.4` for both systems (single shared backend through the
  Copilot SDK).
- **Runs**: BARE = `COPILOT_FOR_Widesearch/run.py --benchmark gaia` (single
  Copilot session, no orchestration); HDMAS 3a =
  `HDMAS_COPILOT/orchestrator.py` with `n_agents=3` and a GAIA-shaped
  blackboard prompt.
- **Picker fix**: An earlier BARE run on L1 selected interim status messages
  instead of the final answer (`max(messages, key=len)` bug); fixed in
  `_pick_final_message` and replayed offline via
  `COPILOT_FOR_Widesearch/repick_from_events.py`. All numbers below are
  post-fix.

## 2. Accuracy (Avg@1)

| Level | n   | BARE        | HDMAS 3a    | Δ        |
|------:|----:|------------:|------------:|---------:|
| L1    | 49  | 39 (79.6%)  | 39 (79.6%)  |  0.0     |
| L2    | 85  | 65 (76.5%)  | 63 (74.1%)  | −2.4     |
| L3    | 25  | 13 (52.0%)  | 13 (52.0%)  |  0.0     |
| **All** | **159** | **117 (73.6%)** | **115 (72.3%)** | **−1.3** |

Per-case crosstab:

| Level | both right | both wrong | BARE-only | HDMAS-only |
|------:|-----------:|-----------:|----------:|-----------:|
| L1    | 36         | 7          | 3         | 3          |
| L2    | 56         | 13         | 9         | 7          |
| L3    | 10         | 9          | 3         | 3          |
| **All** | **102**  | **29**     | **15**    | **13**     |

The dominant outcome is "both right" (102/159 = 64%); the BARE-only and
HDMAS-only buckets are roughly symmetric (15 vs 13) — within noise on n=159.

## 3. Cost

Wall-time and tool-call totals per level:

| Level | n   | system | wall-clock | mean / case | total tool-calls | calls / case |
|------:|----:|:-------|-----------:|------------:|-----------------:|-------------:|
| L1    | 49  | BARE   |   117 min  |   143 s     |  1,273           |  26.0        |
| L1    | 49  | HDMAS  |   396 min  |   485 s     |  7,805           | 159.3        |
| L2    | 85  | BARE   |   303 min  |   214 s     |  3,301           |  38.8        |
| L2    | 85  | HDMAS  |   772 min  |   545 s     | 14,852           | 174.7        |
| L3    | 25  | BARE   |   193 min  |   463 s     |  1,998           |  79.9        |
| L3    | 25  | HDMAS  |   324 min  |   777 s     |  7,163           | 286.5        |

HDMAS overhead vs BARE:

| Level | wall-time | tool-calls |
|------:|----------:|-----------:|
| L1    | ×3.39     | ×6.13      |
| L2    | ×2.55     | ×4.50      |
| L3    | ×1.68     | ×3.59      |

L3 is the cheapest ratio because BARE itself spends a lot of wall-clock
exploring deep tool chains, so the relative HDMAS overhead shrinks; the
absolute multiplier on tool-calls (×3.6) is still substantial.

## 4. Why HDMAS doesn't help on GAIA — matches §4.4 prediction

§4.4 listed centralized-friendly conditions:

1. *Strong task-graph dependencies — workers must serialize anyway.*
   GAIA queries are typically deeply sequential: locate the canonical source
   → open the right page/PDF → extract the cell → do arithmetic. A planner
   (or single agent) just has to walk the chain.
2. *Termination is naturally signalled by artifact structure, not coverage.*
   Each GAIA item has one ground-truth string. There is no "list of cells to
   fill"; the run ends when the agent commits a `FINAL ANSWER:`.
3. *N small enough that lock contention isn't a concern.* Trivially true —
   only one cell to write.
4. *Workers don't need different roles.* Trivially true again, but symmetry
   buys nothing because the work cannot be meaningfully partitioned.

GAIA satisfies all four. HDMAS therefore pays the coordination overhead
(claim/lock/release per iteration, redundant re-derivation by every peer)
without gaining any of the failure-containment / late-evidence benefits that
showed up on WideSearch.

## 5. Confirms the architectural framing

Read together with §3 (WideSearch), the two benchmarks bracket the regime:

| benchmark         | task shape                       | HDMAS vs single |
|:------------------|:---------------------------------|:----------------|
| WideSearch (EN+ZH)| wide × shallow, per-item cover.  | **wins** SR + Item-F1 |
| GAIA (val L1-L3)  | narrow × deep, single artifact   | **ties / loses**, costs more |

This is exactly the "where HDMAS does *not* win" boundary that §4.4 names.
The negative result is useful: it lets readers calibrate when to reach for a
flat blackboard team and when to stay with a single agent.

## 6. Caveats

- **Avg@1 single seed** for both systems. Some of the BARE-only / HDMAS-only
  flips would likely re-shuffle under Avg@4.
- **`gpt-5.4` reasoning model** does very well alone on GAIA L1/L2; older or
  weaker models might leave more room for HDMAS to recover failed runs.
- **Tool-call totals are not LLM token totals.** HDMAS calls cheaper tools
  more often (filesystem + lock) than BARE; the actual $ ratio will differ.
  A real $/correct comparison is on the experiments list in
  `HDMAS_review_and_next_steps.md` (Experiment D).
- **GAIA attachment routing** failed on 2 cases for both systems (image /
  Excel attachments not piped through), counted as failures for both.

## 7. Reproducing

```powershell
# BARE
python COPILOT_FOR_Widesearch\run.py --benchmark gaia --split validation --level 1 `
    --output_root COPILOT_FOR_Widesearch\results\gaia_bare_val_level1 --resume
# (repeat for --level 2, --level 3)

# HDMAS 3a
python HDMAS_COPILOT\__main__.py --benchmark gaia --level 1 --n_agents 3 `
    --output_root HDMAS_COPILOT\gaia_benchmark_results\val_level1_3agents

# Re-pick BARE answers if events were captured before the picker fix
python COPILOT_FOR_Widesearch\repick_from_events.py `
    --results-dir COPILOT_FOR_Widesearch\results\gaia_bare_val_level1
```

Aggregated comparison: see `summary.json` in each output directory; the
helper PowerShell snippets used to produce the tables above are reproduced
in this folder's git history.
