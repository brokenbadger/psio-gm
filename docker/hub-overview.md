# PSIO-GM

![PSIO-GM web UI](https://github.com/brokenbadger/psio-gm/raw/v0.2/image.png)

Prepare PlayStation 1 bin/cue games for a PSIO device. This image is a local web app: point it at your games, then Scan and Process in the browser.

Source code: [github.com/brokenbadger/psio-gm](https://github.com/brokenbadger/psio-gm). Stable images are published on this page. GitHub Releases on that repository are for testing; future stable releases are published here.

It will:

- Merge multi-bin games into a single BIN
- Generate CU2 files for CD audio
- Add cover art
- Keep names to 56 characters and remove characters PSIO will not accept
- Group multi-disc games and write `MULTIDISC.LST`
- Detect and patch LibCrypt games
- Optionally rename games from Redump and check track CRC-32

Images are published for `linux/amd64` and `linux/arm64`. It runs on Linux, macOS, and Windows with Docker Desktop.

## Controls

- **About** — version and credits.
- **CRC check on scan** — off by default. Turn it on to compare each data track with Redump while scanning. This is slower and does not change any files.
- **Scan** — read the mounted library and fill the summary and table. Scan does not modify games.
- **Redump rename** — on by default. During Process, a game with a Redump title is renamed to that title.
- **Process** — prepare the games. It merges multi-bin images, writes missing CU2 files, adds covers, fixes names, puts each game in its own folder, groups multi-disc sets, and applies LibCrypt patches.

## Summary

Counts after a scan:

- **Total** — games found.
- **Unidentified** — no PlayStation serial was read from the disc.
- **No cover** — a cover image is missing.
- **Multi-bin** — more than one BIN file. Process merges these into one.
- **Invalid names** — the name is longer than 56 characters or contains a `.`.
- **Multi-disc games** — titles that belong to a multi-disc set.

## Columns

`*` means that column does not apply to the game. **Yes** means it is already done. **No** means it is still needed.

- **Name** — name taken from the cue sheet.
- **ID** — PlayStation serial, such as `SCES-02105`. `—` means the disc was not identified.
- **Cover** — **Yes** if a cover image is present, **No** if it is missing.
- **Disc** — disc number. A single-disc game shows `0`.
- **Bins** — how many BIN files the cue lists.
- **CU2** — CD audio index. `*` if the game has no CD audio. **No** if a CU2 file is required and missing. **Yes** if it is present.
- **LST** — multi-disc list. `*` if the game is not part of a set. **No** if `MULTIDISC.LST` is missing. **Yes** if it is present.
- **LibCrypt** — `*` if the game is not LibCrypt. **No** if it still needs the patch. **Yes** if the BIN is already patched.
- **CRC** — `*` when CRC check is off. **Yes** if the tracks match Redump. **No** if they do not. `—` if Redump has no track data for that game. A LibCrypt patch changes the BIN, so CRC shows **No** afterwards.

## Use

Clone [brokenbadger/psio-gm](https://github.com/brokenbadger/psio-gm) and put each game's bin and cue files in `games`. From the repo folder:

```bash
docker compose pull
docker compose up -d
```

Open http://127.0.0.1:5000, click **Scan**, then **Process**.

On Linux with Docker Engine, match the files to your user:

```bash
PUID=$(id -u) PGID=$(id -g) docker compose up -d
```

To use a different folder:

```bash
PSIO_GAMES_DIR=/path/to/your/games docker compose up -d
```

Windows PowerShell:

```powershell
$env:PSIO_GAMES_DIR="C:\path\to\your\games"
docker compose up -d
```

Later, stop and start the same container with `docker stop psio-gm` and `docker start psio-gm`.

`latest` and `stable` track the newest stable release. `0.2.4` is the current release.
