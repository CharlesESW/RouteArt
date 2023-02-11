import logging
from os import getenv
from pathlib import Path
from time import sleep

from dotenv import load_dotenv

from exceptions import EndOfFileError
from settings import LOG_LEVEL, ACCEPTABLE_LOG_LEVELS

load_dotenv()

_EXAMPLE_GPS_DATA_FILE_NAME = getenv("EXAMPLE_GPS_DATA_FILE_NAME")
if not _EXAMPLE_GPS_DATA_FILE_NAME:
    raise ValueError(f"Environment variable EXAMPLE_GPS_DATA_FILE_NAME must be provided when using file_receiver.")
EXAMPLE_GPS_DATA_FILE_PATH = Path(_EXAMPLE_GPS_DATA_FILE_NAME)

PRETEND_SOCKET_WAIT_TIME = float(getenv("PRETEND_SOCKET_WAIT_TIME", "3"))
if not 0.1 <= PRETEND_SOCKET_WAIT_TIME <= 1000:
    raise ValueError(f"Environment variable PRETEND_SOCKET_WAIT_TIME must be between 0.1 & 1000.")

logger = logging.getLogger(__name__)
if LOG_LEVEL == ACCEPTABLE_LOG_LEVELS[0]:
    logger.setLevel(logging.DEBUG)
elif LOG_LEVEL == ACCEPTABLE_LOG_LEVELS[1]:
    logger.setLevel(logging.INFO)
elif LOG_LEVEL == ACCEPTABLE_LOG_LEVELS[2]:
    logger.setLevel(logging.WARNING)
elif LOG_LEVEL == ACCEPTABLE_LOG_LEVELS[3]:
    logger.setLevel(logging.ERROR)
elif LOG_LEVEL == ACCEPTABLE_LOG_LEVELS[4]:
    logger.setLevel(logging.CRITICAL)

line_num = 0

def get_raw_location_data() -> str:
    global line_num

    logger.info("Started retrieving next example gps data from file.")
    logger.debug(f"Sleeping program for {PRETEND_SOCKET_WAIT_TIME} seconds to pretend to be operate in a similar way to socket receiver.")

    sleep(PRETEND_SOCKET_WAIT_TIME)

    with open(EXAMPLE_GPS_DATA_FILE_PATH, "r") as file:
        try:
            line = file.readlines()[line_num].strip()
        except IndexError as e:
            raise EndOfFileError(file_path=EXAMPLE_GPS_DATA_FILE_PATH, line_number=line_num) from e

        line_num += 1

        logger.debug("Successfully retrieved next example gps data line.")
        return line
