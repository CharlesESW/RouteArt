import logging
import os.path
import shutil
import sys
from json import load as load_json_file, loads as convert_json_string_to_dict, dump as dump_to_json
from os import getenv
from pathlib import Path

import math
import pygame
import requests
from dotenv import load_dotenv

from Frontend.frontend import Button, Image, TextBox, getFile
from exceptions import FailedRequestError
from settings import ACCEPTABLE_LOG_LEVELS, LOG_LEVEL
from Image_Comparisons.Image_Comparer import image_similarity

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

    logger.debug("Raw GPS data successfully extracted from JSON.")

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
        logger.info("Cached image already exists")

    return file_path

def get_walking_background_map_image(width: int | float, height: int | float, zoom: int | float, marker_latlon: dict[str, float] = None) -> Path:
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
        desired_map_original_center: dict[str, float] = load_json_file(file)["desired_map_original_center"]
    if not marker_latlon:
        current_location = extract_current_location(raw_gps_string=get_raw_location_data())
    else:
        current_location = marker_latlon

    file_path = Path(f"""Walking_Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{desired_map_original_center},{zoom},{current_location},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    if not os.path.isfile(file_path):
        map_image_response = requests.get(
            f"""https://maps.geoapify.com/v1/staticmap?style={OSM_MAP_STYLE}&width={width}&height={height}&center=lonlat:{desired_map_original_center["longitude"]},{desired_map_original_center["latitude"]}&zoom={zoom}&marker=lonlat:{current_location["longitude"]},{current_location["latitude"]};type:awesome;color:red;icon:user;iconsize:large;whitecircle:no&apiKey={GEOAPIFY_API_KEY}""",
            stream=True
        )

        if map_image_response.status_code == 200:
            with open(file_path, "wb") as file:
                shutil.copyfileobj(map_image_response.raw, file)
            logger.info("Walking map image background successfully downloaded.")
        else:
            raise FailedRequestError(response=map_image_response)

    return file_path

def get_walking_drawing_image_path(width: int | float, height: int | float, zoom: int | float, thickness: int = 3) -> Path:
    with open("lat_long.json", 'r') as f:
        info = convert_json_string_to_dict(f.read())

    center = info["desired_map_original_center"]

    surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)

    surf.fill((255, 255, 255, 0))

    X_CONST = 6_378_137
    Y_CONST = 111139

    points = []
    for point in info['drawing_points']:
        longitude = point['longitude']
        latitude = point['latitude']
        dif_x = longitude - center['longitude']  # Find x_dif to center point
        dif_y = latitude - center['latitude']  # Find y_dif to center point

        dif_x_m = dif_x * X_CONST * math.pi / 180 * math.cos(latitude * math.pi / 180)
        dif_y_m = dif_y * Y_CONST

        OSM_pixel = math.pi * 6_378_137 * math.cos(math.radians(latitude)) / (2**(zoom+8))

        x = dif_x_m / OSM_pixel
        y = dif_y_m / OSM_pixel

        x = int(x) + width/2
        y = height/2 - int(y)

        points.append((x, y))

    for (p1, p2) in zip(points, points[1:]):
        pygame.draw.line(surf, (0, 0, 0), p1, p2, thickness)

    file_name = str(abs(hash(f"{width},{height},{center},{zoom},{info['drawing_points']}")))
    pygame.image.save(surf, f"Route_GPS_Drawings\\{file_name}.png")

    return Path(f"Route_GPS_Drawings\\{file_name}.png")


def main():
    screen = pygame.display.set_mode((1200, 825), pygame.RESIZABLE)  # TODO: make screen size variable

    big_logo = Image("Frontend\\Logo.png", pos=(600, 320), size=0.6)  # TODO: change position, width & height relative to screen size
    title = TextBox("RouteArt", pos=(600, 665), font_size=80)
    import_drawing_button = Button("Import drawing", pos=(600, 730))  # TODO: change position, width & height relative to screen size
    mini_logo = Image("Frontend\\Logo.png", pos=(105, 105), size=0.18)  # TODO: change position, width & height relative to screen size
    desired_map_image = Image(pos=(600, 330))  # TODO: change position relative to screen size
    course_zoom_in_button = Button("+", pos=(620, 760))
    course_zoom_out_button = Button("-", pos=(650, 760))
    course_zoom_label = TextBox("Course zoom", pos=(640, 700))
    fine_zoom_in_button = Button("+", pos=(780, 760))
    fine_zoom_out_button = Button("-", pos=(810, 760))
    fine_zoom_label = TextBox("Fine zoom", pos=(790, 700))
    get_new_desired_map_center_button = Button("Center map to current location", pos=(400, 700))  # TODO: change position, width & height relative to screen size
    confirm_desired_map_center_button = Button("Confirm map center", pos=(400, 760))  # TODO: change position, width & height relative to screen size
    drawing = Image()
    walk_to_start_title = TextBox("Walk to any point on your drawing to start your journey\nOnly press the button below when you are on your drawing!", font_size=28, pos=(600, 700))  # TODO: change position, width & height relative to screen size
    location_marker_map_image = Image(pos=(900, 460))  # TODO: change position, width & height relative to screen size
    start_walking_button = Button("I am ready to start my route", pos=(600, 780))  # TODO: change position, width & height relative to screen size
    walking_drawing_image = Image(pos=(900, 460))  # TODO: change position, width & height relative to screen size
    add_new_walking_point_button = Button("Add new route drawing point", pos=(600, 755))  # TODO: change position, width & height relative to screen size
    finish_walking_button = Button("Finish route", pos=(600, 790))
    comparison_percentage = TextBox("", font_size=28, pos=(600, 720))

    state = "import_drawing"
    desired_map_zoom = 4
    desired_map_cache_still_deciding_center = {}

    with open(Path("lat_long.json"), "r") as file:
        lat_longJSON: dict[str, dict[str, float] | list[dict[str, float]]] = load_json_file(file)

    lat_longJSON["drawing_points"] = []
    lat_longJSON["desired_map_original_center"] = {}

    with open(Path("lat_long.json"), "w") as file:
        dump_to_json(lat_longJSON, file)

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
            title.draw(screen)
            import_drawing_button.draw(screen)

            if import_drawing_button.click(mousedown):
                drawing_file_path = getFile()
                logger.debug(drawing_file_path or "No file chosen")

                if drawing_file_path:
                    drawing.reloadImage(drawing_file_path)
                    logger.debug("file found")

                    drawing.fitToRect((760, 630))

                    drawing_width, drawing_height = drawing.img.get_size()

                    raw = get_raw_location_data()
                    logger.debug(raw)
                    desired_map_cache_still_deciding_center = extract_current_location(raw_gps_string=raw)

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size

                    drawing.pos = (600, 330)  # TODO: change position relative to screen size
                    drawing.alpha = 0.25

                    logger.debug("changing state to get_desired_map")
                    state = "get_desired_map"

        elif state == "get_desired_map":
            desired_map_image.draw(screen)
            drawing.draw(screen)
            mini_logo.draw(screen)
            course_zoom_in_button.draw(screen)
            course_zoom_out_button.draw(screen)
            course_zoom_label.draw(screen)
            fine_zoom_out_button.draw(screen)
            fine_zoom_in_button.draw(screen)
            fine_zoom_label.draw(screen)
            get_new_desired_map_center_button.draw(screen)
            confirm_desired_map_center_button.draw(screen)

            if course_zoom_in_button.click(mousedown):
                if desired_map_zoom + 1 <= 20:
                    logger.debug("course zoom in")
                    desired_map_zoom += 1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif course_zoom_out_button.click(mousedown):
                if desired_map_zoom - 1 >= 1:
                    logger.debug("course zoom out")
                    desired_map_zoom -= 1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif fine_zoom_in_button.click(mousedown):
                if desired_map_zoom + 0.1 <= 20:
                    logger.debug("fine zoom in")
                    desired_map_zoom += 0.1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif fine_zoom_out_button.click(mousedown):
                if desired_map_zoom - 0.1 >= 1:
                    logger.debug("fine zoom out")
                    desired_map_zoom -= 0.1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif get_new_desired_map_center_button.click(mousedown):
                logger.debug("update center")

                drawing_width, drawing_height = drawing.img.get_size()

                raw = get_raw_location_data()
                logger.debug(raw)
                desired_map_cache_still_deciding_center = extract_current_location(raw_gps_string=raw)
                desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_center))  # TODO: change width & height relative to screen size
            elif confirm_desired_map_center_button.click(mousedown):
                with open(Path("lat_long.json"), "r") as file:
                    lat_longJSON: dict[str, dict[str, float] | list[dict[str, float]]] = load_json_file(file)

                lat_longJSON["desired_map_original_center"] = desired_map_cache_still_deciding_center

                with open(Path("lat_long.json"), "w") as file:
                    dump_to_json(lat_longJSON, file)

                logger.debug("changing state to pre_walk")
                state = "pre_walk"

        elif state == "pre_walk":
            mini_logo.draw(screen)
            desired_map_image.draw(screen)
            drawing.draw(screen)
            start_walking_button.draw(screen)
            walk_to_start_title.draw(screen)

            if start_walking_button.click(mousedown):
                desired_map_image.pos = (290, 460)  # TODO: change position relative to screen size
                drawing.pos = (290, 460)  # TODO: change position relative to screen size
                drawing.alpha = 0.25

                raw = get_raw_location_data()
                logger.debug(raw)
                current_location = extract_current_location(raw)

                with open(Path("lat_long.json"), "r") as file:
                    lat_longJSON: dict[str, dict[str, float] | list[dict[str, float]]] = load_json_file(file)

                lat_longJSON["drawing_points"].append(current_location)

                with open(Path("lat_long.json"), "w") as file:
                    dump_to_json(lat_longJSON, file)

                drawing_width, drawing_height = drawing.img.get_size()

                location_marker_map_image.reloadImage(get_walking_background_map_image(drawing_width, drawing_height, desired_map_zoom, current_location))
                walking_drawing_image.reloadImage(get_walking_drawing_image_path(drawing_width, drawing_height, desired_map_zoom))

                logger.debug("changing state to walking")
                state = "walking"

        elif state == "walking":
            mini_logo.draw(screen)
            desired_map_image.draw(screen)
            drawing.draw(screen)
            location_marker_map_image.draw(screen)
            walking_drawing_image.draw(screen)
            add_new_walking_point_button.draw(screen)
            finish_walking_button.draw(screen)

            if add_new_walking_point_button.click(mousedown):
                raw = get_raw_location_data()
                logger.debug(raw)
                current_location = extract_current_location(raw)

                with open(Path("lat_long.json"), "r") as file:
                    lat_longJSON: dict[str, dict[str, float] | list[dict[str, float]]] = load_json_file(file)

                lat_longJSON["drawing_points"].append(current_location)

                with open(Path("lat_long.json"), "w") as file:
                    dump_to_json(lat_longJSON, file)

                drawing_width, drawing_height = drawing.img.get_size()

                location_marker_map_image.reloadImage(get_walking_background_map_image(drawing_width, drawing_height, desired_map_zoom, current_location))
                walking_drawing_image.reloadImage(get_walking_drawing_image_path(drawing_width, drawing_height, desired_map_zoom))

            elif finish_walking_button.click(mousedown):
                drawing.pos = (600, 330)  # TODO: change position relative to screen size
                drawing.alpha = 1
                walking_drawing_image.pos = (600, 330)  # TODO: change position relative to screen size
                comparison_percentage.text = f"Your route was {image_similarity(walking_drawing_image.path, drawing.path)} similar to the uploaded drawing!"

                logger.debug("changing state to image_comparison")
                state = "image_comparison"

        elif state == "image_comparison":
            mini_logo.draw(screen)
            drawing.draw(screen)
            walking_drawing_image.draw(screen)
            comparison_percentage.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
