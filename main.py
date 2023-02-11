import logging
import shutil
from os import getenv
from dotenv import load_dotenv
import requests
import pygame
from json import loads as convert_string_json_to_dict
from pathlib import Path

from exceptions import FailedRequestError
from settings import LOG_LEVEL, ACCEPTABLE_LOG_LEVELS

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

def extract_current_location(raw_gps_string: str) -> dict[str, float]:
    raw_gps_data: dict = convert_string_json_to_dict(raw_gps_string.replace("'", "\""))

    logger.info("Raw GPS data successfully extracted from JSON.")

    return {
        "latitude": raw_gps_data["network"]["latitude"],
        "longitude": raw_gps_data["network"]["longitude"]
    }

def get_OSM_image_path_location(width: int | float, height: int | float, zoom: int | float) -> Path:
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
    file_path = Path(f"""Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{map_center},{zoom},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    map_image_response = requests.get(
        f"""https://maps.geoapify.com/v1/staticmap?style={OSM_MAP_STYLE}&width={width}&height={height}&center=lonlat:{map_center["longitude"]},{map_center["latitude"]}&zoom={zoom}&apiKey={GEOAPIFY_API_KEY}""",
        stream=True
    )

    if map_image_response.status_code == 200:
        with open(file_path, "wb") as file:
            shutil.copyfileobj(map_image_response.raw, file)
        logger.info("Map image background successfully downloaded.")
    else:
        raise FailedRequestError(response=map_image_response)

    return file_path

def GPS_to_Image(width: int | float, height: int | float, zoom: int | float, centre: tuple[int | float, int | float]):
    with open("lat_long.json", 'r') as f:
        info = convert_string_json_to_dict(f.read())

    points = [((centre[0]-x['longitude'])*(4**zoom)+width/2, height/2-((centre[1]-x['latitude']))*(4**zoom)) for x in info["drawing_points"]]

    surf = pygame.Surface((width, height))

    surf.fill((255, 255, 255))

    for (p1, p2) in zip(points, points[1:]):
        pygame.draw.line(surf, (0, 0, 0), p1, p2)

    pygame.image.save(surf, "temp.jpg")


def main():
    # print(get_OSM_image_path_location(600, 600, 17))

    GPS_to_Image(360, 180, 11, (-1.1873156, 52.9532518))


if __name__ == "__main__":
    main()
