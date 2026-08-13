"""
Headless game-library orchestration for PSIO-GM.

Used by the Flask web UI. No GUI toolkit imports.
"""

from __future__ import annotations

from ast import literal_eval
from os.path import exists, join
from pathlib import Path
from typing import Callable, Optional

from cu2 import Cu2Generator
from db import GameDatabase
from game_files import Binfile, Cuesheet, Game
from utils import Utils

ProgressCallback = Callable[[str, str, int, Optional[int]], None]


class DatabaseError(RuntimeError):
    """Raised when the game database cannot be prepared."""


class GameLibraryService:
    """Scan and process a PSIO game library without a GUI."""

    MAX_GAME_NAME_LENGTH = 56
    DATABASE_NAME = "psio_assist.db"

    def __init__(self, debug_mode: bool = False, resource_root: Optional[Path] = None):
        self.debug_mode = debug_mode
        self.game_list: list[Game] = []
        self.library_path: Optional[str] = None
        self.last_crc_check: bool = False

        # Resolve data relative to the src directory (stable for -m / Flask)
        self.resource_root = Path(resource_root) if resource_root else Path(__file__).resolve().parent

        self.db = GameDatabase(debug_mode=self.debug_mode)
        self.utils = Utils(database=self.db, debug_mode=self.debug_mode)
        self.cu2_generator = Cu2Generator(debug_mode=self.debug_mode)

        self.db.set_database_path(str(self.resource_root / "data"), self.DATABASE_NAME)

    def _debug_print(self, message: str) -> None:
        if self.debug_mode:
            print(message)

    def _emit(
        self,
        on_progress: Optional[ProgressCallback],
        stage: str,
        message: str,
        percent: int,
        game_index: Optional[int] = None,
    ) -> None:
        if on_progress:
            on_progress(stage, message, percent, game_index)

    def ensure_database(self) -> None:
        """Ensure the SQLite DB exists (merged from split parts if needed)."""
        full_path = join(str(self.resource_root / "data"), self.DATABASE_NAME)
        if exists(full_path):
            return
        # Re-use GameDatabase helpers but convert hard exits into exceptions
        if self.db._database_splits_exist():  # noqa: SLF001 — intentional reuse
            try:
                self.db._merge_database()  # noqa: SLF001
            except Exception as error:  # noqa: BLE001
                raise DatabaseError(f"Unable to merge database file: {error}") from error
            if not exists(full_path):
                raise DatabaseError("Unable to merge database file")
            return
        raise DatabaseError("Database split-files not found")

    def scan_library(
        self,
        library_path: str,
        *,
        crc_check: bool = False,
        on_progress: Optional[ProgressCallback] = None,
    ) -> list[Game]:
        """Scan subfolders under library_path and populate game_list."""
        self.ensure_database()
        self.library_path = library_path
        self.last_crc_check = bool(crc_check)
        self.game_list = []

        self._emit(on_progress, "scan", "Generating game list...", 0)
        sub_folders = self.utils.get_sub_folders(library_path)
        if not sub_folders:
            return self.game_list

        total = len(sub_folders)
        for index, sub_folder in enumerate(sub_folders):
            percent = int((index / max(total, 1)) * 100)
            self._emit(on_progress, "scan", f"Scanning {sub_folder}", percent)
            self._process_sub_folder(library_path, sub_folder, crc_check=crc_check)

        self.game_list.sort(key=lambda game: game.get_cue_sheet().get_game_name())
        self._emit(on_progress, "scan", "Scan complete", 100)
        return self.game_list

    def _process_sub_folder(self, selected_path: str, sub_folder: str, *, crc_check: bool) -> None:
        game_directory_path = join(selected_path, sub_folder)
        try:
            cue_sheets = self.utils.find_cue_sheets(game_directory_path)
        except OSError as error:
            print(f"ERROR: Skipping unreadable folder {game_directory_path}: {error}")
            return
        for cue_sheet in cue_sheets:
            game = self._create_game_from_cue(
                game_directory_path, cue_sheet, sub_folder, selected_path, crc_check=crc_check
            )
            if game:
                self.game_list.append(game)

    def _create_game_from_cue(
        self,
        game_directory_path: str,
        cue_sheet: str,
        sub_folder: str,
        selected_path: str,
        *,
        crc_check: bool,
    ) -> Optional[Game]:
        cue_sheet_path = join(game_directory_path, cue_sheet)

        cover_art_path = join(game_directory_path, cue_sheet[:-3])
        cover_art_present = exists(f"{cover_art_path}bmp") or exists(f"{cover_art_path}BMP")

        multi_disc_file_present = exists(join(game_directory_path, "MULTIDISC.LST"))
        cu2_present = exists(join(game_directory_path, f"{cue_sheet[:-3]}cu2"))
        cu2_required = self.utils.detect_cdda(cue_sheet_path)

        bin_files = self.utils.parse_cue_file(cue_sheet_path)
        if not bin_files:
            print(f"ERROR: Skipping game with missing BIN files: {cue_sheet_path}")
            return None

        game_id = self.utils.parse_game_id(bin_files[0].get_file_path())
        disc_number = self.db.get_database_disc_number(game_id) if game_id else 0
        game_name = Path(bin_files[0].get_file_name()).stem
        disc_collection = self.db.get_database_disc_collection(game_id) if game_id else []
        if disc_collection:
            disc_collection = literal_eval(disc_collection)

        libcrypt_required = self.db.get_libcrypt_status(game_id) if game_id else False

        the_cue_sheet = Cuesheet(cue_sheet, cue_sheet_path, game_name)
        for bin_file in bin_files:
            the_cue_sheet.add_bin_file(bin_file)

        the_game = Game(
            sub_folder,
            selected_path,
            game_id,
            disc_number,
            disc_collection,
            the_cue_sheet,
            cover_art_present,
            cu2_present,
            cu2_required,
            multi_disc_file_present,
            libcrypt_required,
        )

        self.utils.libcrypt_already_applied(the_game)
        if crc_check:
            the_game.set_crc_valid(self.utils.crc_check_bin(the_game))

        return the_game

    def process_games(
        self,
        *,
        redump_rename: bool = True,
        on_progress: Optional[ProgressCallback] = None,
    ) -> list[tuple[str, str]]:
        """Process the current game_list. Returns a list of (name, error) failures."""
        self.ensure_database()
        failed_games: list[tuple[str, str]] = []
        total = len(self.game_list)

        self._debug_print("\nPROCESSING GAMES...")
        for game_index, game in enumerate(self.game_list):
            game_name = game.get_cue_sheet().get_game_name()
            self._emit(on_progress, "process", f"Processing - {game_name}", 0, game_index)
            self._debug_print("\n***********************************************************")
            self._debug_print(f"GAME_ID: {game.get_id()}")
            self._debug_print(f"GAME_NAME: {game_name}")

            try:
                self._merge_multi_bin_files(game, on_progress=on_progress)
                self._emit(on_progress, "process", f"Processing - {game_name}", 30, game_index)

                self._generate_cu2_file(game)
                self._emit(on_progress, "process", f"Processing - {game_name}", 40, game_index)

                if redump_rename:
                    self.utils.rename_game_using_redump(game)
                self._emit(on_progress, "process", f"Processing - {game_name}", 50, game_index)

                self.utils.validate_game_name(game)
                self._emit(on_progress, "process", f"Processing - {game_name}", 65, game_index)

                self.utils.add_game_cover_art(game)
                self._emit(on_progress, "process", f"Processing - {game_name}", 75, game_index)

                self.utils.apply_libcrypt_patch(game)
                base = int(((game_index + 1) / max(total, 1)) * 100)
                self._emit(on_progress, "process", f"Processing - {game_name}", min(base, 95), game_index)

            except Exception as error:  # noqa: BLE001 — per-game isolation
                failed_games.append((game_name, str(error)))
                self._debug_print(f"ERROR processing {game_name}: {error}")
                print(f"ERROR processing {game_name}: {error}")
                self._emit(on_progress, "process", f"Failed - {game_name}", 0, game_index)

            self._debug_print("***********************************************************\n")

        self._emit(on_progress, "multidisc", "Generating multi-disc files...", 100)
        try:
            self.utils.generate_multidisc_files(self.game_list)
        except Exception as error:  # noqa: BLE001
            failed_games.append(("MULTIDISC.LST generation", str(error)))
            self._debug_print(f"ERROR generating multi-disc files: {error}")
            print(f"ERROR generating multi-disc files: {error}")

        self._emit(on_progress, "done", "Processing finished", 100)
        self._debug_print("Processing finished!\n")
        return failed_games

    def _merge_multi_bin_files(
        self, game: Game, on_progress: Optional[ProgressCallback] = None
    ) -> None:
        game_name = game.get_cue_sheet().get_game_name()
        game_full_path = join(game.get_directory_path(), game.get_directory_name())

        if len(game.get_cue_sheet().get_bin_files()) > 1:
            self._debug_print("MERGING BIN FILES...")
            self._emit(on_progress, "process", f"Merging bin files - {game_name}", 10)
            if not self.utils.merge_bin_files(game):
                raise RuntimeError(f"Failed to merge multi-bin files for {game_name}")

            bin_path = join(game_full_path, f"{game_name}.bin")
            if exists(bin_path):
                game.get_cue_sheet().set_bin_files([])
                game.get_cue_sheet().add_bin_file(Binfile(f"{game_name}.bin", bin_path))
            else:
                raise RuntimeError(f"Merged BIN not found after merge: {bin_path}")

    def _generate_cu2_file(self, game: Game) -> None:
        game_name = game.get_cue_sheet().get_game_name()
        game_full_path = join(game.get_directory_path(), game.get_directory_name())
        cue_full_path = join(game_full_path, game.get_cue_sheet().get_file_name())

        if game.get_cu2_required() and not game.get_cu2_present():
            self._debug_print("GENERATING CU2...")
            cu2_generated = self.cu2_generator.generate_cu2(cue_full_path, f"{game_name}.bin")
            if cu2_generated:
                game.set_cu2_present(True)

    def games_as_dicts(self) -> list[dict]:
        """Serialize the current game list for APIs / web UI."""
        rows = []
        for game in self.game_list:
            cue = game.get_cue_sheet()
            name = cue.get_game_name()
            rows.append(
                {
                    "id": game.get_id(),
                    "name": name,
                    "disc_number": game.get_disc_number(),
                    "bin_count": len(cue.get_bin_files()),
                    "name_valid": len(name) <= self.MAX_GAME_NAME_LENGTH and "." not in name,
                    "cover_art": game.get_cover_art_present(),
                    "cu2_required": game.get_cu2_required(),
                    "cu2_present": game.get_cu2_present(),
                    "multi_disc": game.get_disc_number() > 0,
                    "lst_present": game.get_multi_disc_file_present(),
                    "libcrypt_required": game.get_libcrypt_required(),
                    "libcrypt_applied": game.get_libcrypt_applied(),
                    "crc_checked": self.last_crc_check,
                    "crc_valid": game.get_crc_valid(),
                    "directory": join(game.get_directory_path(), game.get_directory_name()),
                }
            )
        return rows

    def summarize(self) -> dict:
        """Return summary counts for the current game_list."""
        unidentified = 0
        without_cover = 0
        multi_discs = 0
        multi_disc_games = 0
        multi_bin = 0
        invalid_names = 0

        for game in self.game_list:
            if game.get_id() is None:
                unidentified += 1
            disc_number = game.get_disc_number()
            # Count disc 0 (single-disc) and disc 1; skip later discs in a set
            if not game.get_cover_art_present() and int(disc_number or 0) < 2:
                without_cover += 1
            if self.utils.is_multi_disc(game):
                multi_discs += 1
                if int(disc_number) == 1:
                    multi_disc_games += 1
            if len(game.get_cue_sheet().get_bin_files()) > 1:
                multi_bin += 1
            name = game.get_cue_sheet().get_game_name()
            if len(name) > self.MAX_GAME_NAME_LENGTH or "." in name:
                invalid_names += 1

        return {
            "total_games": len(self.game_list),
            "unidentified": unidentified,
            "without_cover": without_cover,
            "multi_discs": multi_discs,
            "multi_disc_games": multi_disc_games,
            "multi_bin": multi_bin,
            "invalid_names": invalid_names,
        }
