from os import getenv
from time import sleep

from dotenv import load_dotenv

from exceptions import EndOfFileError

load_dotenv()

EXAMPLE_GPS_DATA_FILE_NAME = getenv("EXAMPLE_GPS_DATA_FILE_NAME")
if not EXAMPLE_GPS_DATA_FILE_NAME:
    raise ValueError(f"Environment variable EXAMPLE_GPS_DATA_FILE_NAME must be provided when using file_receiver.")

line_num = 0

def get_location() -> str:
    global line_num

    sleep(3)

    with open(EXAMPLE_GPS_DATA_FILE_NAME, "r") as file:
        try:
            line = file.readlines()[line_num].strip()
        except IndexError as e:
            raise EndOfFileError(file_name=EXAMPLE_GPS_DATA_FILE_NAME, line_number=line_num) from e

        line_num += 1
        return line
