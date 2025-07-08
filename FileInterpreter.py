from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import platform
from typing import final

from FileFormat import FileFormat


class FileInterpreter(ABC):
    """Assume the files exist"""
    @property
    @abstractmethod
    def extension(self) -> str:
        """Intended to allow just file names passed in, and the extension added on while reading and writing"""
        pass

    @abstractmethod
    def write(self, formatted: FileFormat) -> str:
        """Takes a FileFormat, and returns a string to write to a file."""
        pass

    @abstractmethod
    def read(self, file_contents: str) -> FileFormat:
        """
        Needs to take in the contents because there is always the chance that it only exists in the Google Drive
        Returns a FileFormat object to be messed with outside FileManager
        """
        pass