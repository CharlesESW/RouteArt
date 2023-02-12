import logging
import os.path
import shutil
import sys
from json import load as load_json_file, loads as convert_json_string_to_dict
from os import getenv
from pathlib import Path

import pygame
import requests
from dotenv import load_dotenv

from Frontend.frontend import Button, Image, getFile
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

logging.basicConfig()
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

def get_desired_background_map_image(width: int | float, height: int | float, zoom: int | float, latlon: dict[str, float] = None) -> Path:
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
    if not latlon:
        map_center = extract_current_location(raw_gps_string=get_raw_location_data())
    else:
        map_center = latlon

    file_path = Path(f"""Desired_Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{map_center},{zoom},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    logger.debug(f"{OSM_MAP_STYLE},{width},{height},{map_center},{zoom},{GEOAPIFY_API_KEY}")
    if not os.path.isfile(file_path):
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
    else:
        logger.debug("cached image already exists")

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
    file_path = Path(f"""Walking_Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{original_center},{zoom},{current_location},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    if not os.path.isfile(file_path):
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
    screen = pygame.display.set_mode((1200, 825))

    big_logo = Image("Frontend\\Logo.png", pos=(100, 100))  # TODO: change position, width & height relative to screen size
    mini_logo = Image("Frontend\\Logo.png", pos=(50, 50))  # TODO: change position, width & height relative to screen size
    desired_map_image = Image(pos=(150, 150))  # TODO: change position relative to screen size
    course_zoom_in_button = Button("+", (700, 500), (50, 50))
    course_zoom_out_button = Button("-", (700, 560), (50, 50))
    fine_zoom_in_button = Button("+", (770, 500), (50, 50))
    fine_zoom_out_button = Button("-", (770, 560), (50, 50))
    get_new_desired_map_center_button = Button("Center map to current location", (600, 700), (50, 50))  # TODO: change position, width & height relative to screen size
    confirm_desired_map_center_button = Button("Confirm map center", (600, 760), (50, 50))  # TODO: change position, width & height relative to screen size
    import_drawing_button = Button("Import drawing", (600, 412), (50, 50))  # TODO: change position, width & height relative to screen size
    drawing = Image()
    location_marker_map_image = Image(pos=(600, 412))

    state = "import_drawing"
    desired_map_zoom = 4
    desired_map_cache_still_deciding_center = {}

    while True:
        mousedown = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mousedown = True

        screen.fill((255, 255, 255))

        if state == "import_drawing":
            big_logo.draw(screen)
            import_drawing_button.draw(screen)

            if import_drawing_button.click(mousedown):
                drawing_file_path = getFile()
                logger.debug(drawing_file_path)

                if drawing_file_path:
                    drawing.reloadImage(drawing_file_path)
                    logger.debug("file found")

                    desired_map_cache_still_deciding_center = extract_current_location(raw_gps_string=get_raw_location_data())

                    desired_map_image.reloadImage(get_desired_background_map_image(400, 400, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size

                    logger.debug("changing state to get_desired_map")
                    state = "get_desired_map"

        elif state == "get_desired_map":
            mini_logo.draw(screen)
            desired_map_image.draw(screen)
            course_zoom_in_button.draw(screen)
            course_zoom_out_button.draw(screen)
            fine_zoom_out_button.draw(screen)
            fine_zoom_in_button.draw(screen)
            get_new_desired_map_center_button.draw(screen)
            confirm_desired_map_center_button.draw(screen)

            if course_zoom_in_button.click(mousedown):
                if desired_map_zoom + 1 <= 20:
                    logger.debug("course zoom in")
                    desired_map_zoom += 1

                    desired_map_image.reloadImage(get_desired_background_map_image(400, 400, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif course_zoom_out_button.click(mousedown):
                if desired_map_zoom - 1 >= 1:
                    logger.debug("course zoom out")
                    desired_map_zoom -= 1

                    desired_map_image.reloadImage(get_desired_background_map_image(400, 400, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif fine_zoom_in_button.click(mousedown):
                if desired_map_zoom + 0.1 <= 20:
                    logger.debug("fine zoom in")
                    desired_map_zoom += 0.1

                    desired_map_image.reloadImage(get_desired_background_map_image(400, 400, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif fine_zoom_out_button.click(mousedown):
                if desired_map_zoom - 0.1 >= 1:
                    logger.debug("fine zoom out")
                    desired_map_zoom -= 0.1

                    desired_map_image.reloadImage(get_desired_background_map_image(400, 400, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif get_new_desired_map_center_button.click(mousedown):
                logger.debug("update center")

                desired_map_cache_still_deciding_center = extract_current_location(raw_gps_string=get_raw_location_data())
                desired_map_image.reloadImage(get_desired_background_map_image(400, 400, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif confirm_desired_map_center_button.click(mousedown):
                logger.debug("changing state to pre_walk")
                state = "pre_walk"

        # elif state == "pre_walk":
        #     mini_logo.draw(screen)
        #     if desired_map_image.pos != (600, 412):  # TODO: change position relative to screen size
        #         desired_map_image.pos = (600, 412)  # TODO: change position relative to screen size
        #     desired_map_image.draw(screen)
        #     drawing



        pygame.display.flip()


if __name__ == "__main__":
    main()
