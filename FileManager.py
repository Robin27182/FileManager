from enum import Enum, auto
from pathlib import Path
from typing import List

from DriveManager import DriveManager
from FileFormat import FileFormat
from FileInterpreter import FileInterpreter


class SaveMode(Enum):
    drive_only = auto()
    local_only = auto()
    drive_and_local = auto()


class FileManager:
    """
    Use: Make a FileInterpreter and a FileFormat that match your scenario. Need be, give it a DriveManager (Not your own)
    Under the assumption that:
    1. if a file does not exist when reading, raise an error.
    2. if a file exists in Google Drive and not Locally (or vice versa), raise an error. (Only if both are being used)
    3. if the mode is drive_only, all passed files are strings
    """
    def __init__(self,interpreter: FileInterpreter, base_dir: str | Path = None, drive_manager: DriveManager = None) -> None:
        """
        :param interpreter: A FileInterpreter instance for reading and writing for specific scenarios
        :param drive_manager: An optional instance of DriveManager, just to upload copies to one's Google Drive
        :param drive_only: An option to read/write to only Google Drive, or instead go off of nearby files, and backup to Google Drive.
        """
        self.interpreter = interpreter
        self.drive_manager = drive_manager
        self.base_dir: Path = Path(base_dir).resolve()
        self.save_mode: SaveMode = None

        # Logic can be simplified, but it's easier to read like this
        local = base_dir is not None
        drive = drive_manager is not None
        if drive and local:
            self.save_mode = SaveMode.drive_and_local
        elif drive:
            self.save_mode = SaveMode.drive_only
        elif local:
            self.save_mode = SaveMode.local_only
        else:
            raise Exception("You need to pass either a base_dir or drive_manager instance to save files.")

        # This next part is for some sanitization; replace bad characters with weird stuff that we understand.
        self.replacements = {
            '<': '_lt_',
            '>': '_gt_',
            ':': '_colon_',
            '"': '_quote_',
            '/': '_slash_',
            '\\': '_bslash_',
            '|': '_pipe_',
            '?': '_q_',
            '*': '_star_'
        }
        if drive and not self.base_dir.is_dir():
            raise TypeError("The base directory given is not a valid directory")



    def _sanitize_file_name(self, file_name: str | Path) -> str:
        """
        WOO this is a pain. Call this before running most functions. This sanitized file names by...
        Making sure a str does not have the correct extension, else removes it. abc.txt -> abc
        Removing the extension from a path. dir/abc.txt -> abc
        Replaces invalid file chars. ?* -> _q__star_
        Takes the result, slaps on the extension, and it *should* be the same file.
        (This is private because all sanitization is done inside this class. They should not NEED to use this.)
        """
        required_ext = self.interpreter.extension

        if isinstance(file_name, str):
            path = Path(file_name)
            stem = path.stem if path.suffix == self.interpreter.extension else path.name

        elif isinstance(file_name, Path):
            stem = file_name.stem

        else:
            raise TypeError(f"File {file_name} must be a string or a Path.")

        # Sanitize illegal characters
        for bad_c, replace_c in self.replacements.items():
            stem = stem.replace(bad_c, replace_c)

        stem = stem.rstrip(". ") # Windows gets mad

        return stem + required_ext


    def _to_path(self, file: str | Path) -> Path:
        """Make sure that drive_only cannot see this EVER (why this is private, along with you shouldn't NEED a path"""
        if self.save_mode == SaveMode.drive_only:
            raise TypeError("Some file tried to become a path in drive_only")

        if isinstance(file, str):
            file = (self.base_dir / file).resolve()

        if not isinstance(file, Path):
            raise TypeError("File needs to be either a string or a Path.")

        return file


    def _check_contents(self, file: str | Path, give_error = True) -> bool:
        if self.save_mode is not SaveMode.drive_and_local: # Unrelated to give_error because this is a big issue
            raise FileNotFoundError("Tried to match the file contents of local and Google Drive, but one does not exist")

        file: Path = self._to_path(file)

        google_contents = self.drive_manager.read(file.name)
        local_contents = file.read_text()

        if local_contents != google_contents:
            if give_error:
                raise Exception(f"File mismatch: {file} differs between local and Drive copies.")
            else:
                return False
        return True


    def _exist(self, file: str | Path, give_error = True, sanitize = True) -> bool:
        """Gives an error for non-existing files unless give_error is False. Returns a boolean if the files exist"""
        if sanitize:
            file: str = self._sanitize_file_name(file)

        exist = True

        match self.save_mode:
            case SaveMode.drive_only:
                if not self.drive_manager.exists(file):
                    exist = False

            case SaveMode.local_only:
                file: Path = self._to_path(file)
                exist = file.exists()

            case SaveMode.drive_and_local:
                file: Path = self._to_path(file)
                exist = file.exists() and self.drive_manager.exists(file.name)

            case _:
                # Only need to call the _ case once, the other functions call this ASAP
                raise Exception("Woah there why do you not have a save mode?")

        if give_error and not exist:
            raise FileNotFoundError(f"File {file} does not exist")
        return exist

    def exist(self, file: str | Path, give_error = True) -> bool:
        """Gives an error for non-existing files unless give_error is False. Returns a boolean if the files exist"""
        return self._exist(file, give_error=give_error, sanitize=True) # True, because we are scared of what the user gives


    def _create(self, file_name: str, sanitize = True) -> None:
        """Creates a file, makes sure it doesn't exist. Allows sanitization check to not sanitize multiple times."""
        if sanitize:
            file_name: str = self._sanitize_file_name(file_name)

        if self._exist(file_name, give_error=False, sanitize=False): # We already sanitized
            raise Exception(f"Tried to create a file ({file_name}) that already exists.")

        match self.save_mode:
            case SaveMode.drive_only:
                self.drive_manager.create(file_name)

            case SaveMode.local_only:
                path: Path = self.base_dir / file_name
                path.touch()

            case SaveMode.drive_and_local:
                self.drive_manager.create(file_name)
                path: Path = self.base_dir / file_name
                path.touch()

    def create(self, file_name: str) -> None: # Does not accept a Path because you should not have a path that doesn't exist
        """Creates a file, makes sure it doesn't exist."""
        self._create(file_name, sanitize=True) # True, because we are scared of what the user gives


    def _delete(self, file: str | Path, check_exists=True, sanitize=True) -> None:
        if sanitize:
            file: str = self._sanitize_file_name(file)
        if check_exists:
            self._exist(file, give_error=True, sanitize=False)

        match self.save_mode:
            case SaveMode.drive_only:
                self.drive_manager.delete(file)

            case SaveMode.local_only:
                file: Path = self._to_path(file)
                file.unlink(missing_ok=False)

            case SaveMode.drive_and_local:
                file: Path = self._to_path(file)
                self.drive_manager.delete(file.name)
                file.unlink(missing_ok=False)

    def delete(self, file: str | Path) -> None:
        self._delete(file, check_exists=True, sanitize=True)


    def _read_raw(self, file: str | Path) -> str:
        """
        We are trusting that the file exists and that the file is a string in drive_only
        These checks should be dealt with in a slightly higher-level function
        """
        contents: str = None

        match self.save_mode:
            case SaveMode.drive_only:
                contents = self.drive_manager.read(file)

            case SaveMode.local_only:
                contents = self._to_path(file).read_text()

            case SaveMode.drive_and_local:
                self._check_contents(file) # Checks if contents match
                contents = self._to_path(file).read_text() # Doesn't matter if we use the Google Drive either.
        return contents

    def _read(self, file: str | Path, check_exists = True, sanitize = True) -> FileFormat:
        """A more-specific version of self.read, we just don't want to check/sanitize unnecessarily"""
        if sanitize:
            file: str = self._sanitize_file_name(file)

        if check_exists:
            self._exist(file, sanitize=False) # We already sanitized

        contents = self._read_raw(file)
        formatted: FileFormat = self.interpreter.read(contents)
        return formatted

    def read(self, file: str | Path) -> FileFormat:
        return self._read(file, check_exists=True, sanitize=True) # True, because we are scared of what the user gives


    def _write_raw(self, file: str | Path, file_contents: str) -> None:
        """
        We are trusting that the file exists and that the file is a string in drive_only
        These checks should be dealt with in a slightly higher-level function
        """
        match self.save_mode:
            case SaveMode.drive_only:
                self.drive_manager.write(file, file_contents)

            case SaveMode.local_only:
                file_path: Path = self._to_path(file)
                file_path.write_text(file_contents)

            case SaveMode.drive_and_local:
                file_path: Path = self._to_path(file)
                self.drive_manager.write(file, file_contents)
                file_path.write_text(file_contents)

    def _write(self, file: str | Path, formatted: FileFormat, create_if_none = False, sanitize = True) -> None:
        """Does not have a check_exists because that is what create_if_none inherently does."""
        if sanitize:
            file: str = self._sanitize_file_name(file)

        # Do not sanitize, we already have
        if create_if_none and not self._exist(file, give_error=False, sanitize=False):
            # Does not check if file is a Path because it was probably sanitized, and not-existing files shouldn't be Paths
            self._create(file, sanitize=False)

        contents = self.interpreter.write(formatted)
        self._write_raw(file, contents)

    def write(self, file: str | Path, formatted: FileFormat, create_if_none = False) -> None:
        self._write(file, formatted, create_if_none, sanitize=True)


    def _list_files(self) -> List[str]:
        files: List[str] = []
        match self.save_mode:
            case SaveMode.drive_only:
                files = self.drive_manager.list_files()

            case SaveMode.local_only:
                files = [f.name for f in self.base_dir.iterdir() if f.is_file()]

            case SaveMode.drive_and_local:
                drive_files = self.drive_manager.list_files()
                local_files = [f.name for f in self.base_dir.iterdir() if f.is_file()]
                # Checks galore incoming
                if len(drive_files) != len(local_files):
                    raise Exception("There is not an equal amount of files in both areas.")
                for file in local_files:
                    if file not in drive_files:
                        raise FileNotFoundError(f"Could not find file \"{file}\" in drive files, but it was  found in local files.")
                    self._check_contents(file)
                files = local_files # Doesn't matter which
        return files

    def list_file_contents(self) -> List[FileFormat]:
        """
        Does not list file names, because the user should never interact with file names.
        All the user is intended to do is give and take FileFormats.
        """
        file_contents: List[FileFormat] = []
        files: List[str] = self._list_files()
        for file in files:
            file_contents.append(self._read(file, check_exists=False, sanitize=False))
        return file_contents