"""Background job helpers for the Flask web UI."""

from __future__ import annotations

import threading
from typing import Any, Optional

from library_service import GameLibraryService


class ProcessJobManager:
    """Runs at most one library process job at a time."""

    def __init__(self, service: GameLibraryService):
        self.service = service
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self.status: dict[str, Any] = {
            "state": "idle",
            "message": "",
            "percent": 0,
            "stage": "",
            "game_index": None,
            "errors": [],
            "done": True,
        }

    def _set_status(self, **kwargs) -> None:
        with self._lock:
            self.status.update(kwargs)

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self.status)

    def is_running(self) -> bool:
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def start(self, *, redump_rename: bool = True) -> bool:
        """Start processing. Returns False if a job is already running."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False

            def on_progress(stage, message, percent, game_index=None):
                self._set_status(
                    state="running",
                    stage=stage,
                    message=message,
                    percent=percent,
                    game_index=game_index,
                    done=False,
                )

            def worker():
                self._set_status(state="running", message="Starting...", percent=0, errors=[], done=False)
                try:
                    errors = self.service.process_games(
                        redump_rename=redump_rename,
                        on_progress=on_progress,
                    )
                    self._set_status(
                        state="completed",
                        message="Processing finished",
                        percent=100,
                        errors=[{"name": n, "error": e} for n, e in errors],
                        done=True,
                    )
                except Exception as error:  # noqa: BLE001
                    self._set_status(
                        state="failed",
                        message=str(error),
                        percent=0,
                        errors=[{"name": "job", "error": str(error)}],
                        done=True,
                    )

            self._thread = threading.Thread(target=worker, daemon=True)
            self._thread.start()
            return True
