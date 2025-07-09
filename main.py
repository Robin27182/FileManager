import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.errors import HttpError

from DriveManager import DriveManager
from FileManager import FileManager


async def main():
    load_dotenv()
    current_dir = Path(__file__).parent.resolve()
    google_file_id: str = os.getenv("GOOGLE_DRIVE_FILE_ID")
    google_service_key_path: Path = current_dir / os.getenv("GOOGLE_DRIVE_SERVICE_KEY")

    print(f"Using folder ID (repr): {repr(google_file_id)}")
    print(f"Using service key path: {google_service_key_path}")

    file_manager = FileManager(current_dir)


if __name__ == "__main__":
    asyncio.run(main())
