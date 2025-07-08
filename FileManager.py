from enum import Enum, auto
from pathlib import Path
import os
import shutil
import platform

from DriveManager import DriveManager
from FileFormat import FileFormat
from FileInterpreter import FileInterpreter

class CheckAndSanitize:
    def __init__(self, sanitize = True, check_exists = True):
        self.sanitize = sanitize
        self.check_exists = check_exists

    def __call__(self, func):
        def wrapper(instance, file_name: str | Path, *args, **kwargs):
            if self.sanitize:


class FileManager:
    """
    Use: Make a FileInterpreter and a FileFormat that match your scenario. Need be, give it a DriveManager (Not your own)
    Under the assumption that...
    if a file does not exist when reading, raise an error.
    if a file exists in Google Drive and not Locally (or vice versa), raise an error. (Only if both are being used)
    if the mode is drive_only, all passed files are strings
    """
    #TODO Implement base_dir's None ness
    def __init__(self,interpreter: FileInterpreter, base_dir: str | Path = None, drive_manager: DriveManager = None, drive_only: bool = False) -> None:
        """
        :param interpreter: A FileInterpreter instance for reading and writing for specific scenarios
        :param drive_manager: An optional instance of DriveManager, just to upload copies to one's Google Drive
        :param drive_only: An option to read/write to only Google Drive, or instead go off of nearby files, and backup to Google Drive.
        """
        self.interpreter = interpreter
        self.drive_manager = drive_manager
        self.base_dir: Path = Path(base_dir).resolve()
        self.save_mode: SaveMode = None

        #Logic can be simplified, but it's easier to read like this
        if drive_manager is None and drive_only is True:
            raise TypeError("Cannot only use drive if drive is None")
        elif drive_manager is None and drive_only is False:
            self.save_mode = SaveMode.local_only
        elif drive_manager is not None and drive_only is True:
            self.save_mode = SaveMode.drive_only
        elif drive_manager is not None and drive_only is False:
            self.save_mode = SaveMode.drive_and_local

        #This next part is for some sanitization; replace bad characters with weird stuff that we understand.
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


        if not self.base_dir.is_dir():
            raise TypeError("The file given is not a valid directory")

    def sanitize_file_name(self, file_name: str | Path) -> str:
        """
        WOO this is a pain. Call this before running most functions. This sanitized file names by...
        Making sure a str does not have the correct extension, else removes it. abc.txt -> abc
        Removing the extension from a path. dir/abc.txt -> abc
        Replaces invalid file chars. ?* -> _q__star_
        Takes the result, slaps on the extension, and it *should* be the same file.
        """
        required_ext = self.interpreter.extension

        if isinstance(file_name, str):
            path = Path(file_name)
            if path.suffix == required_ext:
                stem = path.stem # We are adding the extension later, lets remove it to not have .txt.txt
            else:
                stem = path.name # Just doesnt have the extension

        elif isinstance(file_name, Path):
            stem = file_name.stem

        else:
            raise TypeError(f"File {file_name} must be a string or a Path.")

        # Sanitize illegal characters
        for bad_c, replace_c in self.replacements.items():
            stem = stem.replace(bad_c, replace_c)

        stem = stem.rstrip(". ") # Windows gets mad

        return stem + required_ext

    def to_path(self, file: str | Path) -> Path:
        """Make sure this is never called anywhere drive_only can see it"""
        #TODO Probably need some crap talking about the base_dir
        if isinstance(file, str):
            file = Path(file).resolve()
        if not isinstance(file, Path):
            raise TypeError("File needs to be either a string or a Path.")
        return file

    def exist(self, file: str | Path, give_error = True) -> bool:
        exist = True

        match self.save_mode:
            case SaveMode.drive_only:
                if not self.drive_manager.exists(file):
                    exist = False

            case SaveMode.local_only:
                file: Path = self.to_path(file)
                exist = file.exists()

            case SaveMode.drive_and_local:
                file: Path = self.to_path(file)
                exist = not file.exists() or not self.drive_manager.exists(file.name)

            case _:
                #Only need to call the _ case once, the other functions call this ASAP
                raise Exception("Woah there why do you not have a save mode?")

        if give_error and not exist:
            raise FileNotFoundError(f"File {file} does not exist")
        return exist


    def read_raw(self, file: str | Path) -> str:
        """Please just use strings for the file names. Paths start making things suck with Google Drive"""
        self.exist(file) #Used for the checks
        contents: str = None

        match self.save_mode:
            case SaveMode.drive_only:
                contents = self.drive_manager.read(file)

            case SaveMode.local_only:
                file: Path = self.to_path(file)
                with open(file, "r") as f:
                    contents = f.read()

            case SaveMode.drive_and_local:
                file: Path = self.to_path(file)
                google_contents = self.drive_manager.read(file.name)

                with open(file, "r") as f:
                    local_contents = f.read()

                if local_contents != google_contents:
                    raise Exception(f"File mismatch: {file} differs between local and Drive copies.")

                contents = local_contents
        return contents


    def write_raw(self, file: str | Path, file_contents: str) -> None:
        self.exist(file) #Used for the checks
        match self.save_mode:
            case SaveMode.drive_only:
                self.drive_manager.write(file, file_contents)

            case SaveMode.local_only:
                file: Path = self.to_path(file)
                with open(file, "w") as f:
                    f.write(file_contents)

            case SaveMode.drive_and_local:
                file: Path = self.to_path(file)
                self.drive_manager.write(file.name, file_contents)



    def _create(self, filename: str) -> None:
        if self.drive_only:
            self.drive_manager.create(filename)
        else:
            path: Path = self.base_dir / filename
            path.touch()

    def read(self, file: str | Path) -> FileFormat:
        contents = self.read_raw(file)
        return self.interpreter.read(contents)

    def write(self, file: str | Path, formatted: FileFormat) -> None:


class SaveMode(Enum):
    drive_only = auto()
    local_only = auto()
    drive_and_local = auto()

"""
For copy and paste:
match self.save_mode:
    case SaveMode.drive_only:
        ...
    case SaveMode.local_only:
        ...
    case SaveMode.drive_and_local:
        ...
"""