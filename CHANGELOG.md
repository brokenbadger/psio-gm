# Changelog

All notable changes to **PSIO-GM** (this fork) are documented here.

The project is based on [logi-26/psio-game-manager](https://github.com/logi-26/psio-game-manager) (upstream default branch `v0.2` / app revision 0.3 at the time of forking).

Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] — 2026-08-12

First PSIO-GM release on branch `v0.1` (release tag **`v0.1.0`** — kept distinct from the branch name to avoid Git ref ambiguity).

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
