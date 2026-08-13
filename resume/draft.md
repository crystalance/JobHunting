# Resume Draft

## Education 
Duke University,  Master's, Electrical and Computer Engineering
August 2024 - May 2027
University of Electronic Science and Technology of China,  Bachelor's, Software Engineering
September 2020 - June 2024

## Internship Experience
### Research Intern   --> Microsoft (03/2026 --> 07/2026)
1. Architected HDMAS, a planner-free, decentralized multi-agent architecture using a lock-protected shared blackboard and distributed task claiming. Holding the GPT-5.4 Copilot backend constant, the three-agent system improved Row-F1 by 11.4% and Item-F1 by 8.0% over a single agent on 200 WideSearch tasks.
2. Built a three-stage pipeline that auto-generates agent benchmarks with zero human annotation — LLM decomposes tasks into atomic facts, a ground-truth agent fills them from the live web, and an isolated verifier independently re-checks each before freezing as gold — raising verified ground-truth coverage from 22.7% to 70.1% (50 tasks, 310 facts).
3. Built and post-trained a batched code-act web-search agent on Qwen2.5-7B (LoRA SFT + GRPO RL; verl/sglang/vLLM, 4×A100 FSDP2) — SFT taught for-loop batched search, lifting F1 from 5% to 40% (8×), and a custom-reward GRPO pass made it simultaneously more accurate (+9% F1) and ~14% cheaper / 9% faster per query.

### Software Engineer Intern    --> Alibaba Cloud(07/2025 --> 11/2025)
• Built an A2A protocol adapter for AgentScope Runtime, part of a 27K+-star open-source agent framework, enabling cross-framework agent interoperability through bidirectional JSON-RPC translation and asynchronous FastAPI streaming.
• Built deployment tooling for agent applications in AgentScope Runtime, automating the full pipeline from Python wheel packaging and OSS pre-signed uploads to serverless deployment orchestration on the Bailian platform, enabling one-click release, versioning, and rapid iteration.
• Contributed to the Bailian platform’s full-code agent management console, implementing application search and status filtering, SLR permission validation, lifecycle management, and unified visibility into Function Compute (FC) deployment metadata and runtime status.
• Integrated platform-level AI safety guardrails, supporting customizable keyword blocking and policy configuration, and enabling controlled content moderation responses to improve agent application security and compliance.


### Software Engineer Intern     --> BoulderAI Technologies(April 2024 - June 2024)
• Designed and implemented prompt pipelines using the FastGPT framework for LLM-driven enterprise automation, enabling dynamic natural language processing and task execution.
• Led the prompt engineering and AI workflow orchestration to translate natural language into BPMN diagrams, automating business process modeling and reducing manual effort by 40%.
• Built a RAG-powered data extraction tool to identify and structure logical entities from Excel headers. Designed effective prompts for LLMs to generate and classify JSON outputs, streamlining data integration.
• Developed a contract analysis automation system using the Eimos low-code platform, customizing prompts to extract key legal terms and summaries, cutting manual review time by 60%.


## Project Experience

### BroswerUse Bot
April 2026 - July 2026

1. Built a supervised browser-automation agent controlled from a phone via a Telegram bot, with a human-in-the-loop login handoff: streams the live browser to the user over noVNC through a one-tap link so they authenticate directly, letting the agent operate on logged-in, authenticated sessions that a naive autonomous agent cannot reach.
2. Extended the open-source browser-use agent with a CodeAct-style tool layer (agent-authored JavaScript over CDP) and a reusable skill system, cutting LLM round-trips ~95% via bulk DOM operations and raising task yield from 1 to 14 grounded results.
3. Instrumented the LLM pipeline with Langfuse tracing (per-step tokens, latency, cost, errors), enabling request-ID → trace lookup to debug production runs and attribute per-task cost.
4. Built a GitHub Actions CI/CD pipeline auto-deploying to AWS EC2 with health-check rollback, running the agent 24/7; reduced deploys to a single push (from manual multi-step to ~2 min, zero-downtime).

### Mini-UPS Backend Development 
Team Leader Durham, NC, USA
January 2025 - April 2025
• Built core backend services using Spring Boot, implementing user management, package tracking, and delivery scheduling features, which laid the foundation for a fully functional logistics system.
• Designed and implemented asynchronous communication with Mini-Amazon and WorldSim using Google Protocol Buffers, achieving reliable instruction and status synchronization across systems.
• Introduced ACK-based confirmation and SEQ number management mechanisms, improving message reliability and increasing system concurrency and throughput.
• Developed a PostgreSQL-based persistence layer to store and manage user, package, and truck data, ensuring data consistency and traceability throughout the delivery lifecycle.
• Deployed the system using Docker Compose, enabling containerized, modular deployment and supporting scalable, cross-service integration during testing and runtime.