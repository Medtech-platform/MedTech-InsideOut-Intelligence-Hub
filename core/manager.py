"""
StateManager — persists agent outputs so downstream agents can read prior results.

Uses a simple JSON file on disk so the state survives between runs.
Pass `run_id` to segregate different assessment runs.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from config.settings import settings


class StateManager:
    def __init__(self, run_id: str | None = None) -> None:
        self.run_id = run_id or str(uuid.uuid4())[:8]
        self._state: dict[str, Any] = {}
        self._path = settings.OUTPUT_DIR / f"state_{self.run_id}.json"
        self._load()

    # ------------------------------------------------------------------ #

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value
        self._persist()

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def update(self, data: dict) -> None:
        self._state.update(data)
        self._persist()

    def all(self) -> dict:
        return dict(self._state)

    # ------------------------------------------------------------------ #

    def _persist(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(self._state, indent=2, default=str))
        except Exception as exc:
            logger.warning(f"StateManager: could not persist state — {exc}")

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._state = json.loads(self._path.read_text())
                logger.debug(f"StateManager: loaded existing state from {self._path}")
            except Exception:
                self._state = {}
