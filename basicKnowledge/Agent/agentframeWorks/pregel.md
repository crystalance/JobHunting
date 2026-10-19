# Pregel, the LangGraph runtime

Source: [Building LangGraph](https://www.langchain.com/blog/building-langgraph) (Sep 2025) and the [Pregel runtime docs](https://docs.langchain.com/oss/python/langgraph/pregel). This is the loop behind the sentence in `langgraph-agentscope.md`.

A `StateGraph` compiles into this runtime. You write nodes and edges. Pregel is the thing that runs them. It is the Bulk Synchronous Parallel algorithm: each step is plan, run, then publish. Nodes in the same step never see each other's writes.

## The step

```text
channels = {}          # name -> {value, version}
seen = {}              # node -> {channel -> version it last read}
pending = []           # writes from the step that is running; invisible until publish

def invoke(input, thread_id):
    checkpoint = load(thread_id)          # missing on the first call
    if checkpoint: channels, seen = checkpoint
    else: write(input_channels, input)    # writing input is what wakes the first nodes

    for step in range(max_steps):
        ready = plan()
        if not ready:
            return read(output_channels)  # nobody is stale; the graph is idle

        snapshot = copy(channels)          # every node in this step reads this copy
        pending = []
        parallel_for node in ready:
            local = copy(snapshot)
            writes, events = node(local)  # the node mutates only its copy
            pending.append(writes)
            emit(events)                   # streaming, while the node is still running
            seen[node] = versions(snapshot)

        publish(pending)                   # deterministic order, not finish order
        save(thread_id, channels, seen)    # one checkpoint per step

def plan():
    # a node is ready when a channel it subscribes to is newer than what it last saw
    return [n for n in nodes if any(channels[c].version > seen[n][c] for c in n.subscribes)]

def publish(pending):
    for write in sorted(pending):          # sort key is stable, not "who finished first"
        channel = channels[write.channel]
        channel.value = channel.reducer(channel.value, write.value)
        channel.version += 1
```

Two nodes that both update `messages` do not race. Each reads the same snapshot. Both writes sit in `pending`. `publish` folds them with the channel's reducer, in a fixed order. Which node returned first does not change the next state.

The loop also stops at `max_steps`, so a cycle cannot spin forever.

## Where the six features sit

The same loop is the feature. Nothing below is a second engine.

```text
parallelization
    plan() may return many nodes
    they run on one snapshot
    publish() applies writes in a fixed order

streaming
    a node yields events while it runs (tokens, tool calls)
    publish() emits the state diff at the step boundary
    modes: values, updates, messages, tasks, checkpoints, custom

checkpointing
    save() writes channel values, channel versions, and seen[]
    serialized (msgpack), not a live process
    the next invoke loads that snapshot and plan() continues
    history length does not matter: only the latest checkpoint is read

human-in-the-loop
    interrupt(payload) is a node saying "stop after this step"
    save() runs, then invoke returns the payload
    the process does not stay up waiting
    resume(value) writes that value into the channel and calls invoke again
    plan() wakes the node that was waiting on it

tracing
    each step has a boundary: which nodes ran, what they read, what they wrote
    those events go to LangSmith, or out as OpenTelemetry
    a trace is the sequence of steps, not a print inside the model call

task queue
    not in this loop
    Pregel runs inside one process
    a queue is a separate worker that calls invoke(thread_id)
    so the HTTP request can return while the graph is still on step 4
    that worker is LangGraph Platform, or your own job runner
```

`interrupt()` only works because the step already ended in a checkpoint. A `while` loop that is paused mid-function cannot be moved to another machine. A finished step can: the next machine loads `channels` and `seen` and calls `plan()`.
