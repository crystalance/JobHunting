

# BQ

## category

### out of responsibility / take initiative / pursue the best / go beyond for a customer

1. Alibaba Cloud → Built AgentScope Runtime deployment tooling, automating packaging, OSS uploads, and serverless deployment on Bailian for one-click releases and versioning.

   **Story: turning a customer's permission complaint into a least-privilege policy for the deploy SDK**

   - **Situation**: I owned the SDK deploy tool. A colleague owned the deployment backend it calls. That backend uses OSS and Function Compute, and each of those services already enforces its own permissions. Which action points (权限点) the backend actually touches was a black box to me: many paths are interleaved in his code. For the moment he told me to have the deploying sub-account grant `AliyunOSSFullAccess` + `AliyunFCFullAccess`, and that is what the guide said.
   - **Trigger**: An early enterprise adopter complained that was too coarse. Their developers deploy from **RAM sub-accounts**, and security would not allow full access to every OSS bucket and every FC function. I heard the ticket and took it. I was the person most familiar with the deploy tool, so I could run the tool itself to discover the actions, which was faster than asking him to untangle the backend.
   - **Action**: I derived the **minimal permission set empirically, starting from zero**:
     1. Created a test RAM sub-account with **no permissions**, ran the deploy script, and let it fail.
     2. Each failure returns an `AccessDenied` log that names the **exact missing action and resource ARN** — e.g. first `oss:PutObject` on the artifact bucket, then `oss:GetObject` (FC pulls the code package from OSS at create time), then `fc:CreateFunction`, `fc:UpdateFunction`, `fc:GetFunction` (idempotent redeploy), `fc:CreateTrigger` (HTTP trigger), `fc:PublishFunctionVersion` (our versioning feature), and `ram:PassRole` (needed when binding the FC execution role to the function).
     3. Added exactly that one action, re-ran, repeated until the full deploy-→invoke-→update loop passed.
     4. Then **tightened the Resource scope**: OSS actions restricted to the specific artifact bucket/prefix (`acs:oss:*:*:{bucket}/agentscope-deploy/*`) instead of `*`, FC actions scoped to the function-name prefix our SDK generates; verified nothing else broke.
     5. Regression-tested the final custom policy end-to-end (fresh deploy, update-in-place, version publish), then documented it as a copy-pasteable RAM policy JSON in the deployment guide, replacing the "grant FullAccess" instruction. One caveat I hit and documented: the **service-linked role (SLR)** for FC must already exist — creating it the first time requires main-account (or explicitly granted) privileges, so the guide tells enterprise admins to do that once up front.
   - **Result**: Sub-account users could deploy with a policy scoped to ~8 actions on named resources instead of two FullAccess policies. The customer's security team accepted it, and the policy JSON went into the docs so every later enterprise user got it for free.
   - **Reflection (what I'd say in the interview)**: the permission points lived in a colleague's backend, and neither of us could list them by reading the code quickly. I could list them by driving the tool I owned. A failed deploy is a better inventory than a guess from the API docs, because the services already check every action.

   > Fits: taking initiative / customer obsession / going beyond assigned scope / attention to security detail.

   **Spoken version (~75 seconds)**

   At Alibaba, my assigned work was the deployment tool in the AgentScope SDK. The backend it called was owned by another engineer. At the time, our guide told users to give deployment sub-accounts broad access to object storage and Function Compute.

    A tech lead on an early enterprise customer’s agent team raised a concern: those sub-accounts belonged to his developers, and he felt the recommended permissions were much broader than they needed. Although the backend was outside my assigned work, this guidance affected whether his team could comfortably use the tool, so I took the initiative to investigate.

    I created a sub-account with no permissions and ran the deployment workflow. Each `AccessDenied` log identified a missing action and resource. I added one permission at a time, then repeated the process for a new deployment, an update, and version publishing. That let me build a policy around the **principle of least privilege** and update the guide with permissions tied to the operations the tool actually performs.

    The team now had a specific permission policy to review instead of a recommendation for full access, and future users could use the same guide. For me, the lesson was to take a customer’s concern seriously even when the code behind it sits outside my assigned area—and use the workflow I knew to find a concrete answer.

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

1. when i was doing HDMAS, the task is to explore the this decentralized architecture's performance, but at that time, i wasnt fully understand what does my mentor want, and i just build, --> multiple agents, coordinated by a shared blackboard. However, what i thought is to get a higher score on the benchmark, and not fully insisted this current architecture, in order to improve the effiency, i added a agent to collect each subagents output, just head down to work very hard to improve this wrong archiecture and test it on benchmark(iterate). Until a week later when i was sync with my mentor i realized this is just a vairation of planner-worker, it still has the single point of failure. And i wasted a whole week and biilions of tokens for that. and my mentor also has to postpond the important meeting with higher manager where he was supposed to share this architecure.

What I learned, and what i will imporve next time: 
Dont make assumptions on others goals, make sure you fully understand the goal(share a common goal with others) make sure 
you handle the property: here, the correctness is much more important than the performance.
And also be proactive, be transprant to what i am doing to mentor

**Spoken version (~90 seconds)**

> At Microsoft the project was to measure a decentralized design: peers share a blackboard, and no single agent can take the run down. I understood the build. I got the goal wrong. I treated the benchmark score as the thing to maximize.
>
> The flat system was slow, so I added one agent whose only job was to collect each peer's output and write the final table. Then I spent a week iterating on that version and running the benchmark. The score moved, so I thought I was on track.
>
> At the next sync my mentor looked at the diagram and said this was planner-worker again. He was right. The peers were still there, but the final answer now depended on one collector. If that agent failed, the run failed. That was the property the project existed to test, and I had removed it to go faster. It cost a week of runs and a large token bill, and he had to push a review with his manager, because what I had built was no longer the architecture he was going to present.
>
> I didn't defend the score. I deleted the collector the same day and reran the flat peers. What I changed after that is how I work, not just that diagram. I stopped assuming we wanted the same thing. Before the next long job I sent him one paragraph: what I was about to change, and which property it might break, so he wasn't hearing it a week later. And I kept the property in front of the score. The goal was to test that no single agent is required. A higher score that breaks that is a failed experiment, not a faster system. The runs after that kept the blackboard. I only changed how many peers I used. Performance is allowed to move. That property is not.


## Prioritization / Pressure / tight ddl




## Project Deep-Dive / biggest challenge?

HDMAS. Order: why planner-worker fails → architecture in one breath → started at 8 → too slow → logs → lock → cut to 3. Quality numbers are the verified ones (Row-F1 +11.4% relative, Item-F1 +8, 200 tasks).

Latency, if they ask you to reconcile: your April notes say easy cases of the **3-agent** run were about **6–8×** the single agent and hard cases about **1.3–1.5×**; **8 vs 3** is about **2×** wall-clock and **2.7×** tool calls (≈59.6 h → ≈117.5 h). The spoken line below uses your “about 6× / about 1.2×” pair. If they ask “eight versus three?”, switch to the 2× / 2.7× pair. Don’t quote both as the same comparison.

**Spoken version (~2 minutes)**

My biggest challenge on HDMAS was that fixing one race created the next bottleneck, and I had to keep the design anyway.

The goal was to answer wide-search questions more completely. A single agent often stopped before finding all the sources, so I built identical peers that share a blackboard and claim work under a lock, so two agents don't take the same subtask. There is no planner.

The first full run was a mess, and the mess was the final file. The claim lock only covered the blackboard. `answer/final.md` was a normal file, and the lock is advisory: if an agent doesn't call `lock_file`, nothing stops the write. Two peers read the same table, each wrote its own rows back, and the second write replaced the first. Rows we had already found disappeared.

I put the same lock around that file: lock, read, write, unlock. The output became consistent, and the run got slower, because every commit waited. I then ran eight peers, which is where I thought more searchers would help. It verified the cost. They spent the time lined up on that lock. Coverage of individual cells was fine. The final table was not, because too many writers were serializing on one file.

That result was a real reason to quit. The run was slower, the table was worse, and the obvious move was to drop the peers and go back to one agent. I didn't. The property I still wanted was a second context that keeps searching when one agent stops, and eight bad runs didn't tell me that property was false. I read the logs again instead of tearing the design out. Each agent was already capable of covering more than one source. Eight was more writers than the task needed. I cut it to three and reran. Same Copilot backend, 200 tasks: Row-F1 from 0.499 to 0.556, Item-F1 from 0.679 to 0.733, against the single agent. Three is enough for a second context to catch an early stop, without eight of them fighting over the answer file.

## help peers