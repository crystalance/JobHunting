# Tool-Call Flow: Harness → vLLM → Model → Parser → Harness

How the `execute_python` tool call travels through the stack, with real examples
captured from the local `qwen25-7b` (Qwen2.5-7B-Instruct) vLLM server.

> **Key idea:** "function calling" is **not** a special model capability. It is a
> plain-text convention (`<tool_call>...</tool_call>`) that the chat template
> injects into the prompt, the model imitates as text, and a server-side parser
> converts back into structured JSON. Nothing about the model weights "knows"
> about JSON tool schemas — it only continues text patterns.

---

## The 5 stages

```
[1] Harness ──HTTP──▶ [2] vLLM applies chat template ──▶ [3] Model emits raw text
                                                                    │
[5] Harness ◀──HTTP── [4] vLLM hermes parser ◀──────────────────────┘
```

| # | Stage | Representation |
|---|-------|----------------|
| 1 | Harness → vLLM (API request) | OpenAI JSON: `messages` + `tools` |
| 2 | vLLM → model (rendered prompt) | flat text w/ `<tools>` defn + format instructions |
| 3 | Model → vLLM (raw generation) | plain text: `<tool_call>\n{...}\n</tool_call>` |
| 4 | vLLM hermes parser | text → structured `tool_calls[]` |
| 5 | vLLM → harness (API response) | OpenAI JSON: `message.tool_calls` |

---

## [1] Input prompt to the vLLM server (Harness → vLLM)

The harness (`SearchAgent`) calls the OpenAI-compatible endpoint via
`self.llm_client.safe_chat(messages, tools=_TOOLS)`. On the wire this is a
`POST /v1/chat/completions` with two relevant fields — the conversation
(`messages`) and the tool schema (`tools`):

```jsonc
{
  "model": "qwen25-7b",
  "messages": [
    { "role": "system", "content": "You are a Search Agent. ..." },
    { "role": "user",   "content": "Compute 17*23 with python." }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "execute_python",
        "description": "Execute Python code in a persistent IPython kernel. ...",
        "parameters": {
          "type": "object",
          "properties": {
            "thought": { "type": "string", "description": "Your reasoning ..." },
            "code":    { "type": "string", "description": "The Python code ..." }
          },
          "required": ["thought", "code"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

This is the *only* place the tool schema exists as structured JSON. The model
never sees this object directly — vLLM turns it into text in stage 2.

---

## [2] From vLLM server to the model (rendered prompt)

vLLM runs `tokenizer.apply_chat_template(messages, tools=...)`. The Qwen2.5
chat template **flattens the `tools` array into the system prompt** and appends
explicit formatting instructions. This is the exact string fed to the model
(captured from the running server):

```text
<|im_start|>system
You are a Search Agent.

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "execute_python", "description": "Run python", "parameters": {"type": "object", "properties": {"thought": {"type": "string"}, "code": {"type": "string"}}, "required": ["thought", "code"]}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call><|im_end|>
<|im_start|>user
Compute 17*23 with python.<|im_end|>
<|im_start|>assistant
```

Takeaways:
- The tool schema is now **plain text inside `<tools>`**.
- The template literally tells the model: *"return ... within
  `<tool_call></tool_call>` XML tags."* This instruction is why a *compliant*
  model produces the right shape — and why a model that ignores it (e.g.
  Qwen2.5-Coder-7B) fails.
- The trailing `<|im_start|>assistant\n` is the generation prompt: the model
  continues from here.

---

## [3] Raw response from the model (Model → vLLM)

The model just autoregressively continues the text. There is **no structure
yet** — it is a token stream. Captured raw generation (via `/v1/completions`
on the rendered prompt, i.e. bypassing the parser):

```text
<tool_call>
{"name": "execute_python", "arguments": {"thought": "Compute the product of 17 and 23.", "code": "17 * 23"}}
</tool_call>
```

At this raw layer the stop reason is just `stop` (the model emitted its end
token). To the model, this is indistinguishable from writing prose.

---

## [4] How the parser works (vLLM `--tool-call-parser hermes`)

The server was started with `--enable-auto-tool-choice --tool-call-parser hermes`.
The hermes parser:

1. **Scans** the generated text for `<tool_call> ... </tool_call>` blocks.
2. **Extracts** the JSON inside each block and `json.loads` it.
3. **Repackages** each into the OpenAI `tool_calls` schema, assigning a synthetic
   `id`, setting `type="function"`, `function.name`, and
   `function.arguments` (kept as a **JSON string**, not a dict).
4. **Rewrites** the response: any text consumed as a tool call is removed from
   `content` (so `content` becomes `null`), and `finish_reason` is switched
   from `stop` to `tool_calls`.

Before vs after, for the same request:

| Field | Raw (stage 3) | After hermes parser (stage 4) |
|-------|---------------|-------------------------------|
| text / `content` | `<tool_call>{...}</tool_call>` | `null` |
| `finish_reason` | `stop` | `tool_calls` |
| `tool_calls` | — | `[{id, type, function{name, arguments}}]` |

> **Requirement:** the parser only succeeds if the raw text matches the
> `<tool_call>{valid json}</tool_call>` pattern. Malformed JSON or a different
> wrapper (e.g. ` ```json ` markdown, or `<tool>` tags) → parser produces
> **no** `tool_calls` and leaves the text in `content`. See "Failure mode" below.

---

## [5] Final response to the harness (vLLM → Harness)

The harness receives the structured OpenAI response. Captured values:

```text
message.content    = None
finish_reason      = "tool_calls"
tool_calls[0].id       = "chatcmpl-tool-381078ad136d47beafc05bdac970e7c1"
tool_calls[0].type     = "function"
tool_calls[0].function.name      = "execute_python"
tool_calls[0].function.arguments = '{"thought": "Compute the product of 17 and 23.", "code": "17 * 23"}'
                                    ^^^ NOTE: a JSON *string*, must be json.loads'd
```

### How the harness consumes it (`search_agent/search_agent.py`)

```python
response = self.llm_client.safe_chat(messages, tools=_TOOLS)
assistant_msg = response.choices[0].message

# 1) Record the assistant turn (including its tool_calls) into history
msg_dict = {"role": "assistant"}
if assistant_msg.tool_calls:
    msg_dict["tool_calls"] = [
        {"id": tc.id, "type": "function",
         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
        for tc in assistant_msg.tool_calls
    ]
messages.append(msg_dict)

# 2) TERMINATION: no tool call => the model gave its final text answer
if not assistant_msg.tool_calls:
    break

# 3) Execute each tool call
for tc in assistant_msg.tool_calls:
    if tc.function.name == "execute_python":
        args   = json.loads(tc.function.arguments)   # string -> dict
        thought = args.get("thought", "")
        code    = args.get("code", "")
        exec_result = executor.run(code)             # runs in persistent IPython kernel
        tool_output = _format_exec_result(exec_result)

    # 4) Feed the result back as a tool message, linked by tool_call_id
    messages.append({
        "role": "tool",
        "tool_call_id": tc.id,
        "content": tool_output,
    })
# loop back to the next LLM call with the updated messages
```

The `tool_call_id` links the assistant's request to its result, so on the next
turn the model sees "call X produced output Y".

### Stage-2 rendering of the tool result (next turn)

When the loop iterates, the appended `role: "tool"` message is rendered back
into text for the model like this:

```text
<|im_start|>assistant
<tool_call>
{"name": "execute_python", "arguments": {"thought": "...", "code": "17 * 23"}}
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
391
</tool_response><|im_end|>
<|im_start|>assistant
```

The model now continues — either another `<tool_call>` or a plain-text final
answer (which triggers termination at step 2 above).

---

## Failure mode observed with open models

The whole chain depends on **stage 4 (parsing) succeeding**, which depends on
**stage 3 (raw text) being well-formed**.

- **Qwen2.5-7B-Instruct:** emits clean `<tool_call>{...}</tool_call>` → 6/6
  compliance with the raw harness prompt. Works.
- **Qwen2.5-Coder-7B-Instruct:** its code-instruct training makes it emit
  ` ```python ``` ` / ` ```json ``` ` markdown instead of `<tool_call>` tags →
  0/6 → parser gets nothing → harness sees no `tool_calls` → treats it as a
  final answer on turn 1 → the agent never runs. (This is why it was dropped.)
- **Multi-turn malformed call:** even a compliant model can occasionally emit a
  `<tool_call>` block with malformed JSON (e.g. a stray `"}}`). The parser
  rejects it, returns it as `content` with `tool_calls == []`, and the harness's
  `if not tool_calls: break` terminates the run prematurely (no output file).

### Hardening implication (P0)

`SearchAgent` should **not** treat "no parsed `tool_calls`" as an unconditional
"final answer." A robust fallback: when `assistant_msg.tool_calls` is empty but
`assistant_msg.content` contains a `<tool_call> ... </tool_call>` block, parse
that block manually (repair minor JSON issues) and execute it — only treating
the turn as final when there is genuinely no tool-call attempt. During RL, the
`format_ok` reward term additionally penalizes malformed calls so the policy
learns to emit clean ones.

---

## Reproduce these examples

```bash
# Server (conda new_verl):
CUDA_VISIBLE_DEVICES=0 vllm serve Qwen/Qwen2.5-7B-Instruct \
  --served-model-name qwen25-7b --tensor-parallel-size 1 --max-model-len 24576 \
  --gpu-memory-utilization 0.90 --enable-prefix-caching \
  --enable-auto-tool-choice --tool-call-parser hermes --port 8000

# Stage 2 — render the exact prompt the model receives:
python - <<'PY'
from transformers import AutoTokenizer
t = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct')
tools=[{'type':'function','function':{'name':'execute_python','description':'Run python',
  'parameters':{'type':'object','properties':{'thought':{'type':'string'},'code':{'type':'string'}},
  'required':['thought','code']}}}]
msgs=[{'role':'system','content':'You are a Search Agent.'},{'role':'user','content':'Compute 17*23.'}]
print(t.apply_chat_template(msgs, tools=tools, tokenize=False, add_generation_prompt=True))
PY

# Stage 3 (raw) vs Stage 5 (parsed) — same input:
python - <<'PY'
from transformers import AutoTokenizer
from openai import OpenAI
t = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct')
tools=[{'type':'function','function':{'name':'execute_python','description':'Run python',
  'parameters':{'type':'object','properties':{'thought':{'type':'string'},'code':{'type':'string'}},
  'required':['thought','code']}}}]
msgs=[{'role':'system','content':'You are a Search Agent.'},{'role':'user','content':'Compute 17*23 with python.'}]
c = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')
prompt = t.apply_chat_template(msgs, tools=tools, tokenize=False, add_generation_prompt=True)
raw = c.completions.create(model='qwen25-7b', prompt=prompt, max_tokens=200, temperature=0.0)
print('RAW:', repr(raw.choices[0].text))
chat = c.chat.completions.create(model='qwen25-7b', messages=msgs, tools=tools, temperature=0.0, max_tokens=200)
m = chat.choices[0].message
print('content:', repr(m.content), '| finish:', chat.choices[0].finish_reason)
print('tool_calls:', m.tool_calls)
PY
```
