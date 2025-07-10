import dropbox
from pathlib import Path
from typing import List
from dropbox.files import WriteMode

from CoreFunction.RemoteManagerABC import RemoteManager


class DropboxManager(RemoteManager):
    def __init__(self, access_token: str):
        self.dbx = dropbox.Dropbox(access_token)

    def _exists_sync(self, file_name: str) -> bool:
        """Return a bool if the file exists."""
        try:
            self.dbx.files_get_metadata(f"/{file_name}")
            return True
        except dropbox.exceptions.ApiError as e:
            if isinstance(e.error, dropbox.files.GetMetadataError):
                return False
            raise

    def _read_sync(self, file_name: str) -> str:
        """Returns the entire file's contents as a string."""
        metadata, res = self.dbx.files_download(f"/{file_name}")
        return res.content.decode()

    def _create_sync(self, file_name: str) -> str:
        """Creates a file with the name "file_name" """
        # Create an empty file
        self.dbx.files_upload(b"", f"/{file_name}", mode=WriteMode.add)
        return file_name

    def _write_sync(self, file_name: str, file_contents: str) -> None:
        """Writes to a file that is already created."""
        self.dbx.files_upload(file_contents.encode(), f"/{file_name}", mode=WriteMode.overwrite)

    def _delete_sync(self, file_name: str) -> None:
        """Deletes an already-made file."""
        self.dbx.files_delete_v2(f"/{file_name}")

    def _list_files_sync(self) -> List[str]:
        """Lists all files as names in strings."""
        entries = self.dbx.files_list_folder("").entries
        return [entry.name for entry in entries if isinstance(entry, dropbox.files.FileMetadata)]
