# CI/CD Deep Dive — formal design + how BrowserUseBot actually does it

> Part 1 = the interview-format system design (start from functional requirements — this is the
> likely round-1 prompt "design a CI/CD service"). Part 2 = your real pipeline, verified against
> `/Users/lanceliao/CursorProjects/BrowserUseBot` (`.github/workflows/deploy.yml`,
> `scripts/deploy.sh`, `scripts/run-aws.sh`). Part 3 = the questions an interviewer will dig into.

---

# Part 1 — Formal design: a CI/CD platform (e.g., for 1,000 repos)

## 1. Functional requirements (say these first, then confirm with the interviewer)

1. **Trigger**: run a pipeline on push / PR / manual dispatch / schedule.
2. **Build & test**: execute user-defined steps (lint, unit tests, build) in isolated, reproducible
   environments; report pass/fail back to the code host (PR status checks).
3. **Artifacts**: store build outputs (images, binaries) versioned and addressable.
4. **Deploy**: promote an artifact to environments (staging → prod) with a chosen strategy
   (rolling / blue-green / canary), gated by health checks.
5. **Rollback**: one-click (or automatic) return to the last known-good version.
6. **Observability**: logs per step, pipeline status dashboard, notifications.

Non-functional: correctness over speed (never deploy an untested commit — trigger→deploy must be
traceable to an exact commit SHA); isolation (one repo's build can't read another's secrets);
elasticity (bursty load — everyone pushes at 5pm); a stuck job must never block the queue
(timeouts); auditability (who deployed what, when).

## 2. Scale estimates (do this unprompted)

1,000 repos × ~30 pushes/day ≈ 30k pipelines/day ≈ 0.35/s average, but bursts of 50–100
concurrent at peak → need ~100–300 concurrent workers if a pipeline averages 5–10 min.
Artifacts: 30k builds × ~200 MB ≈ 6 TB/day raw → dedupe/caching and retention policy are
mandatory, not optional. Logs: ~1–10 MB per pipeline → object storage + index.

## 3. High-level architecture

```
GitHub/GitLab ──webhook──> API Gateway ──> Trigger Service ──> Job Queue (per-priority)
                                                                  │
                        Scheduler/Dispatcher <────────────────────┘
                          │  (matches job → worker pool, enforces per-repo concurrency caps)
                          v
                    Worker Fleet (autoscaled, containerized, ephemeral)
                      │        │
              Cache Service   Artifact Store (object storage, content-addressed)
                      │        │
                      └──> Deploy Controller ──> target envs (staging/prod)
                                    │  health checks + strategy (rolling/canary)
                                    v
                             Metadata DB (pipelines, runs, statuses) + Log Store + Notifier
```

**Data flow (walk one push end-to-end):** push → webhook (verify signature) → trigger service
resolves pipeline config from the repo (`ci.yaml` at that SHA) → enqueue job(s) with priority +
repo concurrency check → dispatcher assigns to an idle worker → worker spins an ephemeral
container, pulls code at SHA, restores dependency cache (keyed by lockfile hash), runs steps,
streams logs, uploads artifact (keyed by content hash) → reports status to the code host →
if branch == main and tests green, deploy controller executes the strategy: shift traffic
gradually, watch health/error-rate metrics, auto-rollback on regression → record everything in
the metadata DB.

## 4. Component deep-dives (pick 1–2, let the interviewer steer)

- **Queue & scheduling**: priority lanes (PR checks > main builds > nightly); per-repo concurrency
  cap so one monorepo can't starve everyone; visibility timeout so a dead worker's job re-queues
  (lease semantics — same idea as my HDMAS claim-lease). Idempotency: job execution keyed by
  (repo, SHA, pipeline-id) so retries don't double-deploy.
- **Workers & isolation**: ephemeral containers/VMs, no cross-job state, secrets injected at
  runtime scoped to the repo, killed at timeout. Autoscale on queue depth.
- **Caching (the biggest speed lever)**: dependency cache keyed by lockfile hash; Docker layer
  cache; test-result cache / test-impact-analysis (only run tests affected by the diff) at the
  advanced end.
- **Deploy strategies**: rolling (replace N at a time, cheap, brief version mixing), blue-green
  (two fleets, atomic switch, 2× cost, instant rollback), canary (1% → 10% → 100% gated on
  metrics; safest, needs good observability). Rollback = repoint to previous *artifact* (never
  rebuild — rebuilds aren't guaranteed identical).
- **Flaky tests** (this team cares): quarantine list, auto-retry-once with flake-tracking,
  detect via pass/fail history on identical SHA.

## 5. Bottlenecks & failure modes to name proactively

Hot spots: queue at peak (shard by org), artifact storage growth (retention + dedupe), secrets
handling (never in logs), webhook loss (reconcile by polling as backup), a worker dying mid-job
(lease timeout → requeue), deploy during deploy (serialize per service — concurrency group).

---

# Part 2 — BrowserUseBot's actual CI/CD (the facts, from the repo)

## Pipeline walkthrough

**Trigger** (`.github/workflows/deploy.yml`): push to `main`, plus `workflow_dispatch` for manual
runs. `concurrency: group: deploy-aws, cancel-in-progress: true` — two rapid pushes can't run two
deploys against the same box; the stale one is cancelled.

**Stage 1 — test job** (ubuntu-latest, Python 3.12, "Linux like prod — catches OS/dep issues
early"): `pip install -e .` then **import smoke tests** — imports every core module
(`core.runner`, `core.handoff`, `core.llm`, `platform.telegram_gateway`, `novnc_view`,
`remote_view`, `tunnel`). Catches syntax errors, broken imports, missing/incompatible deps.
Honest scope: no pytest suite yet (comment in the file says add as it grows).

**Stage 2 — deploy job** (`needs: test` — hard gate): `appleboy/ssh-action` with secrets
(`EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`) SSHes to the EC2 box, `git fetch && git reset --hard
origin/main`, runs `scripts/deploy.sh`.

**deploy.sh — the interesting part:**
1. Records `PREV=$(git rev-parse HEAD)` — the rollback target — *before* touching anything.
2. Accepts an optional ref (`./deploy.sh v1.2.0`) → the same script does pinned deploys and
   manual rollbacks.
3. `git reset --hard $REF` → **deterministic deploys**: the working tree exactly matches the
   repo; local server edits are deliberately destroyed. State that must survive (`.env`,
   `workspace/`, browser profile) is gitignored, so it's untouched.
4. `pip install -e .` + `playwright install chromium` in the project venv, then
   `sudo systemctl restart browseruse`.
5. **Health check + auto-rollback**: sleep 5 → `systemctl is-active browseruse`. On failure:
   `git reset --hard $PREV` → reinstall → restart → re-check; if the rollback also fails, print
   `journalctl -u browseruse -n 50` hint and exit 1 (visible as a red X in Actions).

**Runtime it deploys into** (`run-aws.sh` + systemd): a `browseruse` systemd unit runs the
Telegram gateway 24/7; headful Chromium renders on a persistent Xvfb virtual display (`:99`) with
fluxbox, so noVNC can expose the *agent's own browser* for the human login handoff; the Chromium
profile persists across deploys → logins are rare.

## Design decisions and their rationale (know these cold)

| Decision | Why | Trade-off I accepted |
|---|---|---|
| Git-pull deploy, not Docker images | Single stateful host; the *point* of the box is a persistent logged-in browser profile + Xvfb display — container-per-deploy would either lose that state or need volume plumbing for profile/X display; git+venv is minutes to build, seconds to deploy | No image immutability: deps re-resolved at deploy time (mitigated by pinning), "works in CI, breaks on box" residual risk |
| systemd, not a process manager in Docker | Free auto-restart on crash, `journalctl` logs, boot persistence | Tied to one box; no horizontal scaling (fine: one Telegram bot ↔ one user session) |
| Import smoke test as the CI gate | The failure mode that actually bit: broken imports/deps discovered only at server restart. Cheap (~30 s), catches the majority class | Not a behavior test; a logic bug passes CI and is caught by the health check + rollback instead |
| Health check = `systemctl is-active` after 5 s | The dominant deploy failure is crash-on-startup (bad import, bad .env reference, port conflict) — process liveness catches exactly that | Shallow: a process that's up-but-broken (Telegram auth failing) passes; see improvements |
| Rollback = previous *commit*, reinstall, restart | On a git-deploy model the commit is the artifact; reinstalling from the old tree also restores old pinned deps | Rollback isn't instant (~1 min reinstall) vs blue-green's instant switch |
| `concurrency: deploy-aws` group | Two pushes in quick succession = two SSH sessions mutating the same working tree mid-restart → corrupted deploys | Latest push wins; a cancelled deploy is fine because the next one supersedes it |

## The "zero-downtime" claim — defend it precisely (they WILL push)

`systemctl restart` has a real gap of a few seconds. The claim survives because of **Telegram's
long-polling semantics**: the bot pulls updates via `getUpdates` with an offset, so while the
process restarts, incoming messages queue on Telegram's side and are delivered when polling
resumes — **no user message is ever lost**, and to the user a deploy is invisible.

The honest edge: a task **in flight** during restart is killed. Say it before they find it, plus
the fix: a graceful drain — on SIGTERM, stop accepting new tasks, finish or checkpoint the current
one within a timeout, then exit (systemd `TimeoutStopSec`).

---

# Part 3 — Likely interviewer deep-dive questions (with spoken answers)

**"Your test stage is just imports. Is that enough?"**
> "It's honest about what it covers — dependency and syntax breakage, which was the actual
> majority failure class, at 30 seconds per run. The layered design is: cheap import gate in CI,
> then the health-check-plus-rollback on the box as the behavioral gate. What I'd add next, in
> order: pytest on the pure logic (handoff state machine, skill selection), one headless smoke
> task against a static page in CI, and a staging systemd unit on the same box before prod. I'd
> keep the pyramid cheap at the bottom — a full browser E2E in CI is slow and flaky, exactly the
> kind of test that trains people to ignore red."

**"Why not Docker? You containerize nothing?"**
> "Deliberate for this workload. The value of that box is *state*: a logged-in Chromium profile
> and a persistent X display for the noVNC handoff. Immutable containers want stateless
> workloads; here I'd be mounting the profile and the X socket as volumes, and I've gained
> complexity without gaining the thing images buy you — reproducibility — because the stateful
> parts live outside the image anyway. At team scale, or multi-host, I'd flip: image per release,
> profile in a volume, blue-green on two containers. The decision is workload-shaped, not
> ideological. And I did use docker-compose where it fits — the Langfuse observability stack."

**"What if the health check passes but the bot is actually broken?"**
> "Real gap — `is-active` is liveness, not readiness. The upgrade path: expose a `/health` that
> verifies the Telegram API handshake and a trivial CDP round-trip to Chromium, have the deploy
> script curl it with retries instead of checking the process, and page on failure. Beyond that,
> synthetic monitoring: a canary task once an hour, alert on failure — that catches 'up but
> useless,' which no deploy-time check can."

**"Two deploys race — what happens?"** → the `concurrency` group serializes at the workflow level,
`cancel-in-progress` drops the stale one. On-box, the script is also naturally last-writer-wins
because `reset --hard` is idempotent. The remaining race — a manual `deploy.sh` running while CI
deploys — I'd fix with a `flock` on a lockfile in the script (same primitive as my HDMAS locks).

**"How do secrets get to the app?"** → CI only holds the SSH credentials (GitHub encrypted
secrets). App secrets (`TELEGRAM_TOKEN`, LLM keys) live in `.env` on the box, gitignored,
surviving `reset --hard`. Never in the repo, never in CI logs. At team scale: SSM Parameter
Store / Secrets Manager with instance-role access, so secrets rotate without SSH.

**"Rollback rolls back code. What about data/schema?"** → This app has no DB schema, so commit
rollback is complete. In general: expand-and-contract migrations (add column → dual-write →
switch reads → drop later), so code N−1 always runs against schema N — rollback stays safe.

**"What breaks first at 10× (say, 50 bot instances)?"**
> "The deploy model. SSH-per-box doesn't scale past a handful; and one broken deploy × 50 boxes
> is an incident, not a retry. I'd move to: build an image once in CI, push to a registry, then
> rolling update via ASG instance refresh or ECS — with the browser profile externalized to EFS
> or per-user volumes. The CI half barely changes; it's the CD half that has to grow up. That's
> also the honest scaling answer generally: my current design is optimized for one stateful box
> with a one-person team, and I can tell you exactly which piece I'd replace at each growth step."

**Numbers to have ready:** deploy ≈ 2 min push-to-live (was manual multi-step before) · test gate
~30 s · health-check window 5 s · rollback ≈ 1 min · runs 24/7 via systemd auto-restart.
