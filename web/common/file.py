#!/bin/env python
import os

from fastapi import UploadFile
from typing import Optional, Union, BinaryIO


class FileManager:
    def __init__(self, base_path: str = "/") -> None:
        self.base_path = base_path

    def get_path(
        self,
        filename: str,
        base_path: Optional[str] = None,
    ):
        return os.path.join(
            self.base_path if base_path is None else base_path, filename
        )

    async def save(
        self,
        filename: str,
        data: Union[bytes, BinaryIO, UploadFile],
        base_path: Optional[str] = None,
    ) -> str:
        with open(
            self.get_path(filename, base_path),
            "wb",
        ) as f:
            if isinstance(data, bytes):
                f.write(data)
            elif isinstance(data, BinaryIO):
                f.write(data.read())
            elif isinstance(data, UploadFile):
                f.write(await data.read())
        return filename

    async def close(self):
        pass
