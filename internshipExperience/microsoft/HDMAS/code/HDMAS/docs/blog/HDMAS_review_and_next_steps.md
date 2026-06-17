# HDMAS — Review, Limits, and Where to Go Next

> A reflection after the WideSearch 1a / 3a / 8a runs and the GAIA pipeline are in.
> The user's question, in their own words: *"the more agents you create, the more cost/time you need; the most ideal way is more agents = faster + better up to a limit, but the lock makes that impossible. Suggestions?"*

You've actually arrived at one of the oldest results in distributed systems — and the disappointment you feel is the right one to feel. Let me reframe what you built and where it can go.

## What you actually built (and why the ceiling is real)

HDMAS is essentially **a tuple-space architecture** (Linda, 1985) implemented with `flock()` instead of an in-memory store. The blackboard *is* a shared tuple space; your peers are workers; `vote_stop` is your termination protocol. You independently rediscovered a 40-year-old design — that's not bad, that's a sign the design is natural.

The ceiling you hit is also old. **Amdahl's law**: if any fraction `s` of the work is serialized, max speedup is `1/s` no matter how many workers you add. Your serialized fraction is the read-decide-claim window under the BB lock. Once you have N peers and each holds the lock for time `t_lock` per iteration, peers spend ≈ `N·t_lock` time waiting per round — and that's *before* answer-file contention. That's why your wall-time scales ≈linearly instead of ideally with N, and why tool calls scale super-linearly (peers retry under contention).

So your intuition is correct: **with one shared lock on one shared artifact, "more agents = faster" is mathematically impossible past a small N**. The lock is necessary for correctness, and the lock is the bottleneck. You can't have both.

## But "lock is necessary" deserves a sharper look

What the lock actually protects is *one specific invariant*: **no two peers claim the same subtask**. That's a tiny invariant. You bought it with a giant primitive — a global mutex on the *entire* coordination state plus the entire output. That's the gap to exploit.

Three escape hatches, in increasing order of departure from your current design:

### 1. Shrink the critical section (cheap, high ROI)
- **Per-row / per-section locks on `answer/`** instead of one lock on the whole answer dir. Your §3.4 multi-writer pathology disappears immediately — peers writing different rows of the table don't conflict at all.
- **Append-only blackboard with monotonic claim IDs.** If `task_log` is append-only and each peer's claim has a unique `(agent_id, seq)` key, you don't need a write lock — peers can append concurrently and a deterministic conflict resolver picks the winner on read. Reads become lock-free.
- **Lease-based claims.** Instead of "I hold this subtask forever", "I hold it for 60s, after which any peer can re-claim it." This kills the stalled-agent problem without needing `wake_agent`.

These don't change the architecture; they just stop using a sledgehammer for the invariants.

### 2. Stop pretending all peers are interchangeable (medium)
Your symmetric-peers design is theoretically beautiful but operationally wasteful: every peer re-derives the *whole* subtask list from the query on every iteration, just to claim one item. That's a lot of LLM tokens spent on redundant planning.

A small asymmetry helps: **one peer at a time holds a "planner role" for one round** (decided by lock order, not by birth), enumerates the work list once, and writes it as concrete tasks. Other peers just `take_one()`. You keep the no-permanent-leader property, you keep the no-coordinator-amplification property, but you stop paying the per-peer planning tax. This is roughly the **work-stealing scheduler** model (Cilk, Go's `go` runtime) and it's how real parallel systems get linear speedup.

### 3. Accept that the answer-write phase is fundamentally different (the right insight)
Your benchmarks revealed something specific: **retrieval parallelizes well, assembly doesn't**. The honest fix is to architect for that asymmetry instead of fighting it:

- **Map phase**: N peers in parallel, fully independent, each writes evidence into `evidence/{peer_id}/row_{k}.json` with no shared state at all. No locks needed.
- **Reduce phase**: *one* peer (or one deterministic merge step) reads all `evidence/*/row_*.json` and assembles the final table. No contention, no overwrite, no drift.

This is just MapReduce. It maps perfectly onto your workload. It would eliminate your SR regression at 8a and almost certainly raise SR above 3a's number, at the same wall-time cost. The decentralized claim protocol stays for the map phase; the contended commit step gets its own short serialized phase.

## What I think you should take away

1. **Your honest contribution isn't "more agents = better".** It's "*for wide, weakly-coupled retrieval workloads, a shared blackboard with OS locks beats a planner-coordinator at small N — and the failure mode at large N is the answer-commit step, not the coordination layer*". That's a sharp, defensible, novel-enough claim. Don't try to claim what you can't prove.

2. **The "scale to many agents" goal is the wrong goal for this architecture.** It was always going to hit Amdahl. The right goal is *minimum-coordination-surface multi-agent for tasks where centralized planners amplify failures* — and at that, even N=3 is enough to demonstrate the point against a leaderboard of N≥5 centralized systems.

3. **If you want to keep the scaling story alive, the next iteration is structural** (map/reduce phases, per-section locks, append-only BB), not "tune N". Adding peers to the current architecture has hit its ceiling — your data already shows that, and no amount of prompt engineering will move it.

4. **The Linda / tuple-space / blackboard literature is your friend.** Citing it (Gelernter 1985; Carriero & Gelernter 1989; Engelmore & Morgan's *Blackboard Systems* 1988) instantly grounds the work and tells reviewers you know which problem you're solving and which you've inherited.

## Concrete next-step recommendation

If it were my project, I would:
- ship the current paper with the honest "decentralization wins on per-item-coverage tasks at small N; contention dominates past that" framing (which is what §4 now says — good),
- and run **one more experiment**: implement map/reduce for the answer-write phase only and report 3a / 8a / 16a numbers. If 16a-with-MR beats 3a on SR, you've turned the §4 limitation into a §5 contribution. If it doesn't, you've proven decentralization itself caps out, which is also publishable.

The disappointment you're feeling is the *productive* kind. You've found the wall; now the question is whether to argue the wall is interesting (paper as-is) or to climb it (one more iteration). Both are valid; pick based on time budget.

---

# Round 2 — "If small-N wins go to asymmetric MAS and large-N adds cost, what is HDMAS *for*?"

> Follow-up: *"If small N works fine for asymmetric agents anyway, and large N from HDMAS only gives marginally better results at much greater cost, and planner-worker can also scale — how do I prove HDMAS has value? My intuition is it shines in unstable environments where info has to flow seamlessly across peers and failures don't get amplified."*

You're not worthless, but you're not yet *proven* either. Let me separate the strong claims from the weak ones honestly, then give you a path to prove it.

## Audit of the five "decentralization wins" claims (originally §4.7)

### ✅ Strong (defensible, hard for centralized to replicate)

**Claim 1 — Failure containment.** A planner mis-decomposes → all N workers eat the mistake. A peer mis-claims → only one peer's iteration is wasted, and the next peer corrects it. This is a *correctness* property and doesn't degrade with scale. **This is publishable on its own** if you demonstrate it: inject controlled planner failures into a planner-worker baseline and show HDMAS recovers while the baseline doesn't.

**Claim 4 — Late-arriving evidence is absorbed for free.** A peer that discovers source `k′` mid-execution just appends a claim on its next iteration — no replanning round-trip because there is no plan to replan. Demonstrable: design queries where the right source is only discoverable from inside another source. Planner-worker systematically misses those without expensive replans.

### ⚠️ Real but not unique

**Claim 2 — No single critical path through one model's context.** True, but hierarchical / recursive planning gets most of this. Your version is *cleaner*, not exclusive.

**Claim 3 — Dispatch is `flock()`, not an LLM call.** True for HDMAS, also true for any work-queue MAS (Celery, Ray). You'd need to isolate measured token savings on dispatch specifically; current data doesn't.

### ❌ Weak — your own data refutes it

**Claim 5 — "Scaling is just spawning processes."** Your 3a → 8a numbers (×2 wall-time, ×2.7 tool calls, SR regression) say the opposite. Drop this claim — readers will read §3.4 and call it out.

## The "high-unstable-environment" intuition is the right axis

Reframe the whole pitch around it:

> **HDMAS is not a faster MAS. It is a MAS that degrades gracefully under conditions where planner-worker systems fail catastrophically.**

HDMAS dominates planner-worker in regimes where:

1. **Individual peer failures are common** (timeouts, hallucinated stops, partial answers). Containment > throughput.
2. **The task graph is not knowable up front.** Planner has to re-plan; HDMAS just claims new work.
3. **The failure metric is per-item coverage.** One missed item = one visible failure → planner-mistake amplification is fatal.
4. **Worker pools are heterogeneous or unreliable.** Symmetric peers + idempotent claims = automatic failover.

WideSearch happens to be in this regime, which is why you got the 2.45× SR lift over the leaderboard MA in the first place — but that *isn't* the explanation you've been giving.

# Round 3 — "But planner-worker can just re-plan; what's left for HDMAS?"

> Follow-up: *"For point 2 (task graph not knowable up front), in planner-worker mode I just have the planner re-plan. What's the benefit of HDMAS then?"*

Good challenge. "Planner just re-plans" looks symmetric on the whiteboard. The hidden costs show up in three specific places HDMAS sidesteps for free.

### 1. Re-planning is a barrier; claim-and-go is not

Planner-worker re-planning is a **global synchronization point**: the planner needs all worker results before it can re-decompose. The system runs in waves: workers go → workers wait → planner thinks → workers go. **Tail latency dominates** — the slowest worker in each wave blocks everyone.

HDMAS: a peer that discovers a new source at second 47 *appends a claim at second 48* while the other 7 peers are still mid-task. No wave, no barrier, no waiting. Late-arriving evidence becomes new claimed work *in the same iteration cycle*, not in the next planner round.

### 2. The re-plan itself recreates the §1.2 pathology

Every re-plan call requires the planner to hold **the entire current state in one context**: original query + all subtasks claimed so far + all results returned + new evidence. By replan #5 on a wide-search query, the planner is back to managing 30+ subtasks in one window — *exactly the single-agent context-pressure failure you went multi-agent to avoid*.

HDMAS distributes this: each peer only sees `task_log` (claim records, not full results) and re-derives only its own next claim. No peer's context ever holds the whole accumulated state.

### 3. Re-planning is where consistency breaks

When the planner re-plans it has to decide:
- Is subtask T still in-flight or abandoned?
- Did worker W's "no results" mean "source empty" or "source unreachable"?
- The new evidence contradicts T2's earlier finding — cancel, retry, or trust the new one?

These are **distributed-consensus problems wearing a planning costume**. Every re-planner has to re-implement them, and they're easy to get wrong because there's no operational model — just whatever the planner LLM decides each call. You get *non-deterministic, non-auditable* coordination.

In HDMAS, the protocol answers these:
- In-flight vs abandoned → lease expiry on the claim record.
- Source empty vs unreachable → the peer wrote `outcome={empty|error}` into its claim before releasing the lock.
- Contradicting evidence → the next peer reads both, decides under the lock, appends a new claim with the resolution. Auditable in `task_log`.

### Honest summary

The benefit of HDMAS is that it turns three things planner-worker has to *hope the LLM does correctly* into three things the *protocol enforces*:

| Concern | Planner-worker | HDMAS |
|---|---|---|
| When to re-decompose | Hope the planner notices in its growing context | Every peer re-derives every iteration; cannot miss |
| What's in-flight vs abandoned | Hope the planner remembers across replans | Lease expiry on the claim |
| How to resolve contradictions | Hope the planner picks correctly | `task_log` append makes resolution explicit + auditable |
| Cost of one replan | Full context + planner LLM call + worker barrier | One `flock()` + one append |

Small for one re-plan. Compounds badly when re-plans are frequent — exactly the regime HDMAS claims as home turf.

## Concrete experiments to prove the value (ranked by ROI)

### Experiment A — Inject failures (1-2 days, very high payoff)
Take a centralized planner-worker baseline (write a minimal one in ~200 lines: GPT-4.1 planner emits N subtasks, N workers execute, planner merges). Run it and HDMAS on WideSearch with **failure injection**:
- Random worker dies after T seconds (10% / 30% / 50%)
- Planner forced to drop a random source from its decomposition
- Random worker returns "done" prematurely

Plot SR / Item-F1 vs failure rate for both. If the curves diverge — and they will — that's the headline figure.

### Experiment B — Hidden-source queries (3-4 days, novel finding)
Curate ~20 queries (from GAIA or hand-built) where the right answer requires a source only discoverable mid-execution. Metrics that *isolate* the late-arriving-evidence benefit:
1. **Wall-time to discovery** — HDMAS faster (no barrier).
2. **Planner-context tokens at end of run** — HDMAS doesn't have one; planner-worker's grows.
3. **Variance across N=5 reruns** — HDMAS tighter (protocol pins consensus).

If those three favor HDMAS, you've isolated defensible evidence. If they don't, the planner-just-replans rebuttal wins on this axis and you've learned something.

### Experiment C — Map/Reduce variant (1 week, fixes the scaling weakness)
Per-row locks + single-writer commit phase. Run 3a / 8a / 16a. If 16a-MR beats 3a on SR you've turned §4.6 from a limitation into a contribution. If it doesn't, you've proved the wall is in the architecture.

### Experiment D — Cost-per-correct-answer (cheap, defensive)
Reframe §4.6 from "8a costs 2× more" to **"$ / correct answer"**. If under failure injection 3a is $0.40/correct and planner-worker is $0.60/correct, you have a *strict-dominance* claim on a real metric.

## What to drop / soften in the current article

- **Drop Claim 5** ("scaling is just spawning processes"). Data refutes it.
- **Soften "we beat the leaderboard 2.45×"**. The number is real but contaminated by Avg@1-vs-Avg@4 and possible model-generation differences. Lead with *robustness*, put the leaderboard table as supporting evidence not headline.
- **Re-anchor §1 / §4** around "**failure containment in unstable environments**", not "more agents = better". This is what your data actually supports.

## Bottom line (Round 3)

Your worry "if planner-worker scales too, what's the point" is correct *only if you measure on the wrong axis*. On wall-time-to-correct-answer in benign conditions, planner-worker probably wins or ties. **On correctness-under-failures, it doesn't even come close** — and that axis is what production systems actually care about, because real LLM agents fail constantly.

You haven't built nothing. You've built the wrong demo for the right system. Run Experiment A. If the failure-injection curves separate the way I expect, you have a story. If they don't, you've learned something real about the limits of decentralization — also a story, just a different one.
