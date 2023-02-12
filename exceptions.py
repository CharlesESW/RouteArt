from pathlib import Path
from typing import Collection

from requests import Response

class EndOfFileError(Exception):
    DEFAULT_MESSAGE = "Cannot read next line because end of file has been reached."

    def __init__(self, message: str = None, file_path: Path = None, line_number: int = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE
        self.file_path = file_path

        if isinstance(line_number, int):
            if line_number < 0:
                raise ValueError("Argument line_number must be greater than or equal to 0.")
        self.line_number = line_number

        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self):
        return f"{self.message} (file_path={repr(self.file_path)}, line_number={repr(self.line_number)})"


class FailedRequestError(Exception):
    DEFAULT_MESSAGE = "External HTTP request failed."

    def __init__(self, message: str = None, response: Response = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE
        self.response = response

        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self):
        return f"{self.message} (response={repr(self.response)})"

class SocketDataError(IOError):
    DEFAULT_MESSAGE = "No/invalid data was received at the socket receiver."

    def __init__(self, message: str = None, socket_data: Collection[str] = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE
        self.socket_data = socket_data

        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self):
        return f"{self.message} (socket_data={repr(self.socket_data)})"

class EmptyImageFilePath(ValueError):
    DEFAULT_MESSAGE = "Image object does not have a valid file path."

    def __init__(self, message: str = None, file_path: str = None) -> None:
        self.message: str = message or self.DEFAULT_MESSAGE
        self.socket_data = file_path

        super().__init__(message or self.DEFAULT_MESSAGE)

    def __str__(self):
        return f"{self.message} (file_path={repr(self.file_path)})"
