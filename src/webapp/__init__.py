"""Flask application factory for PSIO-GM web UI."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from library_service import DatabaseError, GameLibraryService
from webapp.jobs import ProcessJobManager

APP_VERSION = "0.2.2"


def _library_root() -> Path | None:
    """Allowlist root (e.g. /games in Docker)."""
    raw = (os.environ.get("PSIO_LIBRARY_ROOT") or "").strip()
    return Path(raw).resolve() if raw else None


def _default_library_path() -> str:
    """Fixed library location — no path picker in the UI."""
    return (os.environ.get("PSIO_DEFAULT_LIBRARY") or "/games").strip()


def _path_allowed(path: Path) -> bool:
    root = _library_root()
    if root is None:
        return True
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return path.resolve() == root


def create_app(service: GameLibraryService | None = None) -> Flask:
    template_dir = Path(__file__).resolve().parent / "templates"
    static_dir = Path(__file__).resolve().parent / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )
    app.config["SERVICE"] = service or GameLibraryService(debug_mode=False)
    app.config["JOBS"] = ProcessJobManager(app.config["SERVICE"])

    @app.get("/")
    def index():
        svc: GameLibraryService = app.config["SERVICE"]
        return render_template(
            "index.html",
            app_version=APP_VERSION,
            games=svc.games_as_dicts(),
            summary=svc.summarize() if svc.game_list else None,
        )

    @app.get("/api/health")
    def health():
        svc: GameLibraryService = app.config["SERVICE"]
        try:
            svc.ensure_database()
            db_ok = True
            db_error = None
        except DatabaseError as error:
            db_ok = False
            db_error = str(error)
        return jsonify(
            {
                "ok": True,
                "database_ok": db_ok,
                "database_error": db_error,
                "library_path": _default_library_path(),
            }
        )

    @app.get("/api/library")
    def get_library():
        svc: GameLibraryService = app.config["SERVICE"]
        return jsonify(
            {
                "path": svc.library_path or _default_library_path(),
                "count": len(svc.game_list),
                "summary": svc.summarize() if svc.game_list else None,
                "crc_checked": svc.last_crc_check,
            }
        )

    @app.post("/api/library")
    def scan_library():
        """Scan the configured library mount (path is not client-selectable)."""
        jobs: ProcessJobManager = app.config["JOBS"]
        if jobs.is_running():
            return jsonify({"ok": False, "error": "Cannot scan while a process job is running"}), 409

        path = _default_library_path()
        path_obj = Path(path)
        if not path_obj.is_dir():
            return jsonify(
                {
                    "ok": False,
                    "error": f"Library not found at {path}. Mount your games folder (Compose uses ./games → /games).",
                }
            ), 400
        if not _path_allowed(path_obj):
            root = _library_root()
            return jsonify(
                {
                    "ok": False,
                    "error": f"Configured library path must be under {root}",
                }
            ), 400

        payload = request.get_json(silent=True) or {}
        crc_check = bool(payload.get("crc_check", False))
        svc: GameLibraryService = app.config["SERVICE"]
        try:
            svc.scan_library(str(path_obj.resolve()), crc_check=crc_check)
        except DatabaseError as error:
            return jsonify({"ok": False, "error": str(error)}), 503
        except OSError as error:
            return jsonify({"ok": False, "error": f"Cannot read library: {error}"}), 400

        return jsonify(
            {
                "ok": True,
                "path": svc.library_path,
                "games": svc.games_as_dicts(),
                "summary": svc.summarize(),
            }
        )

    @app.get("/api/games")
    def list_games():
        svc: GameLibraryService = app.config["SERVICE"]
        return jsonify(
            {
                "games": svc.games_as_dicts(),
                "summary": svc.summarize() if svc.game_list else None,
                "crc_checked": svc.last_crc_check,
            }
        )

    @app.post("/api/process")
    def start_process():
        svc: GameLibraryService = app.config["SERVICE"]
        jobs: ProcessJobManager = app.config["JOBS"]
        if not svc.game_list:
            return jsonify({"ok": False, "error": "No games loaded — scan first"}), 400
        payload = request.get_json(silent=True) or {}
        redump_rename = bool(payload.get("redump_rename", True))
        if not jobs.start(redump_rename=redump_rename):
            return jsonify({"ok": False, "error": "A process job is already running"}), 409
        return jsonify({"ok": True, "status": jobs.get_status()}), 202

    @app.get("/api/process/status")
    def process_status():
        jobs: ProcessJobManager = app.config["JOBS"]
        return jsonify(jobs.get_status())

    return app


def main():
    import argparse

    parser = argparse.ArgumentParser(description="PSIO-GM web UI")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port (default 5000)")
    args = parser.parse_args()

    service = GameLibraryService(debug_mode=args.debug)
    app = create_app(service)
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
