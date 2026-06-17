"""
Configuration constants for HDMAS Copilot edition.
"""

# --- Agent loop ---
MODEL = "gpt-5.4"                # Copilot model name

# --- Agents ---
N_AGENTS = 3

# --- Locks ---
LOCK_WAIT_TIMEOUT = 30.0
LOCK_RETRY_INTERVAL = 1.0
LOCK_TTL = 60.0

# --- Context window ---
# Copilot SDK manages context via infinite sessions (auto-compaction).
# We disable it and let the model's native context handle things.
INFINITE_SESSIONS_ENABLED = True

# --- Search ---
SEARCH_COUNT = 10

# --- Timeouts ---
AGENT_TIMEOUT = 1800.0           # Per-agent timeout (seconds)
