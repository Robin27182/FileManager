import asyncio
import time
from pathlib import Path
from pkgutil import resolve_name
from typing import Type

import dropbox
from dotenv import load_dotenv
import os

from CoreFunction.FileManager import FileManager
from Example.DropboxManager import DropboxManager
from Example.JsonInterpreter import JsonInterpreter
from TestFormat import TestFormat


async def main():
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=Path(__file__).parent.parent / "SensitiveInfo" / ".env")
    dropbox_token = os.getenv("DROPBOX_TOKEN")

    current_dir = Path(__file__).parent.resolve()
    test_dir = current_dir.parent / "LocalWrite"

    dropbox_manager = DropboxManager(dropbox_token)
    interpreter = JsonInterpreter()
    file_manager = FileManager(interpreter, base_dir=test_dir, remote_manager=None)

    test_data = TestFormat(info1="s", info2=3, info3=[1,2,"H"])

    for i in range(len("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()")):
        await file_manager.write("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()"[i], test_data, True)
        test_data_revived: TestFormat = await file_manager.read("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()"[i])

    time.sleep(10)
    for i in range(len("abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()")):
        await file_manager.delete("abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()"[i])

    print(f"1: {test_data_revived.info1}\n2: {test_data_revived.info2}\n3: {test_data_revived.info3}")

if __name__ == "__main__":
    asyncio.run(main())