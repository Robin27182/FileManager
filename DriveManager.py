from typing import List


class DriveManager:
    def __init__(self, crap):
        ...

    def exists(self, file: str) -> bool:
        ...

    def read(self, file: str) -> str:
        ...

    def create(self, filename: str) -> None:
        ...

    def write(self, file_name: str, file_contents: str) -> None:
        ...

    def delete(self, file_name: str) -> None:
        ...

    def list_files(self) -> List[str]:
        ...