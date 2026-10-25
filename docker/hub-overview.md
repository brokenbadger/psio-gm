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

## Windows with Docker Desktop

Use Docker Desktop. It runs this Linux image for you. A normal Windows PC receives `linux/amd64`. Windows on ARM receives `linux/arm64`. You do not set `PUID` or `PGID`.

### Install Docker Desktop

1. Open [Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/) and download **Docker Desktop for Windows - x86_64**. On a Windows on ARM PC, download the Arm build instead.
2. Double-click `Docker Desktop Installer.exe`.
3. When the installer asks for the installation mode, leave the per-user option selected. That is the recommended choice. Continue.
4. On the Configuration page, leave **Use WSL 2 instead of Hyper-V** selected when that option is shown. Continue, then select **Close** when installation finishes.
5. Docker Desktop does not open by itself. Select the Start menu, type `Docker Desktop`, and select **Docker Desktop**.
6. The first window shows the Docker Subscription Service Agreement. Select **Accept**.
7. Wait until the Dashboard is open and is no longer on a starting screen. The whale icon sits in the taskbar notification area. Select the **^** (Show hidden icons) arrow if you do not see it.

The per-user install runs Linux containers only. That is the engine this image uses, so there is no container-type switch to change.

### Prepare the games folder

1. Open File Explorer.
2. Create a folder for the games, for example `C:\Users\YourName\PSIO\games`.
3. Copy each game's `.bin` and `.cue` files into that folder.

### Pull and run the image

1. In the Docker Desktop Dashboard, select the search box in the header.
2. Type `brokenbadger/psio-gm` and select that image from the results.
3. Pull the `stable` tag.
4. In the left-hand navigation, select **Images**.
5. Find `brokenbadger/psio-gm` with the tag `stable`. Hover that row and select **Run**.
6. Select **Optional settings**.
7. Set the container name to `psio-gm`.
8. Under **Ports**, container port `5000` is already listed. Type `5000` in the host port box next to it. If that section says no ports are exposed, close the dialog, go to **Images**, select **More options** on `brokenbadger/psio-gm`, select **Pull**, and open **Run** again.
9. Under volumes, choose the games folder you created as the host path, and set the container path to `/games`.
10. Select **Run**.
11. In the left-hand navigation, select **Containers**.
12. In the search field, type `psio-gm`. If the row is missing, turn off **Only show running containers**.
13. Select the `psio-gm` row, then open its published port in a browser. The address is http://127.0.0.1:5000.
14. On that page, click **Scan**, then **Process**.

### Later

1. Open Docker Desktop from the Start menu, or select the whale icon and then **Dashboard**.
2. Select **Containers** in the left-hand navigation.
3. Find `psio-gm`. Select **Start** or **Stop** on that row.
4. With it started, open http://127.0.0.1:5000.

### Update to a newer stable image

1. Select **Images** in the left-hand navigation.
2. Select `brokenbadger/psio-gm`, select **More options**, then select **Pull**.
3. Select **Containers**, find `psio-gm`, select **Stop**, then delete that container.
4. Run the image again with the same **Optional settings**: name `psio-gm`, host port `5000` next to container port `5000`, and the same games folder mounted at `/games`.

## macOS with Docker Desktop

Use Docker Desktop. It runs this Linux image for you. A Mac with Apple silicon receives `linux/arm64`. A Mac with an Intel chip receives `linux/amd64`. You do not set `PUID` or `PGID`.

### Install Docker Desktop

1. Open [Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/). Download **Docker Desktop for Mac with Apple silicon** or **Docker Desktop for Mac with Intel chip**, matching the Mac.
2. Double-click `Docker.dmg`.
3. Drag the Docker icon onto the Applications folder.
4. Open the Applications folder and double-click **Docker**.
5. The first window shows the Docker Subscription Service Agreement. Select **Accept**.
6. If a settings window is shown, leave **Use recommended settings** selected and select **Finish**. Enter your Mac password if macOS asks for it. If that window is not shown, Docker Desktop opens on its own.
7. Wait until the Dashboard is open and is no longer on a starting screen. The whale icon sits in the menu bar at the top of the screen.

### Prepare the games folder

1. Open Finder.
2. Create a folder for the games, for example `/Users/YourName/PSIO/games`.
3. Copy each game's `.bin` and `.cue` files into that folder.

### Pull and run the image

1. In the Docker Desktop Dashboard, select the search box in the header.
2. Type `brokenbadger/psio-gm` and select that image from the results.
3. Pull the `stable` tag.
4. In the left-hand navigation, select **Images**.
5. Find `brokenbadger/psio-gm` with the tag `stable`. Hover that row and select **Run**.
6. Select **Optional settings**.
7. Set the container name to `psio-gm`.
8. Under **Ports**, container port `5000` is already listed. Type `5000` in the host port box next to it. If that section says no ports are exposed, close the dialog, go to **Images**, select **More options** on `brokenbadger/psio-gm`, select **Pull**, and open **Run** again.
9. Under volumes, choose the games folder you created as the host path, and set the container path to `/games`.
10. Select **Run**.
11. In the left-hand navigation, select **Containers**.
12. In the search field, type `psio-gm`. If the row is missing, turn off **Only show running containers**.
13. Select the `psio-gm` row, then open its published port in a browser. The address is http://127.0.0.1:5000.
14. On that page, click **Scan**, then **Process**.

### Later

1. Select the whale icon in the menu bar, then **Dashboard**. You can also open **Docker** from the Applications folder.
2. Select **Containers** in the left-hand navigation.
3. Find `psio-gm`. Select **Start** or **Stop** on that row.
4. With it started, open http://127.0.0.1:5000.

### Update to a newer stable image

1. Select **Images** in the left-hand navigation.
2. Select `brokenbadger/psio-gm`, select **More options**, then select **Pull**.
3. Select **Containers**, find `psio-gm`, select **Stop**, then delete that container.
4. Run the image again with the same **Optional settings**: name `psio-gm`, host port `5000` next to container port `5000`, and the same games folder mounted at `/games`.

## Linux

Clone this repository and put each game's `.bin` and `.cue` files in `games`. On Linux with Docker Engine, match the files to your user:

```bash
PUID=$(id -u) PGID=$(id -g) docker compose pull
PUID=$(id -u) PGID=$(id -g) docker compose up -d
```

Another games folder:

```bash
PSIO_GAMES_DIR=/path/to/your/games docker compose pull
PSIO_GAMES_DIR=/path/to/your/games docker compose up -d
```

Open http://127.0.0.1:5000, click **Scan**, then **Process**. Later, `docker start psio-gm` and `docker stop psio-gm`.

`stable` is the only tag. It is replaced when a new stable release is published.
