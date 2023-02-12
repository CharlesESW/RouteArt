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

from Frontend.frontend import Button, Image, TextBox, Paragraph, Screen, getFile
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
        map_centre = extract_current_location(raw_gps_string=get_raw_location_data())
    else:
        map_centre = latlon

    file_path = Path(f"""Desired_Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{map_centre},{zoom},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    logger.debug(f"{OSM_MAP_STYLE},{width},{height},{map_centre},{zoom},{GEOAPIFY_API_KEY}")
    if not os.path.isfile(file_path):
        map_image_response = requests.get(
            f"""https://maps.geoapify.com/v1/staticmap?style={OSM_MAP_STYLE}&width={width}&height={height}&center=lonlat:{map_centre["longitude"]},{map_centre["latitude"]}&zoom={zoom}&apiKey={GEOAPIFY_API_KEY}""",
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
        desired_map_original_centre: dict[str, float] = load_json_file(file)["desired_map_original_centre"]
    if not marker_latlon:
        current_location = extract_current_location(raw_gps_string=get_raw_location_data())
    else:
        current_location = marker_latlon

    file_path = Path(f"""Walking_Background_Map_Images/{(str(abs(hash(f"{OSM_MAP_STYLE},{width},{height},{desired_map_original_centre},{zoom},{current_location},{GEOAPIFY_API_KEY}"))) + MAP_IMAGE_FILE_EXTENSION)}""")
    if not os.path.isfile(file_path):
        # noinspection SpellCheckingInspection
        map_image_response = requests.get(
            f"""https://maps.geoapify.com/v1/staticmap?style={OSM_MAP_STYLE}&width={width}&height={height}&center=lonlat:{desired_map_original_centre["longitude"]},{desired_map_original_centre["latitude"]}&zoom={zoom}&marker=lonlat:{current_location["longitude"]},{current_location["latitude"]};type:awesome;color:red;icon:user;iconsize:large;whitecircle:no&apiKey={GEOAPIFY_API_KEY}""",
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

    centre = info["desired_map_original_centre"]

    surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)

    surf.fill((255, 255, 255, 0))

    X_CONST = 6_378_137
    Y_CONST = 111139

    points = []
    for point in info['drawing_points']:
        longitude = point['longitude']
        latitude = point['latitude']
        dif_x = longitude - centre['longitude']  # Find x_dif to centre point
        dif_y = latitude - centre['latitude']  # Find y_dif to centre point

        dif_x_m = dif_x * X_CONST * math.pi / 180 * math.cos(latitude * math.pi / 180)
        dif_y_m = dif_y * Y_CONST

        OSM_pixel = math.pi * 6_378_137 * math.cos(math.radians(latitude)) / (2 ** (zoom + 8))

        x = dif_x_m / OSM_pixel
        y = dif_y_m / OSM_pixel

        x = int(x) + width / 2
        y = height / 2 - int(y)

        points.append((x, y))

    for (p1, p2) in zip(points, points[1:]):
        pygame.draw.line(surf, (0, 0, 0), p1, p2, thickness)

    file_name = str(abs(hash(f"{width},{height},{centre},{zoom},{info['drawing_points']}")))
    pygame.image.save(surf, f"Route_GPS_Drawings\\{file_name}.png")

    return Path(f"Route_GPS_Drawings\\{file_name}.png")


def main():
    WINDOW = Screen(1200, 800)
    screen = pygame.display.set_mode(WINDOW.size, pygame.RESIZABLE)

    clock = pygame.time.Clock()

    big_logo = Image(WINDOW, "Frontend\\Logo.png", pos=(3, 2), size=0.6)
    title = TextBox(WINDOW, "RouteArt", pos=(3, 5), font_size=80)

    # Import photo to trace
    import_drawing_button = Button(WINDOW, "Import drawing", pos=(3, 6))
    mini_logo = Image(WINDOW, "Frontend\\Logo.png", pos=(0, 0), size=0.18)

    # Desired map (on left)
    desired_map_image = Image(WINDOW, pos=(3, 2))

    # Zoom in and out w/ Labels
    course_zoom_in_button = Button(WINDOW, "+", pos=(5, 5), size=(20, 20), auto_size=False)
    course_zoom_out_button = Button(WINDOW, "-", pos=(5, 6), size=(20, 20), auto_size=False)
    course_zoom_label = TextBox(WINDOW, "Course zoom", pos=(5, 4))
    fine_zoom_in_button = Button(WINDOW, "+", pos=(6, 5), size=(20, 20), auto_size=False)
    fine_zoom_out_button = Button(WINDOW, "-", pos=(6, 6), size=(20, 20), auto_size=False)
    fine_zoom_label = TextBox(WINDOW, "Fine zoom", pos=(6, 4))

    get_new_desired_map_centre_button = Button(WINDOW, "Centre map to current location", pos=(1, 5))
    confirm_desired_map_centre_button = Button(WINDOW, "Confirm map centre", pos=(1, 6))
    drawing = Image(WINDOW)
    walk_to_start_title = Paragraph(WINDOW, "Walk to any point on your drawing to start your journey\nOnly press the button below when you are on your drawing!", font_size=28, pos=(3, 4))

    # Right hand map with pointers
    location_marker_map_image = Image(WINDOW, pos=(5, 3))
    start_walking_button = Button(WINDOW, "I am ready to start my route", pos=(3, 6))

    # Right hand walk overlay
    walking_drawing_image = Image(WINDOW, pos=(5, 3))

    add_new_walking_point_button = Button(WINDOW, "Add new route drawing point", pos=(3, 6))
    finish_walking_button = Button(WINDOW, "Finish route", pos=(3, 7))
    comparison_percentage = TextBox(WINDOW, "", font_size=28, pos=(3, 6))

    state = "import_drawing"
    desired_map_zoom = 4
    desired_map_cache_still_deciding_centre = {}

    with open(Path("lat_long.json"), "r") as file:
        lat_longJSON: dict[str, dict[str, float] | list[dict[str, float]]] = load_json_file(file)

    lat_longJSON["drawing_points"] = []
    lat_longJSON["desired_map_original_centre"] = {}

    with open(Path("lat_long.json"), "w") as file:
        dump_to_json(lat_longJSON, file)

    while True:
        clock.tick(60)
        mousedown = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mousedown = True

            if event.type == pygame.VIDEORESIZE:
                WINDOW.size = (event.w, event.h)

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
                    desired_map_cache_still_deciding_centre = extract_current_location(raw_gps_string=raw)

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_centre))

                    drawing.pos = (3, 2)
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
            get_new_desired_map_centre_button.draw(screen)
            confirm_desired_map_centre_button.draw(screen)

            if course_zoom_in_button.click(mousedown):
                if desired_map_zoom + 1 <= 20:
                    logger.debug("course zoom in")
                    desired_map_zoom += 1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_centre))
            elif course_zoom_out_button.click(mousedown):
                if desired_map_zoom - 1 >= 1:
                    logger.debug("course zoom out")
                    desired_map_zoom -= 1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_centre))
            elif fine_zoom_in_button.click(mousedown):
                if desired_map_zoom + 0.1 <= 20:
                    logger.debug("fine zoom in")
                    desired_map_zoom += 0.1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_centre))
            elif fine_zoom_out_button.click(mousedown):
                if desired_map_zoom - 0.1 >= 1:
                    logger.debug("fine zoom out")
                    desired_map_zoom -= 0.1

                    drawing_width, drawing_height = drawing.img.get_size()

                    desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_centre))
            elif get_new_desired_map_centre_button.click(mousedown):
                logger.debug("Update desired map centre")

                drawing_width, drawing_height = drawing.img.get_size()

                raw = get_raw_location_data()
                logger.debug(raw)
                desired_map_cache_still_deciding_centre = extract_current_location(raw_gps_string=raw)
                desired_map_image.reloadImage(get_desired_background_map_image(drawing_width, drawing_height, desired_map_zoom, desired_map_cache_still_deciding_centre))
            elif confirm_desired_map_centre_button.click(mousedown):
                with open(Path("lat_long.json"), "r") as file:
                    lat_longJSON: dict[str, dict[str, float] | list[dict[str, float]]] = load_json_file(file)

                lat_longJSON["desired_map_original_centre"] = desired_map_cache_still_deciding_centre

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
                desired_map_image.pos = (1, 3)
                drawing.pos = (1, 3)
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
                counter = 180

        elif state == "walking":
            mini_logo.draw(screen)
            desired_map_image.draw(screen)
            drawing.draw(screen)
            location_marker_map_image.draw(screen)
            walking_drawing_image.draw(screen)
            add_new_walking_point_button.draw(screen)
            finish_walking_button.draw(screen)

            if counter != 0:
                counter -= 1

            if finish_walking_button.click(mousedown) or counter == 0:
                counter = 180
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

            if finish_walking_button.click(mousedown):
                drawing.pos = (3, 3)
                drawing.alpha = 1
                walking_drawing_image.pos = (3, 3)
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
