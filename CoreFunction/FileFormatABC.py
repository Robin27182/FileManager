from abc import ABC
from dataclasses import dataclass


@dataclass
class FileFormat(ABC):
    """
    Implement to hold all file data.
    Passed from FileReader, and to FileWriter
    Intended to be made only outside FileManager to write.
    """
    pass