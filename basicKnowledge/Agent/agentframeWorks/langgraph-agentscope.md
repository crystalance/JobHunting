# Agent frameworks: LangChain, LangGraph, AgentScope

Sources: [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview), [LangChain products](https://docs.langchain.com/oss/python/concepts/products), [Building LangGraph](https://www.langchain.com/blog/building-langgraph) (Sep 2025), [AgentScope key concepts](https://doc.agentscope.io/tutorial/quickstart_key_concept.html), [AgentScope 1.0 paper](https://arxiv.org/html/2508.16279).

## What a framework is for

An agent framework does not decide the answer. The model does. The framework is the code around the model: call it, run the tools it asked for, put the results back, and stop.

A hand-written agent is a loop:

```text
messages = [system, user]
while steps < cap:
    reply = model(messages, tools)
    if reply has no tool call: return reply
    results = run(reply.tool_calls)
    messages.append(results)
```

That loop is enough for one chatbot, a few tools, and a request that finishes in one turn. LangChain’s own design note says the main alternative to any framework is no framework.

You pick up a framework when that loop has to survive production:

- The model call takes seconds or minutes, so you stream tokens and run independent tools in parallel.
- A failure on the last step should resume from a checkpoint, not restart and pay for the whole run again.
- A person must approve a tool, edit the next step, or interrupt, then continue from the same state.
- Some steps are ordinary code (a checklist, a citation check) and some steps are the model. You want both in one run, with an explicit branch between them.
- You need a trace of every model call and tool call, or the same loop must work against more than one model provider.

## Basic components

These show up in every serious stack. Names differ.

| Piece | Job |
|---|---|
| Model adapter | One interface over OpenAI, Anthropic, and others: chat, tool calls, streaming. |
| Messages | The transcript the model sees. Text, tool calls, tool results. |
| Tools | A name, a JSON schema, and a function. Plus what happens when the function throws. |
| Loop | Reason, act, observe, stop. The stop rule is a max step count, “no more tool calls,” or a structured final answer. |
| State | Working memory for this run: messages, retrieved passages, which rubric item is next. |
| Orchestration | What runs after what. A plain loop, or a graph with branches and parallel nodes. |
| Checkpoint | A snapshot so a crash or a human pause can resume. |
| Trace | Inputs, tool calls, and outputs for debugging and eval. |

Deployment extras, not required to start: a session store, a sandbox around tools, and a queue so the agent is not tied to one HTTP request.

## LangChain, LangGraph, AgentScope

Current LangChain docs (2026) stack their own libraries as three layers:

- **LangChain** is the framework. `create_agent` is a model-and-tools loop, plus middleware for guardrails, retries, and human review. It is built on LangGraph. Use it when the agent is “call tools until done.”
- **LangGraph** is the runtime under that loop. You define state, nodes, and edges. A node can be a Python function, one model call, or a whole agent. Use it when the path is not a single loop: a code step, then a branch, then an agent, with checkpoints and interrupts. LangChain tells beginners to start with `create_agent`, and to drop to LangGraph only for that control.
- **LangGraph’s own runtime** (Pregel) runs the graph in steps: plan which nodes are ready, run those nodes in parallel, then publish their writes. That is how parallel tools avoid racing on the same state. Checkpoints, streaming, and `interrupt()` sit on this runtime. Their production shortlist is parallelization, streaming, a task queue, checkpointing, human-in-the-loop, and tracing. Pseudocode: [pregel.md](pregel.md).

**AgentScope** (1.0, Alibaba) is a ReAct framework, not a graph runtime.

- Building blocks are message, model, memory, and tool.
- An agent implements `reply`, `observe` (hear other agents without answering), and `print`. ReAct splits `reply` into `_reasoning` (model, maybe tool calls) and `_acting` (run the tools). Real-time steering is `handle_interrupt`.
- Multi-agent is normal: agents pass messages. Built-in agents (browser, deep research) are ReAct agents with extra tools and prompts.
- **AgentScope Runtime** is the deploy layer: a Runner for lifecycle, sessions, and streaming, plus a sandbox for tools. Studio traces runs. This is the layer an A2A adapter mounts onto.

| | Hand-written loop | LangChain `create_agent` | LangGraph | AgentScope |
|---|---|---|---|---|
| You write | The while-loop | Tools and a prompt | Nodes, edges, state | A ReAct agent and its tools |
| Control flow | One loop | One loop, middleware around it | Any graph: branch, parallel, nested agent | Reasoning then acting; agents message each other |
| Resume after a crash | You build it | Inherited from LangGraph if you turn persistence on | Checkpoint per step | Session state in the Runtime |
| Human approval | A flag you check | Middleware | `interrupt()` and resume | `handle_interrupt` |
| Multi-agent | You invent the protocol | Possible, not the center | Nodes or subgraphs | `reply` / `observe` messages |
| Fit | One bot, few tools, you own the stop rule | Ship a tool-calling chatbot quickly | Checklist node plus model node, long jobs, approvals | ReAct agents, multi-agent apps, deploy on AgentScope Runtime |

CrewAI, OpenAI Agents SDK, Google ADK, and LlamaIndex sit in the same “framework” row as LangChain: a loop, tools, and a higher-level style. Temporal and Inngest sit in the same “runtime” row as LangGraph: durable execution, not an LLM API.

## Why LangGraph, for this kind of product

The attendee bot is mostly a loop: search the rules, maybe read the checklist, answer with a citation. LangChain or a short handwritten loop covers that. LangGraph earns its place on the steps that are not the model. The missing-file list is a database diff. The deadline is a field, not a sentence to parse. The citation check rejects a quote that is not in the retrieved text. Those are nodes with a fixed result. The model node runs only when the question needs an explanation. The edge between them is the product rule: no citation, no answer.

The judge job is the same shape. For each rubric item: retrieve, ask the model, check that the quote is a substring, then save the packet. A crash on item 6 should resume at item 6. That is a checkpointed graph, which is what LangGraph is for. AgentScope fits if the team is already deploying on its Runtime and the agents are ReAct loops that message each other. It does not draw the checklist-versus-model branch as a graph. You would encode that branch inside `_reasoning` and the tools.
