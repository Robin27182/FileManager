from dataclasses import dataclass
from typing import List, Any

from CoreFunction.FileFormatABC import FileFormat

@dataclass
class TestFormat(FileFormat):
    info1: str
    info2: int
    info3: List[Any]