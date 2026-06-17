"""
File-level lock manager for HDMAS v4.

Provides explicit lock_file / unlock_file operations that agents call
as tools.  Uses a single ``locks.json`` registry file protected by a
threading lock (in-process) and a ``filelock`` physical file lock
(cross-process safety).

Lock registry schema (locks.json):
{
    "blackboard.json": {
        "holder": "agent_0",
        "acquired_at": 1712345678.123
    },
    "answer/answer.md": { ... }
}

TTL: locks older than LOCK_TTL are considered expired and can be
forcibly reclaimed.
"""

import json
import os
import threading
import time
from pathlib import Path
from typing import Optional

from filelock import FileLock

from . import config


class LockManager:
    """Manages file-level advisory locks backed by a JSON registry."""

    def __init__(self, workspace: str):
        self._workspace = Path(workspace)
        self._registry_path = self._workspace / "locks.json"
        self._physical_lock_path = self._workspace / ".locks.json.lock"
        self._physical_lock = FileLock(str(self._physical_lock_path), timeout=10)
        self._thread_lock = threading.Lock()

        # Ensure registry exists
        if not self._registry_path.exists():
            self._write_registry({})

    # ------------------------------------------------------------------
    # Public API (called by ToolExecutor)
    # ------------------------------------------------------------------

    def acquire(
        self,
        path: str,
        holder: str,
        timeout: float = None,
        retry_interval: float = None,
    ) -> dict:
        """Try to acquire a lock on *path* for *holder*.

        Blocks up to *timeout* seconds.  Returns a status dict.
        """
        timeout = timeout or config.LOCK_WAIT_TIMEOUT
        retry_interval = retry_interval or config.LOCK_RETRY_INTERVAL
        deadline = time.time() + timeout
        normalized = self._normalize(path)

        while True:
            with self._thread_lock:
                with self._physical_lock:
                    registry = self._read_registry()

                    entry = registry.get(normalized)

                    # No lock or expired lock → grant
                    if entry is None or self._is_expired(entry):
                        registry[normalized] = {
                            "holder": holder,
                            "acquired_at": time.time(),
                        }
                        self._write_registry(registry)
                        return {"status": "locked", "path": normalized}

                    # Already held by this agent → re-entrant grant
                    if entry.get("holder") == holder:
                        return {"status": "locked", "path": normalized}

            # Lock held by someone else — wait
            if time.time() >= deadline:
                return {
                    "status": "timeout",
                    "path": normalized,
                    "held_by": entry.get("holder", "unknown"),
                    "error": f"Could not acquire lock on {normalized} within {timeout}s",
                }
            time.sleep(retry_interval)

    def release(self, path: str, holder: str) -> dict:
        """Release a lock.  Only the holder (or expired locks) can release."""
        normalized = self._normalize(path)

        with self._thread_lock:
            with self._physical_lock:
                registry = self._read_registry()
                entry = registry.get(normalized)

                if entry is None:
                    return {"status": "not_locked", "path": normalized}

                if entry.get("holder") != holder and not self._is_expired(entry):
                    return {
                        "status": "denied",
                        "path": normalized,
                        "error": f"Lock held by {entry.get('holder')}, not {holder}",
                    }

                del registry[normalized]
                self._write_registry(registry)
                return {"status": "unlocked", "path": normalized}

    def release_all(self, holder: str):
        """Release every lock held by *holder*.  Used during cleanup."""
        with self._thread_lock:
            with self._physical_lock:
                registry = self._read_registry()
                to_remove = [
                    k for k, v in registry.items()
                    if v.get("holder") == holder
                ]
                for k in to_remove:
                    del registry[k]
                if to_remove:
                    self._write_registry(registry)

    def get_holder(self, path: str) -> Optional[str]:
        """Return the current holder of a lock, or None."""
        normalized = self._normalize(path)
        with self._thread_lock:
            with self._physical_lock:
                registry = self._read_registry()
                entry = registry.get(normalized)
                if entry and not self._is_expired(entry):
                    return entry.get("holder")
                return None

    def list_locks(self) -> dict:
        """Return a copy of the current lock registry (non-expired only)."""
        with self._thread_lock:
            with self._physical_lock:
                registry = self._read_registry()
                return {
                    k: v for k, v in registry.items()
                    if not self._is_expired(v)
                }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize(self, path: str) -> str:
        """Normalize a path to workspace-relative, forward-slash form."""
        p = Path(path)
        try:
            rel = p.relative_to(self._workspace)
        except ValueError:
            rel = p
        return str(rel).replace("\\", "/")

    def _is_expired(self, entry: dict) -> bool:
        elapsed = time.time() - entry.get("acquired_at", 0)
        return elapsed > config.LOCK_TTL

    def _read_registry(self) -> dict:
        """Read locks.json. Caller must hold both locks."""
        try:
            return json.loads(self._registry_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_registry(self, data: dict):
        """Write locks.json atomically. Caller must hold both locks."""
        tmp = self._registry_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self._registry_path)
