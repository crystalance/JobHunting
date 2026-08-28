# Mock Interviewer Question Bank — tailored to Weikai's resume

> How to use: don't read silently. Answer each question **out loud in English**, record yourself,
> then check: did I state the situation in 1 sentence? Did I give a number? Did I stop talking after the result?

## A. Resume deep dive — Microsoft (HDMAS)

The interviewer will pick your first bullet and drill. Expected chain:
> Spoken 60–90s answers for all of Q1–Q7: see `HDMAS_spoken_answers.md` (verified against the HDMAS code and docs).

1. Walk me through HDMAS in 2 minutes. What problem does it solve that a single agent can't?
2. Why **planner-free**? What breaks with a centralized planner, and what did you give up by removing it?
3. The shared blackboard is lock-protected — what's the concurrency model? What happens when two agents claim the same task at the same moment? Did you measure lock contention?
4. Why 3 agents? What happens at 10? Where does it stop scaling and why?
5. How do agents avoid duplicating each other's work? What if an agent dies mid-task?
   > **Model answer (verified against HDMAS code):**
   > **Dedup = atomic check-then-claim.** `blackboard.json` holds an append-only `task_log`; claiming means lock BB → read ALL entries → enumerate ALL subtasks → claim only what's unclaimed (append `in_progress` entry) → unlock. The lock (threading.Lock + filelock, `locks.json` registry) serializes the read-modify-write, so racy double-claims are impossible. Caveat to volunteer: the lock gives *atomicity*, not *semantic* dedup — the LLM must recognize two phrasings as the same subtask; the prompt forces full re-enumeration every loop to mitigate.
   > **Agent death — 3 layers:** (1) locks have a 60s TTL (`LOCK_TTL`), expired locks are forcibly reclaimed, plus `finally: release_all()` on graceful failure, plus "never hold a lock during web search"; (2) agents are homogeneous asyncio tasks — orchestrator catches the crash, logs `agent_crash`, survivors keep looping (no planner = no single point of failure); (3) survivors can't `vote_stop` until `answer/` verifiably covers every subtask, so missing work surfaces as an incomplete answer → a survivor claims a fix task and redoes it.
   > **Improvement to volunteer:** locks have leases but task *claims* don't — a dead agent's `in_progress` entry lingers until the completeness check catches it. Fix: give claims the same TTL/lease mechanism, so expired claims become re-claimable.
6. Row-F1 improved 11.4% — is that within noise? How many runs, what variance?
7. If I gave you this system in production and F1 suddenly dropped, how would you debug it?

## B. Resume deep dive — benchmark pipeline (highest-value topic for THIS team)

The JD literally says "establish evaluation standards for AI-assisted R&D". Own this conversation.

1. Why is 22.7% verified coverage the baseline — what made ground truth so unreliable before?
2. Your verifier is also an LLM — who verifies the verifier? How do you prevent correlated errors between generator and verifier?
3. What does "atomic fact" mean concretely? Give an example of a task decomposition.
4. The live web changes — how do you keep a benchmark stable over time?
5. Transfer question (they WILL ask a version of this): "Our team wants to measure whether AI coding agents actually improve developer productivity. Design the benchmark." — reuse your pipeline thinking: task decomposition, verifiable ground truth, isolation of the judge, freeze protocol.

## C. Resume deep dive — post-training (SFT + GRPO)

1. Why did SFT alone take F1 from 5% to 40%? What exactly did the model fail at before?
2. What was your GRPO reward? How did you stop the model from reward-hacking (e.g., answering without searching)?
3. Accuracy up, cost down 14%, latency down 9% simultaneously — why isn't that a contradiction? What behavior change caused it?
4. Why LoRA and not full fine-tuning? Why Qwen2.5-7B?

## D. Resume deep dive — Alibaba Cloud

1. What is the A2A protocol and why does cross-framework interop need an adapter? What was hard about bidirectional JSON-RPC translation?
2. How does streaming work end to end — what happens if the client disconnects mid-stream?
3. The agent management backend serves 10K+ applications — walk me through one request: search with filters. Which indexes did you create and why?
4. What is SLR permission validation? What breaks without it? (You have the least-privilege story ready in BQ/bq_formal.md — perfect here.)
5. If agent-status queries became slow at 100K applications, what would you do?

## E. Resume deep dive — BrowserUse Bot (CI/CD + observability angle)

1. Your CodeAct layer cut LLM round-trips by 95% — mechanically, how? What's the trade-off of letting the agent write JavaScript against the page? (Safety? Debuggability?)
2. Health-check rollback: what exactly does the health check test, and what failure did it actually catch?
3. With Langfuse tracing, tell me about one production bug you found through a trace.
4. Zero-downtime deploy on a single EC2 box — how?

## F. Coding (practice these specific ones)

Backend-practical set repeatedly reported at TikTok:

- **LRU cache** (hashmap + doubly linked list) → follow-up: make it thread-safe → follow-up: what granularity of locking?
- **Rate limiter** (token bucket / sliding window) → follow-up: distributed version?
- LC Hot 100 mediums: sliding window, binary search variants, DP (house robber / LIS / edit distance), graph BFS/DFS (islands, course schedule), tree diameter (asked at TikTok with "prove correctness"), top-K (heap), merge intervals, LFU.
- Habit to drill: state complexity unprompted, list edge cases BEFORE saying "done".

## G. CS fundamentals (ByteDance classics — one evening of review each)

- Java: HashMap JDK8 internals (array+list+red-black tree, treeify threshold 8), ConcurrentHashMap (CAS + per-bucket synchronized), volatile vs synchronized, thread pool parameters.
- MySQL: B+ tree indexes, why index fails (5 scenarios), isolation levels + MVCC, redo/undo/binlog.
- Redis: why fast (IO multiplexing), RDB vs AOF, cache penetration/breakdown/avalanche + fixes, cache-DB consistency (update DB then delete cache, and why).
- Network: TCP 3-way/4-way + 2MSL, HTTPS handshake, HTTP/1.1 vs 2 vs 3.
- OS: process vs thread, deadlock conditions, how locks work. (Your blackboard-lock story gives you a natural bridge.)

## H. System design (NG-lite, this team's flavor)

1. Design a **CI/CD pipeline service** for 1000 repos (queueing, workers, caching build artifacts, flaky-test detection). ← most likely for this team
2. Design an **AI code-review bot** for a monorepo: how to scope diffs, run LLM calls at scale, measure precision/recall of comments, control cost.
3. Design a **conversation-context service** for an LLM chatbot (Redis + MySQL, expiry, consistency) — real ByteDance question from Feb 2026.
4. Classics as backup: rate limiter, notification service, URL shortener, like/follow service.
Framework every time: requirements → rough numbers (QPS/storage) → high-level boxes (gateway/service/cache/DB/queue) → deep dive one component → bottlenecks & trade-offs.

## I. BQ (HM + HR round; also sprinkled in tech rounds)

Core 8 — you need a spoken 60–90s version of each:

1. Tell me about yourself (30-second pitch, tuned to AI-infra).
2. Why TikTok / why this team? (Answer: you've spent 3 internships building agent infrastructure and evaluation; this team does exactly that at TikTok scale. Be specific about "AI agents as first-class platform citizens".)
3. Proudest / most challenging project → HDMAS or benchmark pipeline, with numbers.
4. A failure / biggest mistake → your Smart Home missed-deadline story (BQ/bq.md) is good; polish the spoken version.
5. A conflict / disagreement → your OSS-bucket-ownership story (BQ/bq_formal.md) is excellent and already has a spoken version. This is your strongest story — it shows security thinking + steelmanning.
6. Tight deadline / pressure → BoulderAI two-week prototype story (BQ/bq.md).
7. Going beyond your responsibility → least-privilege RAM policy story (BQ/bq_formal.md).
8. Helping a teammate → mini-Uber frontend story (BQ/bq.md).

Team-specific BQ to prepare fresh:

9. "Where do you think AI coding agents fail today, and what would you build to fix it?" (Have an opinion. You've watched agents fail at Microsoft and in BrowserUse — talk about verification, context management, cost attribution.)
10. "How do you stay current with AI/engineering developments?"
11. "You'll work with teams in different time zones/cultures — how do you handle that?" (ByteDance cross-Pacific collaboration reality.)
12. Career plan for the next 3 years; graduation date + onboarding availability (they need commitment by end of year — know your answer: May 2027 graduation, available immediately after).

## J. Your questions to ask them (prepare 3)

- "What's the balance between building agent infrastructure for internal developers vs. researching agent capability itself?"
- "How does the team measure success — adoption, R&D-efficiency metrics, or business impact?"
- "What does the mentorship/ramp-up structure look like for new grads on this team?"
