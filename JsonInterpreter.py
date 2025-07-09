import json
from dataclasses import fields

from FileInterpreter import FileInterpreter
from TestFormat import TestFormat


class JsonInterpreter(FileInterpreter):
    @property
    def extension(self) -> str:
        """Intended to allow just file names passed in, and the extension added on while reading and writing"""
        return ".json"

    def write(self, formatted: TestFormat) -> str:
        """Takes a FileFormat, and returns a string to write to a file."""
        format_dict = {}
        for field in fields(formatted):
            format_dict[field.name] = getattr(formatted, field.name)
        return json.dumps(format_dict, indent=4)


    def read(self, file_contents: str) -> TestFormat:
        """
        Needs to take in the contents because there is always the chance that it only exists in the Google Drive
        Returns a FileFormat object to be messed with outside FileManager
        """
        data = json.loads(file_contents)
        field_names = {f.name for f in fields(TestFormat)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return TestFormat(**filtered_data)