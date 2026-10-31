## basic idea

From the TikTok Shop search JD (`interviewExperience/tiktok/27-ng-econ/JD.md`). Two systems, not one.

- Query understanding: multi-turn, cross-lingual, a reasoning chain into search tools. Quantization, KV cache, and continuous batching are how that model is served. The KV cache dies with the request.
- Personalized memory: the shopper, kept across requests. Long-term profile, this session's clicks and questions, and a feature pipeline over behavior events. MemAgent ([arXiv 2507.02259](https://arxiv.org/abs/2507.02259)) is the long-text pattern cited there: read in segments, overwrite a fixed memory. It is not the KV cache and not the feature pipeline.

## 1. Where memory sits in the loop

LLM, tools, planning, and execution are the loop. Memory is the state that loop reads before the model call and writes after it. There is no fifth step that "runs memory."

Three layers, and only the first one is the ReAct loop you already know.

| Layer | What it holds | Lifetime | Who reads it |
|---|---|---|---|
| Working | This turn's messages: user, assistant tool calls, tool results | This loop, inside the window | The next model call |
| Session | The transcript, plus a summary once it is compacted | Across turns, one conversation | Loaded before the loop starts |
| Long-term | User profile, facts, retrieved chunks | Across conversations | Injected into the prompt; retrieved, not replayed |

### Working memory vs session memory

Working memory is the message list for this model call. Session memory is the saved transcript that list is loaded from, and written back to, so the next turn can start.

During one ReAct loop they are almost the same list. The user message is appended, the assistant tool call is appended, the tool result is appended, and that whole list is what `llm(context)` sees. In pi that object is `currentContext.messages`. It lives in the process. When the loop ends, that object is gone.

Session memory is the copy on disk. Pi's `AgentSession` appends each of those messages to `SessionManager` as they happen, as entries in a tree (JSONL or SQLite). The next user message does `load(session_id)` and that load becomes the new working list. A restart in between still has the conversation. The working list does not.

They split as soon as the window is full. Compaction, in `prepareNextTurn`, replaces the old prefix of the working list with a summary plus the recent tail. The next model call sees the short list. The session keeps the compaction entry and the earlier entries under it. Working memory is the view for this call. Session memory is the record you can reopen.

Planning is a write into working memory. A ReAct thought, or a to-do list, is an assistant message. The next call sees it because it is in the list, not because a planner process is still running.

Tools are the other write. The model does not remember a tool result on its own. The loop appends the result as a message. The next call is a new model invocation over that longer list.

The KV cache is not any of these layers. It is the serving trick that avoids recomputing tokens already in the prompt. Drop the conversation from the session store and the cache is gone too.

### Pseudocode

The basic ReAct loop is the inner `while`. Memory is the lines before it, the appends inside it, and the save after it.

```text
session = load(session_id)                    # session layer
context = session.messages
           + agents_md                          # human-written, cross-session
           + retrieve(user_id, query)           # long-term: profile, facts, chunks

while true:
    context = prepare_next_turn(context)        # compact here if the window is full
    response = llm(context)                     # one call; planning is inside this text
    context.append(response)
    persist(response)

    if response has no tool calls:
        break

    for call in response.tool_calls:            # parallel when the calls do not depend on each other
        result = tools[call.name](call.args)
        context.append(result)                  # working memory for the next call
        persist(result)

save(session_id, context)
```

`retrieve` is the long-term layer. Omit it and the loop is still a correct agent. It only knows this conversation. `prepare_next_turn` is where a long session becomes a summary plus the recent tail. The summary is still session memory. It replaces old messages. It does not become a user profile.

### What pi actually does

Source: [earendil-works/pi](https://github.com/badlogic/pi-mono), read 2026-10-21. The loop is `packages/agent/src/agent-loop.ts`, `runLoop`. The session is `packages/coding-agent/src/core/agent-session.ts`.

Pi has working memory and session memory. It has no long-term memory store. Searching the SDK for "memory" finds `SessionManager.inMemory()` and a credential store, which are backends, not a belief the agent writes.

The loop matches the pseudocode above, with these names:

- `currentContext.messages` is the working list. Tool results are pushed onto it before the next `streamAssistantResponse`.
- `prepareNextTurn` runs before the next assistant turn. Compaction is this hook. The comment in the loop says preparation can be long-running, for example compaction.
- `prepareRequest` can rewrite the context one more time before the provider call. Extensions use the `context` event for the same job.
- `getSteeringMessages` and `getFollowUpMessages` are the user talking during the loop. Those messages are appended before the next model call, same as a tool result.
- `AgentSession` appends every message to `SessionManager`. The store is a tree of entries (`id`, `parentId`), JSONL or SQLite, not a flat log. A fork inherits the branch it was cut from.

Compaction is the session-layer write. `packages/agent/src/harness/compaction/compaction.ts` asks a model for a prose summary, then attaches `readFiles` and `modifiedFiles` parsed from the tool calls (`extractFileOpsFromMessage`). The file list is not left to the model. After compaction, the context the next call sees is the summary, that manifest, and the retained tail.

The only built-in text that survives across sessions is `AGENTS.md` / `SYSTEM.md`, loaded by `resource-loader.ts`. A person writes those files. The agent does not update them as a memory loop. A plugin that wants user facts injects them on the `context` event and can react at `session_before_compact`. Pi does not retrieve, rank, or delete those facts. That gap is the long-term layer in the table, and it is the layer the TikTok bullet is hiring for.

Spoken answers for the Tencent memory set (questions 15–20) are in `腾讯Agent开发校招面经题汇总 (1).md`, section 四. The names there map onto this note: 短期上下文 is working memory, 持久化任务状态 is the session plus a task cursor, 长期记忆 is the profile and the retrieved facts.

### What compression keeps

Keep the system constraints, the current user goal, the unfinished plan, the latest tool result the next step needs, the cited chunk id and its text, and the task cursor. The file list is parsed from tool calls, the same way pi builds `readFiles` and `modifiedFiles`. Drop old turns once they are in the summary, bulky tool output after the conclusion is saved, low-score chunks, and duplicate tool calls. The citation rule and the cursor are not left only inside the summary prose.

A full window is handled in that order. A sliding window drops the oldest messages and can drop the goal, so it is the fallback. Summary compaction, in `prepareNextTurn`, replaces the prefix with a summary plus the recent tail. Facts that must outlive the conversation go to the long-term store and come back by retrieval. Retrieval does not replace the current turn's tool results.

### Expiry, update, delete, isolation

Session cache entries can expire. Facts carry `valid_until` and lose rank by age. They stay in the store. Profile fields overwrite. A new fact is a new version; the old row is marked superseded. Retrieve reads the latest. A user "forget" is a tombstone filtered at retrieve time. Deleting the vector row leaves the fact in the session transcript, so compaction and export have to honor the tombstone. Compaction appends a summary entry. It does not erase the tree.

Every row has `user_id` and `tenant_id` taken from the auth token. The filter runs before any text reaches the model.

### Resume a long task

A hundred files do not resume from the in-process message list. The checkpoint is `{task_id, cursor, completed_ids, failed_ids}`, committed after each file. The file write uses an idempotency key and happens before the cursor advances, so a crash between them retries the same write. Restart loads the checkpoint, skips what is done, and continues at file 81. The new working list is the constraints, a one-line progress summary, and the cursor. The session log remains for audit. Replaying eighty tool results into the window is how the window fills. Pi's append-only session keeps that log. LangGraph's per-step checkpoint (channel values, versions, what each node has seen) is the same idea for a graph: a finished step can move to another process, a function paused mid-call cannot.

## 2. RAG

1. Learn the whole system, how to choose different
