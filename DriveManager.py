import os
import tempfile
from io import BytesIO
from pathlib import Path

from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List

from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload, MediaFileUpload
import asyncio

class DriveManager:
    def __init__(self, service_account_file: Path, folder_id: str):
        if not service_account_file.exists():
            raise FileNotFoundError(f"Service account file not found: {service_account_file}")

        self.folder_id = folder_id

        # Define required scopes
        scopes = ["https://www.googleapis.com/auth/drive"]

        # Authenticate using service account
        self.creds = service_account.Credentials.from_service_account_file(
            str(service_account_file),
            scopes=scopes
        )

        # Build the Drive API client
        self.service = build("drive", "v3", credentials=self.creds)

    async def exists(self, file_name: str) -> bool:
        ...

    def _exists_sync(self, file_name: str) -> bool:
        ...


    async def read(self, file_name: str) -> str:
        return await asyncio.to_thread(self._read_sync, file_name)

    def _read_sync(self, file_name: str) -> str:
        file_id = self.service.files().list(
            q=f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false",
            fields="files(id)",
            pageSize=1
        ).execute()["files"][0]["id"]

        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, self.service.files().get_media(fileId=file_id))
        while True:
            _, done = downloader.next_chunk()
            if done:
                break

        return fh.getvalue().decode("utf-8")


    async def create(self, file: str) -> None:
        ...

    def _create_sync(self, file_name: str) -> None:
        ...

    async def write(self, file_name: str, file_contents: str) -> None:
        await asyncio.to_thread(self._write_sync, file_name, file_contents)

    def _write_sync(self, file_name: str, file_contents: str) -> None:
        # 1. Search for existing file with the same name in the folder
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(file_contents)
            tmp_path = tmp_file.name


        query = f"name = '{file_name}' and '{self.folder_id}' in parents and trashed = false"
        response = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = response.get('files', [])

        media = MediaFileUpload(tmp_path, resumable=True)
        if files:
            # File exists — update the first match
            file_id = files[0]['id']
            updated_file = self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            return updated_file.get('id')
        else:
            # File does not exist — create new
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]
            }
            created_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            return created_file.get('id')


    async def delete(self, file_name: str) -> None:
        ...

    def _delete_sync(self, file_name: str) -> None:
        ...

    async def list_files(self) -> List[str]:
        ...

    def _list_files_sync(self) -> List[str]:
        ...