# HDMAS — Heterogeneous Decentralized Multi-Agent System (Copilot edition)

HDMAS runs **N parallel autonomous agents** that share a filesystem workspace
(via a shared `blackboard.json` and an `answer/` directory) and coordinate
through advisory file locks plus `vote_stop` / `wake_agent` signals. Each
agent is backed by its **own Copilot CLI subprocess**, so agents have
independent context windows and tool state.

This folder was previously named `HDMAS_COPILOT` and lived inside the
`SearchAgent` workspace. It has been relocated and the Python package name
has been renamed `HDMAS_COPILOT → HDMAS`.

> Original location: `…/Documents/SearchAgent/HDMAS_COPILOT`
> New location:      `…/OneDrive - Microsoft/Documents/WebSearchResearch/HDMAS`

---

## 1. Repository layout

```
HDMAS/
├── __init__.py
├── __main__.py            # entry point: `python -m HDMAS` → batch_eval.main()
├── orchestrator.py        # spawns N agents, runs the vote/wake state machine
├── agent.py               # single agent wrapping a CopilotClient session
├── custom_tools.py        # lock_file / unlock_file / vote_stop / wake_agent
├── lock_manager.py        # advisory file-lock implementation
├── event_logger.py        # JSONL event log per run
├── prompts.py             # system prompt for each agent
├── task_prompts.py        # per-benchmark prompt addenda (WideSearch, etc.)
├── config.py              # default model, agent count, timeouts
├── batch_eval.py          # WideSearch batch runner + evaluator
├── gaia_eval.py           # GAIA batch runner + official scorer
├── docs/                  # internal notes, blog drafts, analysis
├── requirements.txt
├── .env.example
└── README.md
```

`batch_results/` and `gaia_benchmark_results/` from the old location were
**not** copied — they are large (>10 GB combined) and contain finished runs.
They remain in the original `HDMAS_COPILOT` folder.

---

## 2. Prerequisites

- **Python 3.10+** (tested on 3.11)
- **Copilot Python SDK** — provides `CopilotClient`, `SubprocessConfig`,
  `define_tool`, and related primitives. This is an internal package; install
  per your team's instructions (e.g. `pip install copilot-python-sdk` from
  your internal index, or `pip install -e <path-to-sdk-checkout>`).
  Without it, `from copilot import CopilotClient` will fail at import time.
- **Azure CLI logged in** (`az login`) — the evaluator uses
  `DefaultAzureCredential` to mint bearer tokens for Azure OpenAI.
- *(optional)* **A local clone of the WideSearch repo** — only required for
  `batch_eval.py` (the WideSearch benchmark). Point `WIDESEARCH_ROOT` at it
  in your `.env`.

---

## 3. Setup

### 3.1 Create a virtualenv

From the **parent** of this folder (so that `HDMAS` is importable as a
top-level package):

```powershell
cd "C:\Users\v-weikailiao\OneDrive - Microsoft\Documents\WebSearchResearch"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r HDMAS\requirements.txt
```

> **Note on OneDrive + venvs.** Avoid creating the `.venv` *inside* the
> OneDrive-synced folder if you can — sync churn on thousands of small
> wheel files is painful. Putting `.venv` at the `WebSearchResearch/`
> level (one above the synced `HDMAS/` folder) is fine; or even better
> use a venv outside OneDrive entirely and just activate it before
> running.

### 3.2 Configure environment variables

```powershell
Copy-Item HDMAS\.env.example HDMAS\.env
# then edit HDMAS\.env and fill in:
#   AZURE_OPENAI_ENDPOINT     (required for evaluation)
#   WIDESEARCH_ROOT           (required for WideSearch batch_eval)
```

`python-dotenv` is loaded automatically by `batch_eval.py`; for other
entry points either load it yourself or `Set-Item Env:AZURE_OPENAI_ENDPOINT …`
in your shell.

### 3.3 Authenticate to Azure (for evaluation only)

```powershell
az login
```

The HDMAS agents themselves are driven by the Copilot SDK and do **not**
read `AZURE_OPENAI_*`. Azure credentials are only needed when you run
`batch_eval.py`, which calls into WideSearch's evaluator LLM.

---

## 4. Running

All commands assume your CWD is the **parent** of `HDMAS/`, with the venv
activated.

### 4.1 WideSearch batch evaluation

```powershell
# Run first 5 WideSearch cases with 3 agents
python -m HDMAS.batch_eval --first_n 5 --agent_count 3 --model gpt-4.1 `
    --output_root HDMAS\batch_results\smoke_test

# Run a specific instance list
python -m HDMAS.batch_eval --instance_ids ws_en_001,ws_en_002 `
    --output_root HDMAS\batch_results\two_cases

# Inference only (skip eval); useful for resuming later
python -m HDMAS.batch_eval --first_n 20 --stage infer `
    --output_root HDMAS\batch_results\run_a

# Eval only (against an existing infer run)
python -m HDMAS.batch_eval --first_n 20 --stage eval `
    --output_root HDMAS\batch_results\run_a

# Resume a partially-completed run
python -m HDMAS.batch_eval --first_n 200 --resume `
    --output_root HDMAS\batch_results\run_a
```

### 4.2 GAIA benchmark

```powershell
# First 10 validation cases (auto-skips audio/video/etc.)
python -m HDMAS.gaia_eval --first_n 10 --agent_count 3 --model gpt-4.1 `
    --output_root HDMAS\gaia_benchmark_results\smoke

# Only Level-1, with 8 agents
python -m HDMAS.gaia_eval --level 1 --agent_count 8 --model gpt-4.1 `
    --output_root HDMAS\gaia_benchmark_results\level1_8agents

# Resume
python -m HDMAS.gaia_eval --level 1 --agent_count 8 --resume `
    --output_root HDMAS\gaia_benchmark_results\level1_8agents
```

### 4.3 Default entry point

`python -m HDMAS` is equivalent to `python -m HDMAS.batch_eval` (see
`__main__.py`).

---

## 5. How it works (very short version)

- **Orchestrator** creates the workspace, the shared `blackboard.json`,
  one shared `CopilotClient`, and spawns `N` `Agent` coroutines.
- Each **Agent** opens its own Copilot session on the shared client, gets
  the system prompt from `prompts.py` plus the user query, and is given
  four custom tools: `lock_file`, `unlock_file`, `vote_stop`, `wake_agent`.
  Built-in Copilot tools handle file I/O, shell, web search, etc.
- Agents converge by writing to `answer/` (typically `answer/final.md`)
  and unanimously calling `vote_stop`. The orchestrator collects all
  `answer/*.md` files and returns them.
- `batch_eval.py` / `gaia_eval.py` then score each case with the
  benchmark's official scorer.

For deeper architectural notes see `docs/`.

---

## 6. Differences from the original `HDMAS_COPILOT` folder

| Change | Why |
|---|---|
| Folder + package renamed `HDMAS_COPILOT` → `HDMAS` | Matches the new location name. |
| `WIDESEARCH_ROOT` env var added | Old code assumed WideSearch was `../../WideSearch` relative to `SearchAgent`. After moving out of `SearchAgent`, that relative path no longer works. The new helper `_widesearch_root()` checks `WIDESEARCH_ROOT` first, then falls back to a sibling `WideSearch/` next to this folder. |
| `batch_results/`, `gaia_benchmark_results/` not copied | ~10 GB of completed runs; kept in the original location. |
| Local `requirements.txt` | Repo-scoped, includes the `copilot` SDK and `tenacity` that the parent `SearchAgent/requirements.txt` did not list. |
| `.env.example` added | Documents the env vars actually read by the code. |

---

## 7. Troubleshooting

- **`ModuleNotFoundError: copilot`** — install the internal Copilot Python
  SDK. There is no public PyPI package by that name.
- **`FileNotFoundError: WIDESEARCH_ROOT=… does not exist`** — set
  `WIDESEARCH_ROOT` in your `.env` to the absolute path of your WideSearch
  clone, or put a `WideSearch/` directory next to this folder.
- **`AZURE_OPENAI_ENDPOINT not set; eval LLM calls may fail`** —
  evaluation cannot proceed without an endpoint. Fill it into `.env`.
- **Azure auth errors** — run `az login`; `DefaultAzureCredential` will
  pick up your CLI credentials.
- **OneDrive locking files mid-run** — if you see sporadic
  `PermissionError` writing to the workspace, pause OneDrive sync for the
  `HDMAS/` folder while a long run is in flight, or direct
  `--output_root` to a path outside OneDrive.
