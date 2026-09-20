# Bailian / AgentScope Runtime — Deploy, Console, Impact (Spoken)

> Pair with `a2a_adapter_spoken.md` (interop) and `BQ/bq_formal.md` (OSS ownership + least-privilege).
> Grounded in: one-click flowchart (bucket1 → build → bucket2 → FC), `ModelstudioDeployer`
> (`ApplyTempStorageLease` + `HighCodeDeploy`), 10K+ apps on the management backend.
> 60–90s unless marked. If they ask schema details you didn't own, say "I'd design it this way"
> instead of inventing a table you never wrote.

---

## Meta — "These sound like three internships. What's the thread?"

> "They're one platform, three surfaces of the same problem: **how do agents become first-class products**.
>
> **Deploy** — get an agent from a laptop onto Function Compute in one click, with a scanned, versioned artifact.
> **Manage** — a backend that lists, filters, and operates tens of thousands of those apps, with RAM/SLR checks and a view that matches what FC actually is, not just what we wrote down.
> **Interoperate** — A2A, so a Runtime agent is callable by other frameworks without a custom SDK.
>
> Same invariant everywhere: the agent is a **versioned artifact plus a runtime plus a control plane**. Packaging, console, and protocol adapter are not side quests — they're how you productize an agent instead of leaving it as a demo script. That's also why this maps to TikTok General Architecture: AI-native infra is deploy, evaluate, manage, and let agents talk to each other."

---

## Q1 — "What happens after one click?"

> "One click is: the user hits deploy. Everything after that is a CI/CD pipeline we own, not 'run a script on their laptop and hope.'
>
> **Client / SDK.** The Runtime packs the app — wheel plus a zip — and asks Bailian for a **temporary storage lease**. That returns a pre-signed PUT. The bytes go into **our** bucket1, not the user's OSS. Then we call `HighCodeDeploy` with the object URL, `agent_name`, and `agent_id` if this is a redeploy.
>
> **Build plane.** A worker pulls bucket1. Fail the download, we stop. Else: security scan, dependency package, **trial start**. That's CI — compile-equivalent plus a smoke boot. Fail, we tell the user to fix the package. Pass, we promote a **stable zip to bucket2**.
>
> **Scan is a gate.** Async malware / rule scan runs in parallel, but promote-to-bucket2 and FC must not proceed if scan fails. We copy into a platform bucket at intake so the bytes we scanned are the bytes we build — user-bucket overwrite can't swap the object behind the same key.
>
> **CD.** We hand FC a **time-limited URL** to bucket2, create or update the function in the user's account, start it, **health-check**. Green: console shows deployed. Red: we do not call that version 'current.'
>
> So one click is trigger → lease → upload → scan/build/smoke → immutable promote → FC + probe. The user never activates OSS, never creates a bucket, never writes a cross-account grant."

**Walk it on the whiteboard as two planes:** offline ingest (bucket1/build/bucket2) and online runtime (FC + heartbeat). Same split as a normal CI/CD service.

---

## Q2 — "How do you rollback?"

> "Rollback is **repoint to a previous artifact**, not rebuild. Rebuilds aren't bit-identical.
>
> We keep at least **current and previous** stable objects in bucket2 — lifecycle expires intermediates so 10K apps don't become unbounded OSS. Console **version** is a pointer: `current_artifact_id`, `previous_artifact_id`, `fc_function_name`.
>
> Rollback = `UpdateFunction` with the previous OSS location + the same health check. If the probe fails, we stay on the last known-good and page. We do **not** 'notify the user to zip again' as the recovery path — that's a failed pipeline, not rollback.
>
> Two honest limits in v1. First, **no per-app deploy lock** in the first flowchart: two clicks can last-writer-win on `UpdateFunction`, so a slower old build can clobber a newer one. I'd serialize on `agent_id` — lease or queue — same as a CI concurrency group. Second, in-flight sessions on FC are affinity-sticky; a code rollback doesn't drain them. I'd document that and, at scale, version the HTTP trigger or drain by session TTL."

---

## Q3 — "What impact? How would you measure it?" (TikTok R&D-efficiency poke)

Do **not** invent a fake 40% unless you have it. Measure like a platform.

> "The product claim is **time-to-live-agent** and **who can ship**, not lines of deploy YAML.
>
> **Productivity.** Baseline was: install OSS, create a bucket, write RAM, zip, upload, click FC, wire a trigger, debug `AccessDenied`. One-click target is: pack, click, URL. I'd measure **median minutes from first deploy click to healthy endpoint**, **steps before first success**, and **percent of deploys done by RAM sub-accounts** — that last one is the enterprise unlock from the least-privilege policy. Funnel: lease requested → scan pass → build pass → FC healthy. Drop-off at scan vs FC is a different bug.
>
> **Stability.** Deploy success rate, health-check fail rate, **rollback rate**, time-to-recover, and **split-brain rate** — console says running, FC says not. If we don't measure that, the console is lying at 10K apps.
>
> **Correctness / safety.** Scan-block rate, and whether a blocked artifact ever became `current` — that should be zero. Guardrails are a separate policy path; I'd track false-block vs miss on a labeled set, not 'we added keywords.'
>
> What I would **not** report: number of agents created. That's vanity. A thousand broken deploys is not R&D efficiency."

---

## Q4 — Backend deep dive: "Walk a search-with-filters request"

> "List page: workspace-scoped, filters on **name / status / owner / update time**, pagination.
>
> **API.** `GET /workspaces/{wid}/agents?q=&status=&page=&size=`. Auth first — RAM identity plus workspace membership. Then **SLR / permission probe**: if the workspace can't call FC, I still return **our** rows but mark `fc_reachable=false` rather than 500 the whole list. Search is not allowed to become 'FC ListFunctions as the source of truth' — that's slow and eventually consistent in the wrong direction.
>
> **Data model** (control plane, not FC):
> `agents(id, workspace_id, name, status, owner_id, current_version_id, fc_function_name, updated_at)`
> `agent_versions(id, agent_id, artifact_uri, checksum, scan_status, build_status, created_at)`
> `deploy_runs(id, agent_id, version_id, state, error, started_at)`
>
> **Indexes** I'd put on for 10K+ and growing: `(workspace_id, updated_at DESC)` for the default list; `(workspace_id, status, updated_at DESC)` for tabs; `(workspace_id, name)` or a trigram/`q` field if they type-ahead. **Never** leading-wildcard `LIKE %foo%` on 10K without an engine. `fc_function_name` unique per workspace so we don't bind two apps to one function.
>
> Status in the DB is **lifecycle we own** — `draft / building / deploying / running / failed / stopped`. FC metadata is **joined at read** or refreshed by a reconciler, not the primary key of the list query."

---

## Q5 — "What is SLR validation? What breaks without it?"

> "SLR is the **service-linked role** Function Compute needs in the **customer's** account to pull code, write logs, ENI, and so on. Creating it the first time is a **main-account** (or explicitly granted) action. Sub-accounts that can deploy still can't create the SLR.
>
> Validation is a **preflight**, not a surprise at `CreateFunction`. Before we start a paid build: does this account have the FC SLR? If not, we fail with a **human** error — 'ask your admin to create the SLR once' — the same sentence I put in the Runtime deploy docs when I derived the least-privilege RAM policy.
>
> Without the check: scan and build succeed, then FC fails `AccessDenied`, the console sits on `deploying`, support tickets look like 'our platform is broken,' and we waste a build minute. With it: we don't start the pipeline. Same idea as least-privilege on the **deployer** RAM user: fail at the permission boundary, not halfway through CD."

---

## Q6 — "DB says running, FC says the function is gone / stale. What now?"

This is the question they will enjoy. Lead with **who is source of truth for what**.

> "Two writers, two clocks. **Postgres is source of truth for product intent** — name, owner, which artifact we *want* live, last user action. **FC is source of truth for runtime fact** — does the function exist, last update time, instance errors.
>
> Divergence is normal: deploy RPC succeeded, our write failed; user deleted the function in the FC console; update raced; region lag.
>
> **Read path.** List from DB. Status badge is `min(db_status, last_reconcile)`. If `reconcile_at` is stale, show 'checking' and don't claim healthy.
>
> **Reconcile job.** Periodically `GetFunction` / list by prefix. Cases: FC missing → mark `drifted` or `stopped`, don't silently recreate (the user may have deleted on purpose). FC exists, DB `failed` → repair the row. Checksum / last-modified mismatch → `needs_redeploy`.
>
> **Write path.** Deploy is a **state machine** on `deploy_runs`: `uploaded → scanned → built → fc_updated → healthy`. Only `healthy` flips `current_version_id`. If FC update succeeds and our commit dies, the next reconcile sees a newer function than `current_version_id` and either adopts it or rolls back to the DB pointer — **policy choice**, I'd adopt if checksum matches an uploaded version we know, else flag.
>
> **What I wouldn't do:** make every status API a live `GetFunction`. At 10K apps that's a thundering herd and FC rate limits. Cache + reconcile; live fetch only on the detail page or after a user-triggered deploy."

---

## Q7 — "Concurrency on deploy / two operators click Update"

> "Same as the Runtime FC tutorial: two `HighCodeDeploy`s with the same `agent_id` are two pipelines. OSS keys can be unique; **`UpdateFunction` is last writer wins** — or FC `409 ConcurrentUpdateError`.
>
> I'd take a **row lock / lease** on `agents.id`: `UPDATE … SET deploy_lock_until = now()+15m WHERE id=? AND (lock is null or expired)`. Second click gets 409 'deploy in progress' or queues. `deploy_runs` is append-only so we can audit which checksum won.
>
> Idempotency: client sends `Idempotency-Key` or we key on `checksum`. Same zip twice = return the existing run, don't build twice."

---

## Q8 — "If search is slow at 100K apps?"

> "First, confirm it's the list query, not the FC join. Explain, `workspace_id` selectivity. Covering index for the default sort. If `q` is prefix search, `name` btree; if it's token search, OpenSearch / ES, DB stays the source of filterable columns. Cursor pagination on `(updated_at, id)`, not `OFFSET`. Push FC freshness to the reconciler so the hot path is one indexed SELECT. Shard by `workspace_id` only if a single tenant is huge — most 100K problems are missing indexes and OFFSET, not sharding."

---

## Numbers / facts to have ready

| Item | What to say |
|---|---|
| Scale | Management backend: **10K+ applications** (platform), not "27K" (that's AgentScope GitHub stars) |
| Artifact path | Lease → **platform bucket1** → scan/build/smoke → **bucket2** → FC **signed URL** |
| Retention | Current + previous stable; lifecycle on intermediates |
| SLR | Must exist once per account; sub-account deploy cannot create it |
| RAM story | ~8 scoped actions vs OSS+FC FullAccess (BQ) |
| A2A | `/a2a` JSON-RPC + Agent Card; wire streaming off in v1 |
| v1 gap | No per-`agent_id` deploy lock; advertise it before they find it |

---

## Delivery notes

- Unifying thread **first** if the interviewer is hopping projects — then pick deploy *or* console to go deep.
- Impact: talk **funnels and SLOs**, not a made-up percentage.
- DB vs FC: **intent vs fact** + reconciler. That sentence is the pass bar.
- Don't mix 27K stars into the 10K apps number.
