'''
Sqlite3 database functions
The application uses a local Sqlite3 database to store game names and game cover art

The local database file has been split into 4 separate files in the repo
This is due to the 100MB file size limit in GitHub
The application will merge the split database files into a single file when it is launched
'''

from sys import exit
from os import remove, makedirs
from os.path import exists, join, getsize
from sqlite3 import connect, Error


class GameDatabase:
    """Manages SQLite3 database operations for game data and assets"""
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self._database_path = None
        self._database_file = None
        self._database_full_path = None


    # ************************************************************************************
    def _debug_print(self, message: str):
        """Print debug messages if debug mode is enabled"""
        if self.debug_mode:
            print(message)
    # ************************************************************************************


    # ************************************************************************************
    def _split_database(self):
        """Splits the database file into 4 equal parts"""
        if not exists(self._database_path):
            makedirs(self._database_path)

        file_size = getsize(self._database_full_path)
        chunk_size = file_size // 4

        with open(self._database_full_path, 'rb') as f:
            for i in range(4):
                if i == 3:
                    chunk_size = file_size - (chunk_size * 3)

                chunk_data = f.read(chunk_size)
                output_path = join(self._database_path, f'psio_assist_db_part_{i+1}')
                with open(output_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
    # ************************************************************************************


    # ************************************************************************************
    def _merge_database(self):
        """Merges the 4 split database files back into a single file"""
        with open(self._database_full_path, 'wb') as outfile:
            for i in range(1, 5):
                part_path = join(self._database_path, f'psio_assist_db_part_{i}')
                if not exists(part_path):
                    raise FileNotFoundError(f"Part file {part_path} not found")

                with open(part_path, 'rb') as infile:
                    outfile.write(infile.read())

        # Keep the split parts so fresh checkouts / reinstalls remain redistributable
    # ************************************************************************************


    # ************************************************************************************
    def _database_splits_exist(self):
        """Checks if each of the database split-files exist"""
        for i in range(1, 5):
            if not exists(join(self._database_path, f'psio_assist_db_part_{i}')):
                return False
        return True
    # ************************************************************************************


    # ************************************************************************************
    def _delete_database_splits(self):
        """Delete the database split-files"""
        for i in range(1, 5):
            part_path = join(self._database_path, f'psio_assist_db_part_{i}')
            if exists(part_path):
                remove(part_path)
    # ************************************************************************************


    # ************************************************************************************
    def _create_connection(self):
        """Establish a connection with the local SQLite3 database"""
        try:
            conn = connect(self._database_full_path)
            return conn
        except Error as error:
            print(error)
            return None
    # ************************************************************************************


    # ************************************************************************************
    def set_database_path(self, database_path: str, database_name: str):
        """Set the database path based on whether running as script or executable"""
        self._database_path = database_path
        self._database_file = database_name
        self._database_full_path = join(database_path, database_name)
    # ************************************************************************************


    # ************************************************************************************
    def database_is_readable(self) -> bool:
        """Return True when the merged database opens and passes a quick check.

        A CRLF-corrupted split merge still exists on disk but raises
        'database disk image is malformed' on query. Callers must not treat
        that as an empty result set.
        """
        if not self._database_full_path or not exists(self._database_full_path):
            return False
        try:
            conn = connect(f'file:{self._database_full_path}?mode=ro', uri=True)
        except Error:
            return False
        try:
            row = conn.execute('PRAGMA quick_check').fetchone()
            return bool(row) and row[0] == 'ok'
        except Error:
            return False
        finally:
            conn.close()
    # ************************************************************************************


    # ************************************************************************************
    def ensure_database_exists(self):
        """Ensures that the database file exists and has been merged"""
        if not exists(self._database_full_path):
            if self._database_splits_exist():
                self._merge_database()
                if not exists(self._database_full_path):
                    print('\n******************************')
                    print('Unable to merge database file!')
                    print('******************************\n')
                    exit()
            else:
                print('\n******************************')
                print('Database split-files not found!')
                print('******************************\n')
                exit()
    # ************************************************************************************


    # ************************************************************************************
    def select(self, select_query: str):
        """Select data from the local database"""
        rows = []
        conn = self._create_connection()
        try:
            if conn:
                cursor = conn.cursor()
                cursor.execute(select_query)
                rows = cursor.fetchall()
                cursor.close()
        except Error:
            pass
        finally:
            if conn:
                conn.close()
        return rows
    # ************************************************************************************


    # ************************************************************************************
    def _extract_game_cover_blob(self, row_id, image_out_path: str):
        """Extract the game cover art data from the local database"""
        conn = self._create_connection()
        try:
            if conn:
                cursor = conn.cursor()
                with open(image_out_path, 'wb') as output_file:
                    cursor.execute(f'SELECT psio FROM covers WHERE id = {row_id};')
                    image_blob = cursor.fetchone()
                    output_file.write(image_blob[0])
                cursor.close()
        except Error:
            pass
        finally:
            if conn:
                conn.close()
    # ************************************************************************************


    # ************************************************************************************
    def _extract_game_libcrypt_patch_blob(self, row_id, ppf_out_path: str):
        """Extract the game LibCrypt PPF patch data from the local database"""
        conn = self._create_connection()
        try:
            if conn:
                cursor = conn.cursor()
                with open(ppf_out_path, 'wb') as output_file:
                    cursor.execute(f'SELECT psio FROM libcrypt_patches WHERE id = {row_id};')
                    patch_blob = cursor.fetchone()
                    output_file.write(patch_blob[0])
                cursor.close()
        except Error:
            pass
        finally:
            if conn:
                conn.close()
    # ************************************************************************************


    # ************************************************************************************
    def get_database_disc_collection(self, game_id: str) -> str:
        """Get the game collection from the local database"""
        if not game_id:
            return ''

        formatted_game_id = game_id.replace('-', '_')
        query = f'SELECT collection FROM games WHERE game_id = "{formatted_game_id}"'
        response = self.select(query)
        return response[0][0] if response else ''
    # ************************************************************************************


    # ************************************************************************************
    def get_redump_name(self, game_id: str) -> str:
        """Get game name from Redump/PSX Data-Centre stored in local database"""
        if not game_id:
            return ''

        formatted_game_id = game_id.replace('-', '_')
        query = f'SELECT name FROM games WHERE game_id = "{formatted_game_id}"'
        response = self.select(query)
        return response[0][0] if response else ''
    # ************************************************************************************


    # ************************************************************************************
    def get_track_info(self, game_id: str):
        """Get disc track info from the local database"""
        if not game_id:
            return

        formatted_game_id = game_id.replace('-', '_')
        query = (
            f'SELECT track_number, pregap, sectors, size, crc '
            f'FROM tracks '
            f'WHERE game_id = "{formatted_game_id}" '
            f'ORDER BY track_number'
        )
        return self.select(query)
    # ************************************************************************************


    # ************************************************************************************
    def get_database_disc_number(self, game_id: str):
        """Get disc number from the local database"""
        if not game_id:
            return

        formatted_game_id = game_id.replace('-', '_')
        query = f'SELECT disc_number FROM games WHERE game_id = "{formatted_game_id}"'
        response = self.select(query)
        return response[0][0] if response else 0
    # ************************************************************************************


    # ************************************************************************************
    # Multi-disc LibCrypt PPFs are stored once, with X in place of the disc digit
    # (SLES_02082 and SLES_12082 both use SLES_X2082).
    # Some reprints share a serial with the protected release but are not LibCrypt.
    # The byte is the revision marker used by libcrypt-patcher at that offset.
    _LIBCRYPT_SKIP_BYTE = {
        "SLES_01879": (0x9368, 0x16),  # OverBlood 2 Europe disc 1 v1.1
        "SLES_11879": (0x9368, 0xF7),  # OverBlood 2 Europe disc 2 v1.1
    }
    # Formula One 99 beta keeps the retail boot id. This byte selects the beta PPF.
    _LIBCRYPT_ALT_BYTE = {
        "SCES_01979": (0x9368, 0xE6, "SCED_01979"),
    }

    def _formatted_game_id(self, game_id: str) -> str:
        return game_id.replace('-', '_')

    def _byte_at(self, bin_path: str, offset: int):
        """Return one byte from a disc image, or None if it cannot be read."""
        if not bin_path or not exists(bin_path):
            return None
        try:
            with open(bin_path, 'rb') as bin_file:
                bin_file.seek(offset)
                found = bin_file.read(1)
        except OSError:
            return None
        return found[0] if len(found) == 1 else None

    def _libcrypt_lookup_id(self, game_id: str, bin_path: str = None) -> str:
        """Serial used to find a patch, after a same-id revision check."""
        formatted = self._formatted_game_id(game_id)
        alt = self._LIBCRYPT_ALT_BYTE.get(formatted)
        if alt and bin_path:
            offset, marker, alt_id = alt
            if self._byte_at(bin_path, offset) == marker:
                return alt_id
        return formatted

    def _libcrypt_patch_skipped(self, game_id: str, bin_path: str = None) -> bool:
        """True when this image is a reprint that must not be patched."""
        spec = self._LIBCRYPT_SKIP_BYTE.get(self._formatted_game_id(game_id))
        if not spec or not bin_path:
            return False
        offset, marker = spec
        return self._byte_at(bin_path, offset) == marker

    def _libcrypt_patch_candidates(self, formatted_game_id: str) -> list:
        candidates = [formatted_game_id]
        # SLES_02082 -> SLES_X2082
        if (
            len(formatted_game_id) == 10
            and formatted_game_id[4] == '_'
            and formatted_game_id[5:].isdigit()
        ):
            shared = formatted_game_id[:5] + 'X' + formatted_game_id[6:]
            if shared not in candidates:
                candidates.append(shared)
        return candidates

    def _libcrypt_patch_row_id(self, game_id: str, bin_path: str = None):
        """Row id of the PPF for this disc, or None."""
        if not game_id or self._libcrypt_patch_skipped(game_id, bin_path):
            return None

        lookup_id = self._libcrypt_lookup_id(game_id, bin_path)
        for candidate in self._libcrypt_patch_candidates(lookup_id):
            response = self.select(
                f'SELECT id FROM libcrypt_patches WHERE game_id = "{candidate}"'
            )
            if response:
                return response[0][0]
        return None

    def get_libcrypt_status(self, game_id: str, bin_path: str = None):
        """Get libcrypt status from local database.

        The games.libcrypt flag is incomplete for some titles that still have
        patches in libcrypt_patches (e.g. SCES_02105 CTR Europe). Treat a game
        as LibCrypt-required if either the flag is set or a patch is available.
        """
        if not game_id:
            return False

        formatted_game_id = self._formatted_game_id(game_id)
        query = f'SELECT libcrypt FROM games WHERE game_id = "{formatted_game_id}"'
        response = self.select(query)
        if response and response[0][0]:
            return True
        return self.libcrypt_patch_available(game_id, bin_path)
    # ************************************************************************************


    # ************************************************************************************
    def libcrypt_patch_available(self, game_id: str, bin_path: str = None) -> bool:
        """Check if LibCrypt PPF patch is available in local database"""
        return self._libcrypt_patch_row_id(game_id, bin_path) is not None
    # ************************************************************************************


    # ************************************************************************************
    def copy_game_cover(self, output_path: str, game_id: str, game_name: str):
        """Copy game front cover art if available in local database"""
        if not game_id:
            return

        formatted_game_id = game_id.replace('-', '_')
        query = f'SELECT id FROM covers WHERE game_id = "{formatted_game_id}"'
        response = self.select(query)

        if response:
            row_id = response[0][0]
            image_out_path = join(output_path, f'{game_name}.bmp')
            self._extract_game_cover_blob(row_id, image_out_path)
    # ************************************************************************************


    # ************************************************************************************
    def copy_libcrypt_patch(self, output_path: str, game_id: str, bin_path: str = None):
        """Copy LibCrypt PPF patch file if available in local database"""
        row_id = self._libcrypt_patch_row_id(game_id, bin_path)
        if row_id is not None:
            ppf_out_path = join(output_path, f'{game_id}.ppf')
            self._extract_game_libcrypt_patch_blob(row_id, ppf_out_path)
    # ************************************************************************************
