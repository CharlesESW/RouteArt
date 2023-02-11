from pathlib import Path

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
