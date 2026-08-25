

# BQ

## category

### out of responsibility / take initiative / pursue the best / go beyond for a customer

1. Alibaba Cloud → Built AgentScope Runtime deployment tooling, automating packaging, OSS uploads, and serverless deployment on Bailian for one-click releases and versioning.

   **Story: turning a customer's permission complaint into a least-privilege policy for the deploy SDK**

   - **Situation**: Our FC deploy tooling (`FCDeployManager`) automates: package the agent app → upload the artifact to an OSS bucket → create/update the Function Compute function (code pulled from OSS) → create the HTTP trigger → bind the execution role. Our docs told users to grant the deploying account the broad system policies — effectively `AliyunOSSFullAccess` + `AliyunFCFullAccess`. That was "fine" initially because we mainly targeted personal developers deploying with their own main account.
   - **Trigger**: An enterprise customer complained the authentication requirement was too coarse: their developers deploy from **RAM sub-accounts** under a company main account, and security policy wouldn't allow granting a sub-account full access to *all* OSS buckets and *every* FC function in the account. Strictly speaking this was outside my task scope (my part was the SDK deploy script; role/permission setup was "the platform's problem"), and I could have routed it to customer service. But I thought: if we're asking users to over-grant, that's a real product defect — so I took it.
   - **Action**: I derived the **minimal permission set empirically, starting from zero**:
     1. Created a test RAM sub-account with **no permissions**, ran the deploy script, and let it fail.
     2. Each failure returns an `AccessDenied` log that names the **exact missing action and resource ARN** — e.g. first `oss:PutObject` on the artifact bucket, then `oss:GetObject` (FC pulls the code package from OSS at create time), then `fc:CreateFunction`, `fc:UpdateFunction`, `fc:GetFunction` (idempotent redeploy), `fc:CreateTrigger` (HTTP trigger), `fc:PublishFunctionVersion` (our versioning feature), and `ram:PassRole` (needed when binding the FC execution role to the function).
     3. Added exactly that one action, re-ran, repeated until the full deploy-→invoke-→update loop passed.
     4. Then **tightened the Resource scope**: OSS actions restricted to the specific artifact bucket/prefix (`acs:oss:*:*:{bucket}/agentscope-deploy/*`) instead of `*`, FC actions scoped to the function-name prefix our SDK generates; verified nothing else broke.
     5. Regression-tested the final custom policy end-to-end (fresh deploy, update-in-place, version publish), then documented it as a copy-pasteable RAM policy JSON in the deployment guide, replacing the "grant FullAccess" instruction. One caveat I hit and documented: the **service-linked role (SLR)** for FC must already exist — creating it the first time requires main-account (or explicitly granted) privileges, so the guide tells enterprise admins to do that once up front.
   - **Result**: Sub-account users could deploy with a policy scoped to ~8 actions on named resources instead of two FullAccess policies. The customer's security team accepted it, and the policy JSON went into the docs so every later enterprise user got it for free.
   - **Reflection (what I'd say in the interview)**: the feedback was technically "not my module," but the least-privilege principle is exactly the kind of thing that's cheap to fix at the SDK-docs level and expensive for every customer to figure out alone. Deriving permissions from real failure logs, rather than guessing from API docs, is also more trustworthy — the same "verify empirically, then freeze" habit I used later at Microsoft for benchmark ground truth.

   > Fits: taking initiative / customer obsession / going beyond assigned scope / attention to security detail.


   ## conflict / Disagreement

1. Alibaba Cloud → AgentScope Runtime deployment tooling: **who should own the OSS bucket for deployment artifacts — the user or the platform?**

   **Story: a technical disagreement with my mentor, resolved with a friction analysis and a security argument**

   - **Situation**: I was building the one-click deploy path for Bailian's high-code agent platform: a local packaging script zips the user's agent code, uploads it, and triggers the platform's build-and-deploy flow onto Function Compute. The open design question was **where the uploaded artifact should live**.
   - **The disagreement**: My mentor's plan was to reuse the **user's own OSS bucket** — the script uploads to the user's bucket, and Bailian pulls the package from there for the build. I believed the **platform should provide the storage** (Bailian-owned buckets). We were both trying to ship the same one-click experience; we disagreed on the trade-off.
   - **His side (which was legitimate — I steelmanned it before arguing)**:
     1. **Cost**: with the platform hosting artifacts for every app at 10K+-application scale, storage and bandwidth land on our bill instead of the user's.
     2. **Ship fast**: the user-OSS path reused the existing SDK upload flow — get the pipeline running end-to-end first, optimize later.
     3. **Data ownership**: user code staying in the user's own bucket is a cleaner IP boundary — they control retention and deletion, and the platform never "holds" customer source code.
   - **My side (I owned the platform backend, so I saw the flow-level cost)**:
     1. **Onboarding friction breaks "one-click"**: since I was also building the high-code platform's backend, the deploy flow would have to **query the user's OSS activation status first**. If OSS isn't activated, the user must leave the flow entirely and go activate **a separate, separately-billed cloud service** — which takes time, adds a cost line on *their* bill, and realistically requires someone technical to create the bucket, set the region correctly, and grant the platform read access. That's 4-5 extra steps, a new prerequisite dependency, and several new failure modes I'd have to build, handle, and support in the backend. For a product whose whole pitch is "one click," the first-deploy experience would routinely be "first go sign up and pay for another cloud service" — we'd be pushing our infrastructure decision onto the user as a procedure.
     2. **Authorization is a security surface**: pulling from a user bucket needs a cross-account read grant (RAM/STS). In practice users over-grant (the same coarse-permission problem I'd seen in the SDK feedback) — every user bucket integration is a new misconfiguration risk on both sides.
     3. **The artifact-integrity gap (the decisive security argument)**: our build pipeline runs a **malicious-file scan** before building. An OSS object is addressed by bucket + key, and re-uploading to the same key silently **overwrites the content behind the same URL** — so with a user-controlled bucket, the bytes we scanned and the bytes we build from aren't guaranteed to be the same. You can patch this (pin the ETag and fetch with `If-Match`, or require the user to enable bucket versioning and pin a `versionId`), but every patch either adds machinery or depends on configuration in a bucket we don't control. The clean, unconditional guarantee is to snapshot-copy into a platform bucket at intake — at which point the platform bucket isn't optional, it's the design.
     4. **Reliability/UX**: a platform bucket is region-colocated with the build machines, and lets us control versioning and issue **time-limited signed URLs** instead of standing permissions.
   - **How I handled it**: I didn't argue in the abstract. I (1) wrote up the two options as a trade-off table, (2) walked through the first-deploy flow step-by-step under each option, counting user-visible steps and failure points, and (3) raised the scan-then-swap integrity problem. For his cost concern I proposed a concrete mitigation instead of dismissing it: artifacts are **transient** — lifecycle rules auto-expire build intermediates, we keep only the current + previous stable version for rollback, so per-app storage stays bounded (tens of MB), and it's traded against fewer onboarding drop-offs and support tickets.
   - **Resolution & Result**: My mentor agreed once the friction count and the TOCTOU argument were on the table — his "run the flow first" instinct stayed (we shipped incrementally), but on platform-owned storage. The final architecture: the local script uploads through the platform entry point into **Bailian bucket1** → build machine (security scan → dependency packaging → trial launch) → stable artifact promoted to **bucket2**, served to Function Compute via **time-limited access URLs**. One-click stayed literally one click: no OSS activation, no bucket creation, no cross-account grant for the user.
   - **Reflection**: two things I'd repeat. First, **steelman before you argue** — his cost and ownership points were real, and my proposal had to *answer* them (lifecycle policy, retention rules), not wave them away. Second, **disagree with artifacts, not adjectives**: a step-count of the actual onboarding flow and one concrete attack scenario moved the discussion in ten minutes, where "I think platform storage is cleaner" would have gone nowhere. And if the decision had gone the other way, activation-check flow was buildable — I'd have committed to it.

   > Fits: disagreement with manager/mentor · technical trade-off debate · security awareness · disagree-and-commit.

   **Spoken version (~90 seconds)**

   > At Alibaba Cloud I built the one-click deploy pipeline for the Bailian agent platform — package the user's agent code, upload it, build, and deploy it to serverless. My mentor and I disagreed on one design point: where the uploaded artifact should live. His plan was to use the **user's own OSS bucket** — reuse the existing upload path, and storage cost stays on the user's bill. I thought the **platform should own the storage**.
   >
   > His concerns were legitimate: at platform scale, hosting every app's artifacts is real money, and user code staying in the user's bucket is a cleaner ownership boundary. So instead of arguing in the abstract, I did two things. First, I walked through the actual first-deploy flow under his design: OSS is a separate, separately-billed service, so if the user hasn't activated it, they have to leave our flow, sign up, pay, create a bucket, and grant us access — four or five steps that need a technical person, for a product whose whole pitch is "one click." Second, I raised a security gap: our pipeline scans the artifact for malicious files before building, but an OSS object URL doesn't change when its content is overwritten — so in a bucket *we don't control*, the bytes we scanned and the bytes we build aren't guaranteed to be the same. The clean fix is to copy into a platform bucket at intake — which means the platform bucket has to exist anyway.
   >
   > For his cost concern I proposed a concrete answer rather than waving it off: artifacts are transient, so lifecycle rules auto-expire intermediates and we keep only the current and previous version — per-app storage stays at tens of megabytes.
   >
   > He agreed once the step count and the integrity argument were on the table. We shipped on platform-owned buckets: users upload through our entry point, we scan and build, and serve the artifact to Function Compute via time-limited signed URLs. One click stayed literally one click — no service activation, no bucket setup, nothing for the user to configure.
   >
   > What I took away: steelman the other side first — my proposal had to answer his cost point, not dismiss it — and disagree with artifacts, not opinions. A step count and one concrete attack scenario settled in ten minutes what "I think platform storage is cleaner" never would have. And if the call had gone the other way, I'd have built the activation-check flow and committed to it.


---

---



   ## Failure / Mistakes


   ## Prioritization / Pressure / tight ddl


   ## Project Deep-Dive / biggest challenge?



  ## help peers