# Bug: Silent harness crash during search-heavy agent runs

**Date:** 2026-07-07
**Component:** `search_agent/batch_eval.py`, `python_executor/python_executor.py`, `search_client/bing_grounding_search_client.py`
**Severity:** P1 — blocked all evaluation of the retrained model
**Status:** Fixed & verified

---

## 1. Symptom

While evaluating the freshly retrained LoRA model (`sft_train`, 48-trajectory SFT)
on the held-out WideSearch instance `ws_en_028`, the harness **died silently**:

- No output CSV, no `agent_trace.json`, no `*_response.jsonl`.
- **No `ERROR` line and no Python traceback** in the log.
- The process (`batch_eval`) simply vanished after ~5–7 reasoning turns.
- **Reproducible** — happened identically on two separate runs.
- Only artefacts left behind: `config.json` and a partial `workspace/log/*/search_log.json`.

Log tail (last thing before the process disappeared):

```
04:02:04  POST http://localhost:8002/v1/chat/completions "HTTP/1.1 200 OK"   # 5th reasoning turn
<nothing — process gone>
```

## 2. Diagnosis (how we found the root cause)

Step-by-step elimination:

1. **Checked for a Python exception.** `run_infer()` already wraps each instance
   in `try/except Exception` and writes an `ERROR: ...` response + logs with
   `exc_info=True`. The **absence** of any `ERROR`/`FAILED` line meant the death
   was **not a normal Python exception** — it was an OS-level signal
   (`SIGKILL`/`SIGSEGV`) that `try/except` cannot catch.

2. **Ruled out OOM.** `free -g` showed **866 GB RAM, 835 GB free**. Not memory.

3. **Found an orphaned kernel.** After the crash, `pgrep -af ipykernel_launcher`
   showed **1 leftover kernel**. A clean shutdown routes through
   `PythonExecutor.shutdown()` (via the `finally` in `SearchAgent.run`), which
   kills the kernel. An **orphaned** kernel is the tell-tale sign the parent
   died abnormally (by signal), before it could tear the kernel down.

4. **Quantified the trigger.** The partial `search_log.json` had **97 search
   queries** (a later inspection showed the first crash reached 115), issued
   across only ~5–7 reasoning turns — i.e. the policy emitted code cells that
   fanned out ~15–18 searches each. Timeline showed an **~11-minute gap**
   between two reasoning turns = a single cell running dozens of searches, then
   the process died right after the results streamed back.

**Conclusion:** the retrained (small) policy imitated the teacher's *batched
wide fan-out* but not its *converge-and-write* discipline, issuing pathological
per-cell search bursts. During the heavy kernel→parent I/O that followed (huge
IOPub stdout messages through pyzmq / a possibly dying kernel), the **parent
process died by an uncatchable signal**, taking the whole run down with no trace.

> Key insight: this was a **harness-robustness bug**, not a model-quality
> regression. The model was never given the chance to finish.

## 3. Root cause

Two compounding gaps:

1. **No blast-radius limit on searches.** `search_client.search([...])` executed
   whatever list the model produced (the system prompt even invites "up to 200
   queries per call"). A weak policy could issue 100+ searches in one cell.

2. **The executor read loop was not crash-safe.**
   `PythonExecutor.run()` only caught a `get_iopub_msg` **timeout**; it did not
   detect a **dead kernel**, and it accumulated `stdout_parts` **unbounded**
   (truncation happened only *after* the loop). A giant/rapid output stream
   could destabilise the transport, and a kernel death was indistinguishable
   from a slow cell.

3. **No fault isolation.** `run_infer()` ran each instance **in-process**, so a
   signal-level crash on one instance killed the entire batch **silently** — the
   `try/except` was useless against `SIGKILL`/`SIGSEGV`.

## 4. The fix (3 layers of defence)

### Layer 1 — Per-cell search cap (blast-radius limit)
`search_client/bing_grounding_search_client.py` → `search()`

When called with a list, cap the number actually executed via env
`SEARCH_MAX_QUERIES_PER_CALL` (default `50`, `0` disables). Queries beyond the
cap return a machine-readable `SEARCH_SKIPPED` note so the model can re-issue
them in a smaller follow-up call. **The returned list length always matches the
input length**, so the model's indexing never breaks.

```python
cap = int(os.getenv("SEARCH_MAX_QUERIES_PER_CALL", "50"))
if cap > 0 and len(query) > cap:
    head = self._search_batch(query[:cap], max_workers=max_workers)
    skip_note = [json.dumps({"query": q,
        "answer": f"SEARCH_SKIPPED: too many queries in one call (cap={cap}). "
                  "Re-issue this query in a smaller follow-up call.",
        "sources_url": "NONE"}, ensure_ascii=False) for q in query[cap:]]
    return head + skip_note
```

### Layer 2 — Kernel-death guard + bounded stdout
`python_executor/python_executor.py` → `PythonExecutor.run()`

- On a `get_iopub_msg` failure, check `self._km.is_alive()`. A dead kernel now
  returns a clear, catchable `KernelDied` error instead of masquerading as a
  slow cell:

```python
except Exception as exc:
    if not self._km.is_alive():
        error_name = "KernelDied"
        error_value = ("Kernel process died during execution (likely crashed "
                       "or was killed). The cell's output is incomplete.")
    else:
        error_value = f"Timeout waiting for kernel output: {exc}"
    break
```

- Bound in-memory stream accumulation at `max(4 * max_output_chars, 200_000)`
  chars; once exceeded, keep draining messages to `idle` **without storing**
  them. Prevents a runaway cell from ballooning memory / a huge single frame.

### Layer 3 — Per-instance process isolation (the guarantee)
`search_agent/batch_eval.py` → `_run_single_isolated()` / `_infer_worker()`

Run each instance's `run_single()` in a **forked child process**. This is the
only thing that can contain an *uncatchable* signal-level crash:

- Child delivers its result (or a captured exception string) via a `Queue`.
- Parent polls with a 2 s tick so a crash is detected within ~2 s (child no
  longer alive + no result → `RuntimeError`).
- The previously **unused** `--timeout` (default 1800 s) is now **enforced**:
  on timeout the child is `terminate()`-d and a `TimeoutError` raised.
- Any child crash/timeout propagates to the existing `run_infer` `try/except`,
  which records an `ERROR` response **for that one instance only** — never a
  silent whole-batch death.

```python
def _run_single_isolated(*, timeout, **kwargs) -> str:
    ctx = mp.get_context("fork")
    q = ctx.Queue()
    proc = ctx.Process(target=_infer_worker, args=(q, kwargs))
    proc.start()
    deadline = time.time() + timeout
    while True:
        try:
            status, payload = q.get(timeout=2.0); break
        except _queue.Empty:
            if not proc.is_alive():
                proc.join()
                raise RuntimeError(f"instance process crashed with no result "
                                   f"(exitcode={proc.exitcode}; kernel/segfault/OOM-kill)")
            if time.time() > deadline:
                proc.terminate(); proc.join(10)
                raise TimeoutError(f"instance exceeded timeout ({timeout:.0f}s)")
    proc.join(10)
    if status == "ok":
        return payload
    raise RuntimeError(f"instance failed in child: {payload}")
```

> `fork` (not `spawn`) is safe here: the harness venv has **no CUDA/torch**
> loaded in the parent, and no kernel/threadpool exists at fork time (the child
> creates its own). Fork also avoids pickling the args.

## 5. Verification

Re-ran `ws_en_028` (held-out) on the LoRA `sft_train` model with the hardened
harness (`SEARCH_MAX_WORKERS=3 SEARCH_MAX_QUERIES_PER_CALL=40 --timeout 1500`):

| Run | Crash? | Turns | Output CSV | F1_item | F1_row |
|-----|--------|-------|-----------|---------|--------|
| before fix (x2) | **yes, silent** | 5–7 | none | — | — |
| after fix | **no** | 24 | written | **0.80** | 0.0 |

The instance completed cleanly in 1m49s, wrote its output file, and produced a
real score. Progression across checkpoints: base 7B `0 / no output` → LoRA
pilot (11 ex) `F1_item 0.28 / no CSV` → LoRA train (48 ex) `F1_item 0.80 / CSV
written`.

## 6. Lessons

- **A missing `ERROR` line + orphaned child process = death by signal.** No
  Python `try/except` will save you; you need **process isolation** to turn an
  uncatchable crash into a recorded, per-item failure.
- **Never trust an in-process batch loop** around code that drives a
  subprocess/kernel and pulls unbounded external data. Isolate each unit.
- **Cap external fan-out at the source.** A weak RL/SFT policy will do
  pathological things (100+ searches/cell); guardrails belong in the tool, not
  only in the prompt.
- **Bound every accumulator.** Stream buffers must be capped *during* reading,
  not only truncated afterwards.
- **Distinguish "slow" from "dead."** A timeout and a dead kernel need different
  handling; conflating them hides real crashes.
- **A harness bug can masquerade as a model regression.** Always confirm the
  agent is even allowed to finish before drawing conclusions about quality.
