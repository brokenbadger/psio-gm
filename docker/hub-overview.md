# PSIO-GM

Prepare PlayStation 1 bin/cue games for a PSIO device. This image is a local web app: point it at your games, then Scan and Process in the browser.

It will:

- Merge multi-bin games into a single BIN
- Generate CU2 files for CD audio
- Add cover art
- Keep names to 56 characters and remove characters PSIO will not accept
- Group multi-disc games and write `MULTIDISC.LST`
- Detect and patch LibCrypt games
- Optionally rename games from Redump and check track CRC-32

Images are published for `linux/amd64` and `linux/arm64`. It runs on Linux, macOS, and Windows with Docker Desktop.

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

`latest` tracks the newest release. `0.2.4` is the current release.
