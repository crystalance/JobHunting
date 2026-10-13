WEIKAI LIAO 
+1 (919) 672-8418 | lanceliao2002@gmail.com | Durham, NC, USA | linkedin.com/in/weikailiao/ EDUCATION 
Duke University                										        May 2027 Master's, Electrical and Computer Engineering 
University of Electronic Science and Technology of China 							        June 2024 Bachelor's, Software Engineering 
PROFESSIONAL EXPERIENCE 
Microsoft										               March 2026 - July 2026 Research Engineer Intern 
   • Built HDMAS, a decentralized multi-agent system using the GitHub Copilot SDK, where agents self-assign subtasks and share claims and findings through a blackboard to reduce coordination overhead; improved Row-F1 by 11.4% and Item-F1 by 8.0% over a single GPT-5.4 agent on 200 WideSearch tasks.
   • Engineered agent concurrency control with lock-protected task claiming and execution outside critical sections; improved fault tolerance through 60s lock TTLs, exit cleanup, and heartbeat monitoring that flags interrupted tasks for peers.
• Orchestrated Copilot agents to benchmark Microsoft’s Excel agent’s web search through parallel fact-filling, retries, and isolated verification; raised verified ground-truth coverage from 22.7% to 70.1% across 510 facts.
Alibaba Cloud 										        July 2025 - November 2025 Software Development Engineer Intern 
   • Built an A2A protocol adapter for AgentScope Runtime (32K+-star Agent framework) as a pluggable FastAPI protocol layer, choosing JSON-RPC over REST for A2A spec compliance and request-ID correlation; translates messages, task IDs, and task states between A2A and AgentScope schemas.
   • Co-built Bailian's one-click agent deployment from the AgentScope Runtime SDK to the platform backend, turning a local agent project into a public HTTPS API on Function Compute with one command.
   • Developed Bailian’s full-code agent management backend using Spring Boot, implementing search/filtering, SLR permission  validation, lifecycle management, and database CRUD with generated Mappers and indexes; unified visibility into Function  Compute deployment metadata and runtime status across 10K+ agent applications. 
PROJECTS & OUTSIDE EXPERIENCE 
Distributed Configuration Store				                                                                            July 2026 - Sept 2026 Team Leader 
• Built a linearizable replicated key-value store in Go using Multi-Paxos, implementing leader election, pipelined log replication, and crash recovery through write-ahead logging, snapshots, and log compaction.
• Implemented durable recovery with write-ahead logging, snapshots, and log compaction; Verified linearizability with the Porcupine checker under injected crashes, network partitions, and packet loss; sustained ~29K durable writes/s across 5 replicas with ~210 ms median recovery after leader failure.
BroswerUse Bot 										             March 2026 - May 2026 Team Leader 
• Built a supervised browser-automation agent with a messaging-based control interface and noVNC login handoff, extending browser-use with a CodeAct tool layer and reusable skills to reduce LLM round-trips by ~95% for batched tasks.
• Instrumented the LLM pipeline with Langfuse tracing (per-step tokens, latency, cost, errors), enabling request-ID ’ trace lookup  to debug production runs and attribute per-task cost. 
• Built a GitHub Actions CI/CD pipeline auto-deploying to AWS EC2 with health-check rollback, running the agent 24/7; reduced deployments to a single push (from manual multi-step to ~2 min, zero-downtime). 
SKILLS 
Programming Language: Java, C/C++, Python, JavaScript, SQL 
Technologies: Spring Boot, Django, FastAPI, Vue.js, React, MySQL, PostgreSQL, Redis, Elasticsearch, Docker, AWS, LLM Agents,  RAG, SFT, Langfuse, GRPO
