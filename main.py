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
from JsonInterpreter import JsonInterpreter
from TestFormat import TestFormat


async def main():
    load_dotenv()
    current_dir = Path(__file__).parent.resolve()
    google_file_id: str = os.getenv("GOOGLE_DRIVE_FILE_ID")
    google_service_key_path: Path = current_dir / os.getenv("GOOGLE_DRIVE_SERVICE_KEY")

    print(f"Using folder ID (repr): {repr(google_file_id)}")
    print(f"Using service key path: {google_service_key_path}")
    interpreter = JsonInterpreter()
    test_dir = current_dir / "TestDir"
    file_manager = FileManager(interpreter, base_dir=test_dir)
    test_data = TestFormat(info1="s", info2=3, info3=[1,2,"H"])
    file_manager.write(r"nul..\con\\/\:*?\"<>|🚫   ‍", test_data, True)
    test_data_revived: TestFormat = file_manager.read(r"nul..\con\\/\:*?\"<>|🚫   ‍")
    print(f"1: {test_data_revived.info1}\n2: {test_data_revived.info2}\n3: {test_data_revived.info3}")

if __name__ == "__main__":
    asyncio.run(main())

'''
async def run_drive_manager():
    print("\n--- Testing DriveManager (new) ---")
    load_dotenv()
    current_dir = Path(__file__).parent.resolve()
    google_file_id: str = os.getenv("GOOGLE_DRIVE_FILE_ID")
    google_service_key_path: Path = current_dir / os.getenv("GOOGLE_DRIVE_SERVICE_KEY")
    print(f"google file id: {google_file_id} \n google_service_key_path: {google_service_key_path}")

    drive_manager = DriveManager(google_service_key_path, google_file_id)

    try:
        await drive_manager.write("JOE.txt", "JOE IS GAY\n#")
        print("DriveManager write succeeded.")
    except Exception as e:
        print(f"DriveManager write failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_drive_manager())
'''