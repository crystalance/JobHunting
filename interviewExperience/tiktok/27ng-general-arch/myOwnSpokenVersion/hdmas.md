1. briefly introduce it/ and results 
    1. HDMAS solves wide-search tasks — the answer is a table collected from many independent web sources, and a single agent fails because its context fills up and it stops before the table is complete.
    2. So we run N identical agents — no planner, no roles. They coordinate through one shared blackboard: a JSON file protected by an OS-level file lock. Each agent repeats two steps. Claim: lock the blackboard, read the tasks already claimed by others, derive the next to-do, append it, unlock. Execute: do the work with its own tools, then mark the entry done.
    3. Coordination is serialized by the lock, but execution runs in parallel — and that's the trade-off we measured. With the same model backend, 3 agents beat a single agent by 11 percent relative Row-F1 on 200 tasks. At 8 agents, cost roughly doubled and exact-match got worse, because agents spend their time waiting on the lock. So the architecture wins at small N, and the bottleneck is the shared answer file, not retrieval.

       2. why goes planner free
           1. distribute the planning, and make the cost of replanning low,  
       3. why goes homogenous?
           1.  scale out easily for different tasks with 