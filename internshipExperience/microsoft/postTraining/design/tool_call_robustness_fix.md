# Design: Tool-Call Robustness Fix (malformed / multi-turn tool calls)

**Status:** proposed · **Date:** 2026-07-05 · **Scope:** harness hardening (P0)
**Owner file targets:** `llm_client/llm_client.py` (`OpenAICompatClient`), `search_agent/search_agent.py` (safety net)

---

## Problem

During the `ws_en_003` baseline run, `SearchAgent` stopped after 2 turns with no
output CSV. Root cause = two distinct issues:

1. **Harness fragility (engineering).** The agent loop treats "no *parsed*
   `tool_calls`" as "the model gave its final answer" and `break`s. This is an
   unconditional assumption that is wrong for open models served via vLLM.
2. **Model format reliability (model quality).** Qwen2.5-7B occasionally emits a
   `<tool_call>` block inside message *content* with malformed JSON (e.g. a stray
   `"}}`). vLLM's hermes parser rejects it, returns it as `content` with
   `tool_calls == []`, and the harness then terminates.

> These are **not** fixed by SFT/RFT or by switching to Qwen3-8B. Any model
> malforms occasionally (worse at RL sampling temp ≈ 1.0), and Qwen3-8B does not
> run on the current vLLM 0.8.2 / verl 0.2.0 stack. This is an engineering fix.
> The RL `format_ok` reward later reduces the *rate* of malformed calls, but the
> harness must be robust regardless.

---

## Where the bugs live (current code)

`search_agent/search_agent.py`, inside `SearchAgent.run`'s main loop:

| Spot | Approx line | Issue |
|------|-------------|-------|
| Termination | ~360 | `if not assistant_msg.tool_calls: break` — parser miss = "done" |
| Arg parsing | ~368 | `args = json.loads(tc.function.arguments)` — crashes on malformed JSON |
| Duplicated wrap-up | ~400+ | `stop_event` path repeats both of the above |

---

## Architectural decision

Put **response normalization inside `OpenAICompatClient`** (the new code we
added), NOT in the frozen harness. The client returns a response whose
`.tool_calls` is already populated with *valid* arguments, so the harness's
existing `if not tool_calls` logic becomes correct with only a tiny safety net.

Rationale:
- The malformed-tool-call issue is an **open-model quirk** → belongs at the
  open-model client boundary.
- Keeps the harness tool-surface **frozen** (`train-frozen-v1`), so collected
  rollouts stay valid.
- **Model-agnostic**: works for Qwen2.5-7B now and any future model (incl.
  Qwen3-8B once the stack supports it).

```
OpenAICompatClient.safe_chat()
   └─ response arrives
      ├─ [Layer 1] .tool_calls present?  → validate/repair each arguments JSON, return
      └─ [Layer 2] .tool_calls empty but content has <tool_call>…?
                   → recover: extract → repair JSON → inject synthetic tool_calls
                             → strip the raw block from content → return
Harness (safety net)
   └─ tolerant json.loads; on unrecoverable args, feed an error tool-message back
      to the model instead of crashing/terminating
```

---

## Layer 1 — tolerant JSON repair (`_safe_json_parse`)

Repair ladder, cheapest first. Exploits that we *know* the `execute_python`
schema is `{thought, code}`.

```python
def _safe_json_parse(s: str) -> dict | None:
    # 1) fast path
    try:
        return json.loads(s)
    except Exception:
        pass
    # 2) trim to outermost braces + balance them
    try:
        t = s[s.find("{"): s.rfind("}") + 1]
        t = _balance_braces(t)   # match { } counts; drop trailing commas
        return json.loads(t)
    except Exception:
        pass
    # 3) schema-targeted regex fallback (robust for our 2-field tool)
    m_code = re.search(r'"code"\s*:\s*"(.*?)"\s*[},]', s, re.DOTALL)
    m_th   = re.search(r'"thought"\s*:\s*"(.*?)"\s*[,}]', s, re.DOTALL)
    if m_code:
        return {"thought": _unescape(m_th.group(1)) if m_th else "",
                "code": _unescape(m_code.group(1))}
    return None
```

- Step 2 handles the exact stray-`"}}` case.
- Step 3 extracts `code` directly if JSON is unsalvageable.
- Optional: use the `json_repair` library instead of `_balance_braces`
  (dependency vs. maintenance trade-off — default plan is dependency-free).

---

## Layer 2 — recover tool calls from content (`_recover_tool_calls_from_content`)

When the hermes parser returns nothing but the model clearly attempted a call:

```python
_TOOLCALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)
# secondary patterns for robustness: <tool>…</tool>, ```json … ```, bare {…"code"…}

def _recover_tool_calls_from_content(content: str) -> list[_RecoveredToolCall]:
    out = []
    for block in (_TOOLCALL_RE.findall(content) or _fallback_blocks(content)):
        parsed = _safe_json_parse(block)
        if not parsed:
            continue
        args = parsed.get("arguments", parsed)      # tolerate both shapes
        if "code" in args:
            out.append(_RecoveredToolCall(
                id=f"recovered-{uuid.uuid4().hex[:8]}",
                name=parsed.get("name", "execute_python"),
                arguments=json.dumps(args)))         # re-serialize clean JSON
    return out
```

`_RecoveredToolCall` mirrors the OpenAI SDK shape so the harness consumes it
identically:

```python
@dataclass
class _RecoveredFunction:
    name: str
    arguments: str   # JSON string, like the real SDK

@dataclass
class _RecoveredToolCall:
    id: str
    function: _RecoveredFunction
    type: str = "function"
    def __init__(self, id, name, arguments):
        self.id = id; self.type = "function"
        self.function = _RecoveredFunction(name, arguments)
```

The client then **injects** these into the returned message and **clears the raw
`<tool_call>` text** from `content`, so conversation history stays clean and
`tool_call_id`s line up on the next turn.

---

## Harness safety net (minimal change)

In `search_agent/search_agent.py`, replace the hard `json.loads` with a tolerant
parse and degrade gracefully instead of crashing/terminating:

```python
args = _safe_json_parse(tc.function.arguments)
if args is None:
    tool_output = ("[error] Your tool call arguments were not valid JSON and "
                   "were not executed. Re-issue the execute_python call with valid JSON.")
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": tool_output})
    continue   # keep loop alive; model self-corrects next turn
thought = args.get("thought", "")
code    = args.get("code", "")
```

The termination check `if not tool_calls: break` stays — it is now *correct*
because the client guarantees `tool_calls` is populated whenever the model
attempted one. Apply the same two-line tolerance to the duplicated `stop_event`
wrap-up path (or factor tool execution into a shared helper).

---

## Observability (feeds P1 metric + RL reward)

Emit events / per-trajectory flags:

| Flag | Meaning | Downstream use |
|------|---------|----------------|
| `format_recovered` | Layer 2 fired (parser miss, content-recovered) | P1 format-validity %, RL `format_ok` |
| `json_repaired` | Layer 1 repaired malformed args | same |
| `malformed_unrecoverable` | fed error back; model got a retry | same + reward penalty |

These directly populate the design doc's **format-validity %** (P1 gate) and the
**`format_ok`** RL reward term — so robustness handling *becomes* the format
signal, replacing any need for format-teaching SFT.

---

## Why this is the right shape

- **Deterministic + free** — no GPU, no labelled data, no model swap.
- **Frozen-harness-friendly** — quirk handling lives in the new client; harness
  gets only a ~4-line safety net.
- **Model-agnostic** — works now and for future models.
- **RL-ready** — recovery/repair flags become the format signal RL consumes.

---

## Test plan

1. **Unit** `_safe_json_parse`: the real failing string (stray `"}}`) + synthetic
   malformations (missing `}`, trailing comma, unquoted). Expect a valid dict or
   a clean `None`.
2. **Unit** `_recover_tool_calls_from_content`: feed the recorded turn-2 `content`
   from `search_agent/batch_results/qwen25_7b_ws_en_003/ws_en_003/agent_trace.json`;
   expect exactly one recovered `execute_python` call with valid `code`.
3. **Integration**: re-run `ws_en_003` infer — expect the loop to iterate past
   turn 2 and produce `output/*.csv`.
4. **Baseline**: run `--stage eval` (Azure gpt-4.1 judge now works after the
   managed-identity fix) to get the first real `f1_by_row` / `f1_by_item` / `score`.

---

## Related fixes already landed (context)

- `OpenAICompatClient` added (vLLM policy + search summarization).
- `batch_eval.py` wired with `--reasoning_base_url` / `--search_base_url`.
- `AOAIClient` now uses `DefaultAzureCredential(exclude_managed_identity_credential=True)`
  so Azure gpt-4.1 works via the `az login` user (was 401 via VM managed identity).
- Model choice: Qwen2.5-7B-Instruct (6/6 tool-format on raw prompt); Coder-7B
  dropped (0/6); Qwen3-8B blocked by vLLM 0.8.2.
