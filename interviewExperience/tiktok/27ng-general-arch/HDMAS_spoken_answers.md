# HDMAS Deep Dive — Spoken Answers (Section A, Q1–Q7)

> Every answer is 60–90 seconds spoken at a calm pace. All numbers verified against
> `internshipExperience/microsoft/HDMAS/` (code, blog outline, 系统对比 results, review doc).
> Practice rule: record → listen → re-record until one clean take. Pause instead of "uh".

---

## Q1 — "Walk me through HDMAS in 2 minutes. What can't a single agent do?"

> "HDMAS targets wide-search tasks — think 'list every Michelin-starred restaurant in Tokyo that closed in 2024, with five attributes each.' You have to touch maybe twenty independent sources, pull one row from each, and assemble a table that's scored at the cell level.
>
> A single agent fails at this for structural reasons, not prompt reasons. Every source dumps raw pages into one context window, so by source fifteen the context is mostly old evidence. Wall-clock time is serial in the number of sources. And worst, attention drifts — in our logs, the dominant single-agent failure was the agent declaring itself done while three to eight rows were still missing.
>
> The task shape is many independent lookups plus one merge — that's exactly what parallelism is for. But instead of a planner dispatching workers, HDMAS runs N identical peers with no roles at all. All coordination state lives in one shared blackboard file with an append-only task log, protected by a file lock. Each peer loops: lock the board, re-derive the remaining subtasks, claim exactly one, unlock, go execute with its own tools, then come back and mark it done. Termination is a unanimous vote-stop protocol, with a wake mechanism if someone finds the answer incomplete.
>
> Holding the same Copilot backend constant, three agents beat the single agent on 200 WideSearch tasks — Row-F1 up 11.4 percent relative, Item-F1 up 8 — and our numbers were above every multi-agent entry on the public leaderboard."

---

## Q2 — "Why planner-free? What breaks with a planner, and what did you give up?"

> "Three things break with a centralized planner on this workload.
>
> First, the planner is a single point of failure with amplification. If it forgets a source or splits the task along the wrong axis, all N workers inherit the mistake — one bad LLM call becomes N missed rows. On a per-cell metric that's brutal.
>
> Second, the planner recreates the exact context-pressure problem we went multi-agent to escape. To re-plan, it has to hold the whole query, every subtask, and every partial result in one window — so your most critical agent has the most overloaded context in the system.
>
> Third, wide search isn't knowable up front. Sources get discovered mid-run, and retrieval often succeeds only when a different agent retries from a different angle. A planner can re-plan, but every re-plan is a global barrier — workers wait while one context re-decomposes. In HDMAS, a peer that finds new evidence just appends a claim on its next iteration. No barrier.
>
> What I gave up — and I'd say this honestly: distributed termination is genuinely harder, which is why I needed an explicit vote-stop and wake-agent protocol. There's lock contention on the shared board. And there's a planning tax — every peer re-derives the full subtask list every iteration, which is redundant tokens. The bet is that on wide, weakly-coupled work where individual agent failures are common, failure containment is worth more than planning efficiency — and the data supported that."

---

## Q3 — "What's the concurrency model? Two agents claim at the same moment? Did you measure contention?"

> "The lock is two layers: an in-process threading lock plus an OS-level file lock, over a JSON registry that records holder and timestamp per file. Acquire blocks up to thirty seconds with one-second retries, and every lock has a sixty-second TTL, so a dead holder can't deadlock anyone.
>
> Two agents claiming at the same moment is structurally impossible, because claiming is a read-modify-write done entirely under the lock: lock the blackboard, read all existing claims, append exactly one entry, write, unlock. The second agent blocks, and when it acquires, it sees the first agent's claim and picks something else. The key discipline is that the lock is held only across that claim window — never during web search or LLM calls — so execution stays parallel and only coordination serializes.
>
> And yes, we measured contention, and it's the most interesting result. At eight agents, 82 percent of cases had the answer files locked by two or more agents — worst case, seven agents fighting over one final markdown file. Cases with multiple writers on the answer had a 7.8 percent success rate versus 19 percent for single-writer cases. Going from three to eight agents cost two times the wall-clock and 2.7 times the tool calls for a *worse* exact-match score. So contention wasn't hypothetical — it was the measured bottleneck, and it lived at the answer-assembly stage, not at retrieval."

---

## Q4 — "Why 3 agents? What happens at 10? Where does it stop scaling?"

> "Three wasn't a guess — I ran one, three, and eight agents and three won composite.
>
> At eight agents we found a really instructive anti-pattern I'd call 'fine but incomplete.' Cell-level Item-F1 actually went *up* — plus 8 points on the Chinese subset — because more agents extract individual fields more thoroughly. But exact-match success rate dropped 3 to 4 points. More agents find more of the right cells, then corrupt the final assembly, because the bottleneck migrates: at N equals 1 you're retrieval-bound, at small N retrieval saturates, and past that every extra agent adds nothing to coverage but piles contention onto the shared answer file.
>
> At ten agents it would be worse, and the reason is just Amdahl's law: the read-decide-claim window under the global lock is serialized, so peers spend roughly N times the lock-hold time waiting per round. Our cost data shows it — tool calls grew super-linearly from retries under contention.
>
> If I wanted to scale past this, I wouldn't tune N — I'd change structure. Per-row locks on the answer instead of one lock on the whole directory. Or better, a map-reduce split: N peers write evidence to private files with no shared state at all, then a single deterministic reduce step assembles the table. That keeps the decentralized claim protocol where it helps and removes the contended commit entirely."

---

## Q5 — "How do agents avoid duplicating work? What if an agent dies mid-task?"

> "Duplication is prevented by atomic check-then-claim. The blackboard has an append-only task log, and claiming means: acquire the lock, read every existing entry, claim only a subtask that isn't there, release. Since the read-modify-write happens under the lock, two agents can't race on the same claim. The caveat I'd flag myself: the lock gives atomicity, not semantic dedup — the model still has to recognize two phrasings as the same subtask, which is why the prompt forces full re-enumeration every loop.
>
> For agent death, three layers. First, locks carry a sixty-second TTL, so a dead holder can't deadlock anyone — the next acquirer reclaims it — plus a cleanup handler releases all locks on any graceful failure. Second, agents are homogeneous, independent tasks; the orchestrator catches a crash and the others just keep working, because there's no planner to lose. Third, nobody can vote to stop until the answer verifiably covers every subtask — so a dead agent's missing work surfaces as an incomplete answer, and a survivor claims a fix task and redoes it.
>
> One thing I'd improve: locks have leases but task claims don't, so a dead agent's in-progress entry lingers until the completeness check catches it. I'd give claims the same TTL mechanism — expired claim, anyone re-claims."

---

## Q6 — "Is +11.4% within noise? How many runs, what variance?"

> "Fair challenge, and I'll give you the honest version. Each configuration was a single run — Avg-at-1 — over 200 tasks. I didn't have budget for multi-seed reruns, so I don't have error bars, and I flagged that myself in the verification list before anyone else did.
>
> What gives me confidence in the direction, though. First, it's a paired comparison — same Copilot backend, same tools, same 200 tasks; the only variable is the architecture. Second, the effect is consistent across independent slices: English and Chinese subsets separately, the view excluding parse failures, and the strict intersection of cases all systems completed — three-agent wins or ties in every cut. Third, the gain has a mechanism, not just a number: it concentrates in the Chinese subset, plus 9 points Row-F1, where single-agent early convergence was worst — which is exactly what failure containment predicts.
>
> There's a place where I explicitly did *not* trust my own numbers: our leaderboard comparison looked like 2.4x over the best public system, but that's contaminated — they report Avg-at-4, we ran Avg-at-1, and the model generations may differ. I wrote that warning into the report myself. With more budget, the first thing I'd run is Avg-at-4 with standard deviations and a per-case paired bootstrap on the 3-agent-versus-baseline delta."

---

## Q7 — "F1 suddenly drops in production — how do you debug it?"

> "First instinct: separate the measurement from the system. Every HDMAS run emits a JSONL event log, and the blackboard's task log is a full audit trail per case — so I'd re-run the evaluator on old, frozen outputs first. If yesterday's outputs score lower today, the judge or eval pipeline drifted, not my system.
>
> If the system really regressed, the metric shape tells me where to look. Item-F1 stable but exact-match down — that's an assembly problem: I'd grep the event logs for multi-writer lock events on the answer files, because we measured that pattern crushing SR at high agent counts. Both metrics down together — that's coverage: retrieval failing, so I'd check search-tool errors and whether specific sources went dark.
>
> Then I'd diff task logs case by case between a good run and a bad run. Fewer claims per case means subtask enumeration regressed — likely a model behavior change. Same claims but more 'failed' outcomes means sources became unreachable. I'd also check for agent-crash events, lock timeouts, and early vote-stops.
>
> Last, backend drift: the Copilot model behind the agents isn't pinned, so if nothing else explains it, I'd re-run a fixed twenty-case subset to bisect when behavior changed. The general principle is the reason I like the blackboard design: coordination is a file, so the whole run is auditable after the fact — you debug from evidence, not from guesses."

---

## Delivery notes

- Q3 and Q4 share the contention data (82%, 2×/2.7×, SR 7.8 vs 19) — know those five numbers cold; they're your strongest proof you measure what you build.
- Q6 is a trap question about intellectual honesty, not statistics. Leading with "I'll give you the honest version" and the self-flagged caveat is the win condition.
- If pressed past any answer, bridge to the improvement you'd make (map/reduce, claim leases, Avg@4) — always end owning the next step.
