import logging
import shutil
import sys
from json import load as load_json_file, loads as convert_json_string_to_dict
from os import getenv
from pathlib import Path

import pygame
import requests
from dotenv import load_dotenv

from exceptions import FailedRequestError
from settings import ACCEPTABLE_LOG_LEVELS, LOG_LEVEL

load_dotenv()

# noinspection SpellCheckingInspection
_ALLOWED_OSM_MAP_STYLES = ("osm-carto", "osm-bright", "osm-bright-grey", "osm-bright-smooth", "klokantech-basic", "osm-liberty", "maptiler-3d", "toner", "toner-grey", "positron")
OSM_MAP_STYLE = getenv("OSM_MAP_STYLE", "osm-carto")
if OSM_MAP_STYLE not in _ALLOWED_OSM_MAP_STYLES:
    raise ValueError(f"Environment variable OSM_MAP_STYLE must be one of {repr(_ALLOWED_OSM_MAP_STYLES)}")

_ALLOWED_MAP_IMAGE_FILE_EXTENSIONS = (".jpg", ".png", ".bmp", ".jpeg")
MAP_IMAGE_FILE_EXTENSION = getenv("MAP_IMAGE_FILE_EXTENSION", ".jpg").lower()
if MAP_IMAGE_FILE_EXTENSION not in _ALLOWED_MAP_IMAGE_FILE_EXTENSIONS:
    raise ValueError(f"Environment variable MAP_IMAGE_FILE_EXTENSION must be one of {repr(_ALLOWED_MAP_IMAGE_FILE_EXTENSIONS)}")

# noinspection SpellCheckingInspection
GEOAPIFY_API_KEY = getenv("GEOAPIFY_API_KEY")
if not GEOAPIFY_API_KEY:
    # noinspection SpellCheckingInspection
    raise ValueError(f"Environment variable GEOAPIFY_API_KEY must be provided.")

_ALLOWED_RECEIVER_FUNCS = ("file", "socket")
RECEIVER_FUNC = getenv("RECEIVER_FUNC", "file")
if RECEIVER_FUNC not in _ALLOWED_RECEIVER_FUNCS:
    raise ValueError(f"Environment variable RECEIVER_FUNC must be one of {repr(_ALLOWED_RECEIVER_FUNCS)}")

if RECEIVER_FUNC == _ALLOWED_RECEIVER_FUNCS[0]:
    from GPS_Data_Receivers.file_receiver import get_raw_location_data
elif RECEIVER_FUNC == _ALLOWED_RECEIVER_FUNCS[1]:
    from GPS_Data_Receivers.socket_receiver import get_raw_location_data

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

pygame.init()
pygame.display.set_caption("RouteArt")
pygame.display.set_icon(pygame.image.load("Frontend\\Window_Icon.png"))

def extract_current_location(raw_gps_string: str) -> dict[str, float]:
    raw_gps_data: dict = convert_json_string_to_dict(raw_gps_string.replace("'", "\""))

    logger.info("Raw GPS data successfully extracted from JSON.")

    return {
        "latitude": raw_gps_data["network"]["latitude"],
        "longitude": raw_gps_data["network"]["longitude"]
    }

def get_desired_background_map_image(width: int | float, height: int | float, zoom: int | float) -> Path:
    if isinstance(width, (int, float)):
        if not 50 < width <= 10000:
            raise ValueError("Parameter width must be between 50 & 10000.")
    else:
        raise TypeError("Parameter width must be an integer or a float.")

    if isinstance(height, (int, float)):
        if not 50 < height <= 10000:
            raise ValueError("Parameter height must be between 50 & 10000.")
    else:
        raise TypeError("Parameter height must be an integer or a float.")

    if isinstance(zoom, (int, float)):
        if not 1 <= zoom <= 20:
            raise ValueError("Parameter zoom must be between 1 & 20.")
    else:
        raise TypeError("Parameter zoom must be an integer or a float.")

    map_center = extract_current_location(raw_gps_string=get_raw_location_data())
    file_path = Path(f"""Desired_Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{map_center},{zoom},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    map_image_response = requests.get(
        f"""https://maps.geoapify.com/v1/staticmap?style={OSM_MAP_STYLE}&width={width}&height={height}&center=lonlat:{map_center["longitude"]},{map_center["latitude"]}&zoom={zoom}&apiKey={GEOAPIFY_API_KEY}""",
        stream=True
    )

    if map_image_response.status_code == 200:
        with open(file_path, "wb") as file:
            shutil.copyfileobj(map_image_response.raw, file)
        logger.info("Desired map image background successfully downloaded.")
    else:
        raise FailedRequestError(response=map_image_response)

    return file_path

def get_walking_background_map_image(width: int | float, height: int | float, zoom: int | float) -> Path:
    if isinstance(width, (int, float)):
        if not 50 < width <= 10000:
            raise ValueError("Parameter width must be between 50 & 10000.")
    else:
        raise TypeError("Parameter width must be an integer or a float.")

    if isinstance(height, (int, float)):
        if not 50 < height <= 10000:
            raise ValueError("Parameter height must be between 50 & 10000.")
    else:
        raise TypeError("Parameter height must be an integer or a float.")

    if isinstance(zoom, (int, float)):
        if not 1 <= zoom <= 20:
            raise ValueError("Parameter zoom must be between 1 & 20.")
    else:
        raise TypeError("Parameter zoom must be an integer or a float.")

    with open(Path("lat_long.json"), "r") as file:
        original_center: dict[str, float] = load_json_file(file)["original_center"]

    current_location = extract_current_location(raw_gps_string=get_raw_location_data())
    file_path = Path(f"""Walking_Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{original_center},{zoom},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    map_image_response = requests.get(
        f"""https://maps.geoapify.com/v1/staticmap?style={OSM_MAP_STYLE}&width={width}&height={height}&center=lonlat:{original_center["longitude"]},{original_center["latitude"]}&zoom={zoom}&marker=lonlat:{current_location["longitude"]},{current_location["latitude"]};type:awesome;color:red;icon:user;iconsize:large;whitecircle:no&apiKey={GEOAPIFY_API_KEY}""",
        stream=True
    )

    if map_image_response.status_code == 200:
        with open(file_path, "wb") as file:
            shutil.copyfileobj(map_image_response.raw, file)
        logger.info("Walking map image background successfully downloaded.")
    else:
        raise FailedRequestError(response=map_image_response)

    return file_path


def main():
    screen = pygame.display.set_mode((400, 400))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 255))

        pygame.display.flip()

if __name__ == "__main__":
    main()
