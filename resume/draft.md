# Resume Draft

## Education 
Duke University,  Master's, Electrical and Computer Engineering
August 2024 - May 2027
University of Electronic Science and Technology of China,  Bachelor's, Software Engineering
September 2020 - June 2024

## Internship Experience
### Research Intern   --> Microsoft (03/2026 --> 07/2026)
1. Architected HDMAS, a planner-free, decentralized multi-agent architecture using a lock-protected shared blackboard and distributed task claiming. Holding the GPT-5.4 Copilot backend constant, the three-agent system improved Row-F1 by 11.4% and Item-F1 by 8.0% over a single agent on 200 WideSearch tasks.
2. Built an automated evaluation pipeline for Excel web-search agents that decomposes tasks into atomic facts, generates and independently verifies reproducible ground truth, and scores answers extracted from execution traces; scaled to 50 tasks and 310 fact definitions while raising verified ground-truth coverage from 22.7% to 70.1%.
3. Post-trained Qwen2.5-7B (LoRA SFT + GRPO RL on verl/sglang, 4×A100 FSDP2) into a tool-using "code-act" web-search agent — built the custom multi-turn tool/agent-loop, reward function, and evaluation harness — lifting WideSearch f1 from 0.05 → 0.35 (SFT) → ~0.40 (RL).


### Software Engineer Intern    --> Alibaba Cloud(07/2025 --> 11/2025)
• Designed and implemented an A2A (Agent-to-Agent) protocol adapter for AgentScope Runtime(https://github.com/agentscope-ai/agentscope, 27k stars opensource agent sdk), enabling bidirectional translation between external protocols and internal agent architecture. Exposed JSON-RPC APIs via FastAPI with asynchronous streaming support to improve multi-agent collaboration and system integration.
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

1. controlled on the phone using telegram bot, easy to access, the main idea/main feature is includes human-in-the-loop, hand off the account login to user by a link via noVNC, and it can do and access much more things when logged in, which is fundamentally powerful than naive browseruse agent.
2. Integrating and improving broswerUse agent(opensource project,https://github.com/browser-use/browser-use) for manipulating browser, reducing batch task execute time by __%, using code-act pattern tool and skill system.
3. Observability: integrated Langfuse for llm tracing, given request id--> find tracing id --> to locate the bug/problems for production environment, evaluate cost
4. Develop CI/CD pipeline using Github Action, cutting down the deploy time(?) deploy the project on AWS EC2 for 24h responding.


### Mini-UPS Backend Development 
Team Leader Durham, NC, USA
January 2025 - April 2025
• Built core backend services using Spring Boot, implementing user management, package tracking, and delivery scheduling features, which laid the foundation for a fully functional logistics system.
• Designed and implemented asynchronous communication with Mini-Amazon and WorldSim using Google Protocol Buffers, achieving reliable instruction and status synchronization across systems.
• Introduced ACK-based confirmation and SEQ number management mechanisms, improving message reliability and increasing system concurrency and throughput.
• Developed a PostgreSQL-based persistence layer to store and manage user, package, and truck data, ensuring data consistency and traceability throughout the delivery lifecycle.
• Deployed the system using Docker Compose, enabling containerized, modular deployment and supporting scalable, cross-service integration during testing and runtime.