# Benchmark Generation Pipeline — 2-min Overview + Follow-up Answers (Section B)

> Source of truth: `internshipExperience/microsoft/BenchmarkBuildingPipeline/`
> (flowchart HTML, run report 20260616, `custom_benchmark/` code).
> All numbers below verified against the run report. Spoken style — record, listen, re-record.

---

## The 2-minute overview take

> "The problem I was solving: to measure web-search agents, you need ground truth — but human annotation doesn't scale, and for live-web tasks the 'truth' isn't even stable over time. So I built a pipeline that generates and maintains benchmark ground truth automatically, with zero human annotation.
>
> It has three core stages. Stage one takes a raw task — a user query plus a workbook — and an LLM decomposes it into **atomic facts**: the smallest independently verifiable claims, each with a type, a unit, a refresh tier, and **identity keys** — the minimal fields that let a later verifier uniquely locate that exact value on a real source. A second LLM pass audits just the identity keys, asking one question: could an honest verifier confirm this value belongs to this instance?
>
> Stage two fills the gold: a ground-truth agent with web search finds each value and must cite the evidence URL and snippet — and it's instructed to prefer null over guessing. Then a **separate, isolated verifier session** re-fetches the cited source independently and re-derives the value. Filling and verification are deliberately asymmetric — the verifier never sees the filler's reasoning, only the claim.
>
> Stage three keeps it alive: every fact has a freshness tier — half our facts were static, but 41 percent were daily-changing, like commodity prices. For those, the pipeline auto-writes deterministic parser skills, tests them by replaying against frozen snapshots, and re-resolves values at eval time, with drift detection.
>
> The result: verified ground-truth coverage went from 22.7 percent to 70.1 percent — 309 of 441 instances across 50 generated cases, each frozen with value, evidence URL, timestamp, and a verified flag. Any candidate agent can then be scored deterministically against it."

**The thesis sentence (use when they ask "what's the key idea?"):**
> "A benchmark is only as credible as its ground truth is *verifiable* — so I made verification the product: every gold value carries its own evidence and can be independently re-derived, by an agent at build time and by a deterministic parser afterward."

---

## B.1 — "Why was 22.7% the baseline? What made ground truth so unreliable before?"

> "22.7 percent was the first full run, and the failures fell into three buckets — and only one of them was the model's fault.
>
> First, operational: we had a 30-minute per-case cap and one LLM session per instance. Twenty of fifty cases timed out — some genuinely needed hours, one case had 34 instances so it spawned 34 sessions. Second, spec defects: the identity keys authored in stage one were often not *source-visible* — the verifier would find the right page but couldn't confirm the value belonged to that exact instance, so it correctly refused to verify. Third, genuine hard cases: values behind JavaScript obfuscation or anti-scrape, and some instances where no authoritative value exists at all.
>
> The fixes matched the buckets. Operationally: a 2-hour cap, instance batching — up to 12 instances per session, so 34 sessions became 7 — smallest-cases-first scheduling so one hung case can't block the run, and monotonic merge so a flaky retry can never erase an already-verified value. On specs: the reviewer pass that minimizes identity keys, and a rewritten value-first verifier. And for the honest-null cases, we made 'faithfully null' a first-class outcome that's reported, not hidden — knowing that no authoritative value exists is itself ground truth.
>
> That took it to 70.1 percent, and the remaining 30 percent is mostly the hard tail: anti-scrape sources and nulls."

---

## B.2 — "Your verifier is also an LLM — who verifies the verifier? Correlated errors?"

> "Three answers, in increasing strength.
>
> First, structural independence. The verifier is an isolated session that never sees the filler's reasoning — only the claim: identity keys, value, cited URL. And it's *value-first*: it re-fetches the source and re-derives the value itself, then compares. So the failure mode isn't 'two LLMs agree on a hallucination' — the value has to actually be on the page. The evidence anchors both of them to the external world.
>
> Second, the verifier doesn't trust its own fetch blindly. It routes by source type: binary files get downloaded and parsed by code, JavaScript-rendered pages go through headless Chromium, and if the cited URL is dead it falls back to corroborating against an independent authoritative source.
>
> Third — and this is the real answer to 'who verifies the verifier' — we added deterministic gates behind the LLM. Gate 2 replays a generated parser against the frozen HTML snapshot and requires byte-equality with the frozen value: no LLM in the loop, producer must equal product. Gate 3 runs the fetcher live. And we found the LLM verifier and the deterministic gates disagree *in both directions* — there was a source with JavaScript-obfuscated values the LLM verifier failed, but the deterministic parser de-obfuscated and reproduced 3 out of 3. That divergence is exactly why you need both layers.
>
> The honest residual risk: filler and verifier are the same model family, so they share blind spots — if both misread the same table the same way, it passes. Mitigations are the corroborate path and majority voting across sources in the repair stage; the full fix would be a different model family for verification, which is on my list."

---

## B.3 — "What does 'atomic fact' mean concretely? Give an example decomposition."

> "An atomic fact is the smallest claim that can be verified against the web independently of every other claim. Concretely it's a schema: a type, a unit, a refresh tier, an enumeration mode, and identity keys — the minimal set of fields that uniquely and *source-visibly* pin the instance.
>
> Example from a real case: the task is 'compute Scope 2 emissions for our facilities using EPA eGRID factors.' That decomposes into: one fact 'grid emission factor', with unit pounds CO2 per megawatt-hour, refresh tier annual, enumeration *fixed* with one instance per eGRID subregion, identity keys being subregion code plus data year, and authority restricted to epa.gov. The Scope 2 totals themselves are *not* facts — they're arithmetic on facts, so they belong to the grader, not the ground truth.
>
> The enumeration split matters. *Fixed* means all instances are knowable at authoring time — like those four subregions. *Discovered* means the spec only defines a key schema and a filter — say 'every vendor selling product X' — and the ground-truth agent enumerates the instances at fill time. That split is what lets the same pipeline handle both lookup tasks and open-ended coverage tasks.
>
> The authoring stage also has explicit drop rules — things that look like facts but aren't verifiable: opinions, values computed inside the workbook, claims with no public source. Scale-wise, 50 task templates decomposed into 310 facts and over 700 fixed instances."

---

## B.4 — "The live web changes — how do you keep the benchmark stable over time?"

> "By admitting upfront that stability isn't one problem — it's two, and they need different machinery.
>
> Half of our facts were static — historical numbers that never change. Those are frozen once, with value, evidence URL, a snapshot of the page text, and an as-of timestamp. Done forever.
>
> But 41 percent were *daily*-changing — commodity prices, cash bids. Freezing those makes the benchmark wrong within a week. So every fact carries a refresh tier — static, annual, monthly, weekly, daily — and for dynamic facts the pipeline auto-generates a *skill*: a deterministic parser bound to the source host. Each skill is tested on two gates before promotion: replay against the frozen snapshot must reproduce the frozen value exactly — that proves the parser is correct, offline, no network — and a live fetch must return a plausible value — that proves it still works against today's page. Only fetchers passing both get consolidated for eval-time use.
>
> At evaluation time, static facts score against frozen gold; dynamic facts get re-resolved live, with drift detection — a value that jumped more than about 60 percent is flagged as suspicious rather than silently adopted. Every refresh emits a manifest — old value, new value, drift percent, status — so the oracle's own history is auditable.
>
> The design principle: for dynamic ground truth, don't freeze *values* — freeze *the verified method of obtaining the value*, and keep proving that method still works."

---

## B.5 — Transfer: "Design a benchmark to measure whether AI coding agents improve developer productivity."

> "I'd reuse the same skeleton: decompose into verifiable atoms, verify independently of the producer, freeze with evidence, and maintain against drift.
>
> First, tasks from reality, not synthetics: mine the org's own git history — merged PRs that fixed real issues, with the repo state at the parent commit as the fixture. That kills the 'benchmark doesn't reflect our codebase' objection, but you must hold out by date to avoid contamination — the agent's training or retrieval must not contain the actual fix.
>
> Second, atomic verifiable outcomes instead of one vague score. Per task: does the test suite pass — including the tests the real fix added, which are the natural gold; does it not regress anything; diff size against the human fix; and review effort — how many human comments before merge. The existing test suite plays exactly the role my deterministic Gate 2 played: a non-LLM verifier that doesn't share the generator's blind spots. If you also want an LLM judge for code quality, fine — but it's the weakest layer, and it must be isolated from the agent's own reasoning, same asymmetry as my verifier sessions.
>
> Third, report strict and averaged metrics separately — my WideSearch experience: cell-level scores can rise while exact-match falls, and averaged-only reporting hides real regressions. Here: 'tests pass' is the strict gate; 'percent of hunks matching human fix' is the averaged signal. Plus cost per merged task, not per attempt — productivity claims must survive the cost column.
>
> Fourth, maintenance: codebases drift like the web does. Re-validate fixtures on a cadence — do the pinned dependencies still build, does the held-out test still fail before the fix — and retire tasks that no longer discriminate. A benchmark you don't maintain quietly becomes a benchmark of nothing.
>
> And measure the human side honestly: same tasks, agent-assisted versus not, time-to-green as the outcome — because 'the agent produced a diff' and 'the developer shipped faster' are different claims, and only the second one is productivity."

---

## On your validity thesis ("the answer must be verifiable with high credibility")

Agreed — and worth sharpening into interview language, because "verifiable" is doing four jobs at once in this pipeline:

1. **Locatable** — identity keys make the claim *findable* on a source (the reviewer pass exists purely for this; most early verification failures were identity failures, not value failures).
2. **Independently re-derivable** — the verifier re-obtains the value from the evidence, never trusts the producer. Verification without independence is just agreement.
3. **Deterministically reproducible** — the strongest credibility comes from the non-LLM gates (snapshot replay, live fetch). LLM-only verification caps out; the run report literally documents Gate 1 and the parser disagreeing in both directions.
4. **Durable** — verifiable *today* isn't enough for dynamic facts; the refresh machinery keeps the verification property alive over time.

Two nuances to volunteer before the interviewer does: **verified ≠ true** (same-model correlated errors survive all four layers — hence corroboration, majority voting, and ideally a second model family), and **faithful null is part of credibility** — a pipeline that can say "no authoritative value exists, and here's the search trail" is more trustworthy than one that always produces a number.

---

## Numbers to know cold

| Number | What it is |
|---|---|
| 22.7% → 70.1% | verified ground-truth coverage, baseline run → after fixes (309/441 instances) |
| 50 / 310 / 714 | task templates / atomic facts / fixed instances |
| 50.3% vs 41.3% | static facts vs daily-refresh facts |
| 30 min → 2 h, 12/session | timeout fix + instance batching (34 sessions → 7 on the worst case) |
| Gate 2: 55% · Gate 3: 42.3% | offline parser replay pass · live fetch pass (consolidate on both) |
| 26 fetchers / 27 of 80 facts | consolidated deterministic skills promoted for eval-time reuse |
