

# BQ

## category

### out of responsibility / take initiative / pursue the best

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