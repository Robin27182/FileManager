from abc import ABC, abstractmethod

from pathlib import Path

from typing import List, final

import asyncio

class RemoteManager(ABC):
    """
    DO NOT DO EXTRA EXCEPTION CHECKS!!!
    FileManager will deal with all cases, checking just wastes time.
    """
    @abstractmethod
    def __init__(self, *args):
        """Init the file system. Probably need authentication args."""
        pass

    @final
    async def exists(self, file_name: str) -> bool:
        """
        Return a bool if the file exists; do not raise errors.
        Calls user-implemented function for async purposes.
        """
        return await asyncio.to_thread(self._exists_sync, file_name)

    @abstractmethod
    def _exists_sync(self, file_name: str) -> bool:
        """Return a bool if the file exists. Do not raise errors."""
        pass

    @final
    async def read(self, file_name: str) -> str:
        """
        Returns the entire file's contents as a string.
        Calls user-implemented function for async purposes.
        """
        return await asyncio.to_thread(self._read_sync, file_name)

    @abstractmethod
    def _read_sync(self, file_name: str) -> str:
        """Returns the entire file's contents as a string."""
        pass

    @final
    async def create(self, file_name: str) -> None:
        """
        Creates a file with the name "file_name".
        Calls user-implemented function for async purposes.
        """
        await asyncio.to_thread(self._create_sync, file_name)

    @abstractmethod
    def _create_sync(self, file_name: str) -> str:
        """Creates a file with the name "file_name" """
        pass

    @final
    async def write(self, file_name: str, file_contents: str) -> None:
        """
        Writes to a file that is already created.
        Calls user-implemented function for async purposes.
        """
        await asyncio.to_thread(self._write_sync, file_name, file_contents)

    @abstractmethod
    def _write_sync(self, file_name: str, file_contents: str) -> None:
        """Writes to a file that is already created. DO NOT CREATE A FILE IN THIS IMPLEMENTATION."""
        pass

    @final
    async def delete(self, file_name: str) -> None:
        """
        Deletes an already-made file.
        Calls user-implemented function for async purposes.
        """
        await asyncio.to_thread(self._delete_sync, file_name)

    @abstractmethod
    def _delete_sync(self, file_name: str) -> None:
        """Deletes an already-made file."""
        pass

    @final
    async def list_files(self) -> List[str]:
        """
        Lists all files as names in strings.
        Calls user-implemented function for async purposes.
        """
        return await asyncio.to_thread(self._list_files_sync)

    @abstractmethod
    def _list_files_sync(self) -> List[str]:
        """Lists all files as names in strings."""
        pass