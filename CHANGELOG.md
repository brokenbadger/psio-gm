# Changelog

All notable changes to **PSIO-GM** (this fork) are documented here.

The project is based on [logi-26/psio-game-manager](https://github.com/logi-26/psio-game-manager) (upstream default branch `v0.2` / app revision 0.3 at the time of forking).

Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- **Docs** — drop redundant `mkdir -p games`; Compose already creates `./games` via `create_host_path`

## [0.2.2] — 2026-08-13

Docker-only Flask line (tag **`v0.2.2`**).

### Changed
- **Docker-only product path** — supported run method is `docker compose up --build` (Flask web UI). Removed Compose profiles and the X11 Tk service
- **Dependencies** — `requirements.txt` is **Flask + Pillow only**; removed ttkbootstrap / Tk desktop entrypoint (`src/psio_gm.py`). Use branch `v0.1` for the Tk app
- **Slimmer image** — no Tk apt packages; image tag `psio-gm-app:0.2.2`
- **Docs** — README rewritten around Docker

## [0.2.1] — 2026-08-13

Review follow-up for the v0.2 web/Docker line (tag **`v0.2.1`**).

### Fixed
- **Flat library paths** — no-subdir libraries use `.` as the folder name so Redump rename cannot target filesystem root (e.g. under `/games` in Docker)
- **LibCrypt apply** — only mark applied / invalidate CRC after a successful PPF1–3 apply; guard against failed file opens
- **Cover summary** — single-disc games (`disc_number == 0`) count toward missing covers
- **Web CRC column** — matches Tk/README (`*` when CRC check off; `—` only when no Redump track data)
- **Web process UI** — refresh summary after jobs; list per-game errors; reject scan while a job runs; atomic single-job start
- **Tk Browse cancel** — no longer enables Process with an empty path
- **Docs / Compose** — clarify path text field vs host browser; remove incorrect “named volume” warning; prefill `/games` and allowlist via `PSIO_LIBRARY_ROOT` / `PSIO_DEFAULT_LIBRARY`; image tag `0.2.1`

### Changed
- **Tk GUI** — remove unused pre-service scan/merge helpers left after the GameLibraryService refactor
- **Docs** — prefer `python src/run_web.py` from repo root (`python -m webapp` needs cwd/`PYTHONPATH` under `src/`)

## [0.2.0] — 2026-08-13

First **v0.2** line release (tag **`v0.2.0`** on branch `v0.2` — tag kept distinct from the branch name).

### Fixed
- **LibCrypt detection** — titles with a PPF in `libcrypt_patches` but a missing/`0` `games.libcrypt` flag (e.g. SCES_02105 CTR Europe) are now treated as LibCrypt-required so the UI shows Yes/No and patches can apply
- **CRC display** — when Redump track CRC rows are missing from the DB (e.g. SCES_02104 Spyro 2 Europe), the CRC column shows `—` instead of a false `No`

### Added
- **Headless core** — `GameLibraryService` (`src/library_service.py`) for scan/process; shared by Tk and web
- **Flask web UI** — localhost MVP (`python src/run_web.py` / `python -m webapp`); configure a library path on disk (no BIN uploads); background process job with status polling
- **Docker Compose `--profile web`** — web container on `127.0.0.1:5000` with games bind-mount (no X11); Tk GUI moved to `--profile gui`

### Changed
- **App revision** — `CURRENT_REVISION = 0.2` on branch `v0.2`
- **Tk GUI** — scan/process/database ensure delegate to `GameLibraryService`
- **Dependencies** — add `flask==3.1.2`; keep `ttkbootstrap==2.2.0` and `pillow==12.3.0`
- **Docs** — README covers web UI, Compose profiles, and CRC column meanings (`Yes` / `No` / `—` / `*`)

## [0.1.0] — 2026-08-12

First PSIO-GM release on branch `v0.1` (release tag **`v0.1.0`** — kept distinct from the branch name to avoid Git ref ambiguity).

### Packaging
- **Cursor rules excluded** — `.cursor/` is local-only (gitignored / export-ignored) and is not included in the release source archive

### Security / data safety
- **Safe multi-BIN merge** — merged BIN/CUE files are staged and verified before originals are deleted ([#1](https://github.com/brokenbadger/psio-gm/issues/1), `5d5e8dc`)
- **Batch error isolation** — a failure on one game no longer aborts the whole batch; failures are collected and shown in a dialog ([#2](https://github.com/brokenbadger/psio-gm/issues/2), `5d5e8dc`)
- **Missing BIN guard** — CUEs that reference missing BIN files are skipped instead of crashing with `IndexError` ([#3](https://github.com/brokenbadger/psio-gm/issues/3), `5d5e8dc`)

### Fixed
- **Post-merge BIN path** — after merge, the app looks for `{game_name}.bin` (merged output name), not the CUE stem ([#4](https://github.com/brokenbadger/psio-gm/issues/4), `5d5e8dc`)
- **CU2 track matching** — TRACK/INDEX regexes match whole track numbers so track 1 no longer matches tracks 10+ ([#5](https://github.com/brokenbadger/psio-gm/issues/5), `7700950`)
- **Incomplete multi-disc collections** — MULTIDISC folding/LST generation is skipped if any disc in the collection is missing; BIN/CUE path updates only apply to `.bin`/`.cue` files ([#6](https://github.com/brokenbadger/psio-gm/issues/6), `7700950`)
- **PPF3 “already applied” check** — undo bytes are skipped only when the PPF3 undo flag is set ([#7](https://github.com/brokenbadger/psio-gm/issues/7), `7700950`)
- **Resource / database paths** — data and icons resolve from the script directory (or PyInstaller `_MEIPASS`), not the process CWD ([#8](https://github.com/brokenbadger/psio-gm/issues/8), `a63c190`)
- **Database split parts retained** — merging into `psio_assist.db` no longer deletes the redistributable split parts ([#8](https://github.com/brokenbadger/psio-gm/issues/8), `a63c190`)
- **UI polish** — About dialog works; Auto Rename toggle log text corrected; LST status casing consistent (`Yes`); browse dialog starts at the user’s home directory ([#8](https://github.com/brokenbadger/psio-gm/issues/8), `a63c190`)

### Changed
- **Rebrand** — entrypoint `psio_gm.py`, class `PSIOGM`, product name **PSIO-GM**, venv example `psio_gm_env` (`5aaf7d1`)
- **App revision** — `CURRENT_REVISION = 0.1` (fork versioning; not a continuation of upstream’s 0.3 number) (`99d2f7c`)
- **Dependencies** — `requirements.txt` trimmed to `ttkbootstrap` (stdlib `pathlib`; dropped unused `pathlib2` / `six` / pinned `pillow`) (`a63c190`)
- **License header** — main module header aligned with repo **GPL-3.0** (`a63c190`)
- **About dialog** — credits upstream LoGi26 and this fork (brokenbadger, 2026), with readable blank lines (`99d2f7c`, `fac1ce7`)

### Added
- **Docker Compose** — `docker-compose.yml` with X11 bind mounts and `PSIO_GAMES_DIR` for a host game library; explicit bind syntax so relative folders are not mistaken for named volumes (`43b92cd`, `99d2f7c`)
- **`.dockerignore`** — keeps builds lean (`.venv`, games dumps, etc.) (`43b92cd`)
- **Dockerfile updates** — correct `psio_gm.py` entrypoint, Tk packages, image labels for title/version 0.1 (`a63c190`, `99d2f7c`)

### Documentation
- README updated for PSIO-GM naming, Python 3.9+/Tk notes, 56-character name limit, Docker Compose usage, and fork releases link
- This changelog added to record fork deltas versus upstream

### Upstream baseline
Forked from `logi-26/psio-game-manager` at `e5415b0` (`v0.2` tip at fork time). Upstream Windows builds (if needed for comparison) remain on their releases page; PSIO-GM builds will be published under [brokenbadger/psio-gm releases](https://github.com/brokenbadger/psio-gm/releases).
