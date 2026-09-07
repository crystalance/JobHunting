# Round 1 — System Design From Zero (confirmed format: SD + AI project deep-dive, 60 min)

> Recruiter confirmed: first round = system design + AI-related project deep-dive, 60 min video.
> Likely split: ~25–30 min each. Deep-dive prep is done (HDMAS / benchmark / postTraining spoken
> answers). This file closes the SD gap in ~2 weeks.

## 0. Reframe: you have done system design — you just haven't done the interview format

You designed: a multi-agent coordination system with locks and TTLs (HDMAS), a 5-stage data
pipeline with retry loops and freshness maintenance (benchmark), a deploy pipeline with artifact
storage, scanning, and signed URLs (Alibaba), and a CI/CD system with health-check rollback
(BrowserUse). The interview only asks you to do the same reasoning *out loud, in a fixed order,
with capacity numbers*. What you lack is the **format and the standard vocabulary**, not the
ability. Two weeks is enough for NG-lite expectations.

## 1. NG-lite expectations (what "pass" means for a new grad)

You are NOT expected to know Kafka internals or design Twitter at planet scale. You ARE expected to:
1. Clarify requirements before designing (functional + scale: users, QPS, read/write ratio).
2. Do rough numbers without prompting (back-of-envelope: QPS, storage, bandwidth).
3. Draw a sane high-level shape: client → gateway/LB → stateless services → cache → DB → queue → workers.
4. Go one level deep on 1–2 components (schema, API, cache policy, queue semantics).
5. Name bottlenecks and trade-offs out loud (hot keys, read-heavy, consistency vs latency).
6. Respond to "what if 10× traffic / a node dies / two writes race?" without freezing.

## 2. The answer skeleton (memorize — use every single time)

1. **Requirements (3–4 min):** functional (3–5 bullet features) + non-functional (scale numbers,
   latency target, consistency needs). ASK, don't assume: "How many DAU? Read-heavy? Is stale-by-
   seconds acceptable?"
2. **Estimates (2 min):** QPS = DAU × actions / 86,400 (≈10⁵ s/day); peak = 2–3× average;
   storage = items × size × retention. Round aggressively; the habit matters, not precision.
3. **API (2 min):** 3–5 endpoints, method + path + params. Defines the contract for the boxes.
4. **High-level diagram (5 min):** the standard shape, then walk one request end-to-end aloud.
5. **Deep dive (8–10 min):** let the interviewer pick, or pick your strongest component:
   data model + why this DB, cache strategy (TTL? invalidation? cache-aside), queue (why async,
   what if consumer dies), idempotency.
6. **Bottlenecks & scaling (5 min):** single points of failure, hot partitions, what breaks at
   10×, what you'd measure first.

Phrases that buy thinking time (drill these): "Let me state my assumptions first…" ·
"The trade-off here is X vs Y; given the requirement, I'd pick…" · "This works to roughly N QPS;
past that I'd shard by…" · "I'll simplify for now and note it as an extension."

## 3. Vocabulary you must be fluent in (map each to something you already did)

| Concept | You already did it |
|---|---|
| Mutex / lock granularity / TTL leases | HDMAS lock manager (60s TTL, per-file locks) |
| Idempotency + retries + monotonic merge | benchmark fill-loop; Mini-UPS ACK/SEQ |
| Queue + workers + backpressure | benchmark dispatcher/fill-loop; batch eval |
| Cache-aside, TTL, invalidation | Redis in your projects; 缓存三兄弟 from AIsystem.md notes |
| Blob storage + signed URLs + lifecycle | Alibaba OSS two-bucket design |
| Health checks, rollback, zero-downtime deploy | BrowserUse CI/CD |
| Rate limiting (token bucket / sliding window) | learn fresh — 30 min |
| DB indexing, sharding key choice, read replicas | Alibaba Spring Boot backend indexes |
| Consistent hashing | learn fresh — 30 min (ring, virtual nodes, why resharding is cheap) |

When you use a concept, cite your experience in one clause: "I'd lease the claim with a TTL —
I did exactly this in my multi-agent system to survive dead agents." That converts textbook
answers into evidence.

## 4. Most-likely questions for THIS team (practice in this order)

1. **Design a CI/CD pipeline service for 1,000 repos.** (Their daily work.) Queue of build jobs,
   worker pool, artifact cache keyed by content hash, flaky-test detection, per-repo concurrency
   limits, priority lanes. You can anchor on your GitHub Actions + rollback experience.
2. **Design an AI code-review bot for a large org.** Webhook on PR → diff scoping → chunking →
   LLM workers with rate/cost budget → dedupe/rank comments → feedback loop measuring
   accept-rate. Anchor: your benchmark pipeline (evaluation, judge isolation) + CodeAct batching.
3. **Design an LLM conversation-context service.** (Real ByteDance question, Feb 2026.) Redis
   hot store + MySQL persistence, cache-aside, TTL expiry sweep, write path = update DB then
   delete cache, sharding by user_id. Anchor: AIsystem.md Q&A you already wrote.
4. **Design a rate limiter** (classic warm-up; also a component inside #1–3). Token bucket local
   → Redis + Lua for distributed → answer "what about clock skew / Redis down?" (fail-open vs
   fail-closed).
5. **Design a URL shortener / notification service** (generic backups; 30 min each of reading a
   worked solution, then redo from memory).

## 5. The 2-week crash plan (assumes interview booked ~2.5 weeks out)

**Days 1–2 — format & vocabulary.**
- Learn the skeleton (§2) by heart. Watch 2–3 worked NG-level SD interviews (e.g. "Hello
  Interview" / "Jordan has no life" system design walkthroughs) — watch for *structure and
  narration*, not content.
- 30-min targeted reads: consistent hashing, token bucket, cache patterns (you have the Redis
  notes already), DB sharding basics.

**Days 3–8 — one design per day, out loud, 30 minutes on a timer.**
Order: rate limiter → context service → URL shortener → CI/CD service → AI code-review bot →
notification service. Method per session: 30 min solo on paper/Excalidraw *speaking the whole
time* → 15 min compare against a reference solution → write a 5-line gap list → next day starts
by redoing yesterday's diagram from memory in 5 min.

**Days 9–10 — the two team-flavored designs again, deeper.**
Redo CI/CD service and code-review bot with full skeleton + numbers. These are the two most
likely real prompts; you want them at "second time through" fluency.

**Days 11–12 — mock under pressure.**
Two full 60-min mocks (friend, or me as interviewer in chat): 25 min SD + 30 min project
deep-dive + 5 min questions. The deep-dive half re-uses your spoken answers — practice the
*transition*: finishing a design, then switching register to storytelling.

**Days 13–14 — polish + rest.** Re-record weak spots; day before = review diagrams only, no new
material; test Lark.

**Throughout:** keep 2–3 LC mediums/week (LRU + rate limiter implementations count — they're
both SD-adjacent AND coding practice), and keep the daily English story reps from prep_plan.md
alive — the deep-dive half of this round is where fluency pays.

## 6. Deep-dive half: how it connects

The interviewer will likely pick ONE project and push. Expected priority given the team:
benchmark pipeline ≥ postTraining ≥ HDMAS ≥ BrowserUse. Your prepared files map 1:1:
`benchmark_generate_pipeline.md`, `postTraining_spoken_answers.md` + `trainningDetails/details.md`,
`HDMAS_spoken_answers.md`. Rehearse each project's 2-minute overview until the first 30 seconds
are automatic — the opening under nerves is what fails first.
