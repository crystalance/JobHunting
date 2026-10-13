# Resume with reviewer comments

Source: [Weikai_Liao_resume_1](https://docs.google.com/document/d/1HKmDaajTyVrDe97MAL2iEKeYp3OAygk-A_oaUim5ado/edit?tab=t.0). All 16 comments are from Alex Z, left on 2026-10-04. Each comment sits under the line it was anchored to, quoted as written.

---

## WEIKAI LIAO

> **Alex Z — overall comment**
> Overall comment. As of this very moment, I'll have to say your current skillset is still rather shallow compared to the expecations of NG AIE applications. To increase depth, I would incorporate one of the three following concepts into your resume points (anywhere is fine, especially in the cases where you have to remove something or pivot away from somewhere).
>
> 1) Dual-layer RAG, where retriever layer and reranker layer are separated; possibly even with another RDBMS system integrated (first SQL query and then RAG through query results, or paralelly then combine results); best accomplished using PostgreSQL + pgvector.
> 2) Orchestration of multi-agent system with LangGraph, where different agents have different roles, featuring in-depth implementation details on how the orchestration worked, and why designed the way they were designed.
> 3) Distributed systems project that deals with concepts such as membership lists, failure detection, concurrency control, leadership election and replica management (using Paxos/Raft). Best in C++ or Golang.
>
> Without at least one of these, you'll be at a disadvantage competing with others for AIE roles. For general backend SDE, you're missing even more so I would actually consider focusing your effort on preparign for AIE roles at this point.

+1 (919) 672-8418 | lanceliao2002@gmail.com | Durham, NC, USA | linkedin.com/in/weikailiao/

## EDUCATION

**Duke University** — May 2027
Master's, Electrical and Computer Engineering

**University of Electronic Science and Technology of China** — June 2024
Bachelor's, Software Engineering

## PROFESSIONAL EXPERIENCE

### Microsoft — Research Intern (March 2026 - July 2026)

> **Alex Z — on "Research Intern"**
> OK after reading the whole thing, unfortunately I'll have to break it to you that your most recent internship experience isn't really useful for your upcoming job finding if you plan on going for general SDE backend or AIE. This is very much MLE+Data-based role which use completely different techstack and focus on different parts from SDE / AIE. The only way I can think of rescuing this experience (as in not completely throwing it out) is by pivoting towards the benchmark / eval pipeline. You'll have to pull out at least 3 detailed points on how you built the benchmarking system and how did you evaluate the truth-verification process; consider adding downstream content such as LangSmith / LangFuse or similar to solidfy the "well-roundedness". If you don't think this is viable, then the other solution is to just throw out all the points and keep only the title; this way people know you've done something unrelated so you've saved the space for more relevant content.

- Architected HDMAS, a planner-free, decentralized multi-agent architecture using a lock-protected shared blackboard and distributed task claiming. Holding the GPT-5.4 Copilot backend constant, the multi-agent system improved Row-F1 by 11.4% and Item-F1 by 8.0% over a single agent on 200 WideSearch tasks.

  > **Alex Z — on "claiming. Holding"**
  > not a hard rule but I personally really don't like having more than one sentence in a single point.

  > **Alex Z — on "claiming. Holding"**
  > I would just connect with a semi-colon.

  **Revised (lead kept; follow-ups checked against `orchestrator.py`, `agent.py`, `prompts.py`, `lock_manager.py`, `config.py`, and the Copilot SDK JSON-RPC client):**

  - Built HDMAS, a decentralized multi-agent system using the GitHub Copilot SDK, where agents see peers' claims on a shared blackboard and self-assign subtasks to reduce coordination overhead; improved Row-F1 by 11.4% and Item-F1 by 8.0% over a single GPT-5.4 agent on 200 WideSearch tasks.
  - Orchestrated asyncio agents to lock the blackboard, claim one subtask, and unlock before executing; expired unreleased locks via 60s lease TTLs and multiplexed all sessions on one Copilot CLI over JSON-RPC/stdio.

- Built an automated three-stage benchmark generation pipeline that decomposes tasks into atomic facts, generates ground truth from the live web, and independently verifies each fact; increased verified ground-truth coverage from 22.7% to 70.1%.

  > **Alex Z**
  > See comment above.

  **Revised (checked against `ground_truth_agent/fill_loop.py`, `dispatcher.py`, `gt_agent.py`, `verifier.py`, `run_smallest_first.py`):**

  - Built a ground-truth pipeline for Microsoft's Excel agent benchmark, fanning 310 atomic facts to batched concurrent Copilot sessions with monotonic retries and an isolated verifier per value; raised verified coverage from 22.7% to 70.1%.

- Post-trained a batched code-act web-search agent on Qwen2.5-7B (LoRA SFT + GRPO): SFT improved F1 8× (5% to 40%); a custom-reward RL pass added +9% F1 while cutting per-query cost 14% and latency 9%.

### Alibaba Cloud — Software Development Engineer Intern (July 2025 - November 2025)

- Built an A2A protocol adapter for AgentScope Runtime, part of a 27K+-star open-source agent framework, enabling cross-framework agent interoperability through bidirectional JSON-RPC translation and asynchronous FastAPI streaming.

  > **Alex Z**
  > This is good

  > **Alex Z**
  > From the looks of things, you'll need to add some additional follow-up points on how the adapter was designed and why designed the way it was; consider adding a phrase along the lines of "utilized xx design methodology, selected over yy for its compatability with AA, BB business logic requirements...etc". Orelse you're missing too much info.

  **Revised (checked against `agentscope_runtime/engine/deployers/adapter/a2a/`):**

  - Built an A2A (Agent-to-Agent) protocol adapter for AgentScope Runtime, the deployment layer of the 30K+-star AgentScope framework, so any A2A client can discover a deployed agent through a well-known Agent Card and invoke it over a JSON-RPC `/a2a` endpoint.
  - Designed the adapter as a plugin that mounts A2A routes onto the agent's existing FastAPI app, so it ships inside the same serverless deployment with no separate gateway; chose JSON-RPC over REST because A2A specifies it as the default transport and one endpoint covers send, get, and cancel with request-ID correlation.
  - Implemented bidirectional translation between A2A and AgentScope schemas (context/task IDs to session/response IDs, Parts to Content, run status to TaskState), consuming the Runtime's async event stream and returning only the completed message so a failed run never publishes a partial answer; the runtime owns the Agent Card's capability flags, so an agent cannot advertise streaming the endpoint does not serve.

- Built AgentScope Runtime deployment tooling, automating packaging, OSS uploads, and serverless deployment on Bailian for one-click releases and versioning.

  > **Alex Z**
  > This is full-on deployment framework which is more on the DevOps side of things, so unfortunately this point isn't very usable either.

- Developed Bailian's full-code agent management backend using Spring Boot, implementing search/filtering, SLR permission validation, lifecycle management, and database CRUD with generated Mappers and indexes; unified visibility into Function Compute deployment metadata and runtime status across 10K+ agent applications.

  > **Alex Z — on "and database CRUD with generated Mappers and indexes"**
  > this part should be a seperate point as well, delving into the domain-layer design, including DAO/DTO design patterns.

  > **Alex Z — on "unified visibility into Function Compute deployment metadata and runtime status across 10K+ agent applications."**
  > This should technically also be in a separate point on traceability framework; but I guess it is ok to be attached to either of the two split off points for this particular case.

### BoulderAI Technologies — Software Engineer Intern (April 2024 - June 2024)

- Built LLM-driven enterprise automation pipelines using FastGPT, orchestrating prompt workflows to translate natural language into BPMN diagrams and reduce manual process modeling effort by 40%.

  > **Alex Z — on "orchestrating prompt workflows"**
  > context engineering I suppose, so I would add some follow-up point on designing the structured output and an evals pipeline.

- Built a RAG-powered Excel data extraction tool to identify and structure logical entities from headers, using LLMs to generate and classify structured JSON outputs for data integration.

  > **Alex Z — on "RAG-powered Excel data extraction tool"**
  > The way you described things here is a bit off. I would instead state "Build an Excel-based data extraction tool attached to a RAG pipeline which identifies .... and generates structured JSON outputs ....". And then, might as well add another follow-up point describing how the pipeline was orchestrated along with structured output design patterns. (from the previous comment too).

## PROJECTS & OUTSIDE EXPERIENCE

### BroswerUse Bot — Team Leader (March 2026 - May 2026)

- Built a supervised browser-automation agent controlled via Telegram, with a noVNC-based human-in-the-loop login handoff for authenticated sessions.

  > **Alex Z**
  > Ehhh, from a non-technical perspective, anything related to Telegram isn't very looked well upon since its reputation is really bad. If I were you I would try to frame the experience through a different platform.

- Extended the open-source browser-use agent with a CodeAct tool layer and reusable skills, cutting LLM round-trips by ~95% and increasing task yield from 1 to 14 grounded results.

  > **Alex Z — on "increasing task yield from 1 to 14 grounded results."**
  > what sort of skills did you employ to accomplish these impacts? Not very clear either (LLM round-trips doesn't really impact task yield, does it? Task yield is per task rather than per unit time)

- Instrumented the LLM pipeline with Langfuse tracing (per-step tokens, latency, cost, errors), enabling request-ID → trace lookup to debug production runs and attribute per-task cost.

  > **Alex Z**
  > This is good

- Built a GitHub Actions CI/CD pipeline auto-deploying to AWS EC2 with health-check rollback, running the agent 24/7; reduced deploys to a single push (from manual multi-step to ~2 min, zero-downtime).

  > **Alex Z**
  > Unfortuantely this is also DevOps content, though for a personal project I would say ok to keep as is, just that it's not likely to help out much during job finding.

## SKILLS

**Languages:** Python, Go, Java, C/C++, JavaScript, SQL

**Technologies:** FastAPI, Spring Boot, JSON-RPC, LLM Agents, Langfuse, MySQL, PostgreSQL, Redis, Docker, AWS
