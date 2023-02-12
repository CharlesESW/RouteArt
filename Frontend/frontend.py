# Code to start program
from pathlib import Path

import pygame
import tkinter as tk
from tkinter import filedialog

from exceptions import EmptyImageFilePath

pygame.font.init()

root = tk.Tk()
root.withdraw()


class Screen:
    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height

        self.x = [
            self._width / 6,  # Big left of centre
            self._width / 4,  # Medium left of centre
            self._width / 3,  # Small left of centre
            self._width / 2,  # Middle of screen
            2 * self._width / 3,  # Small right of centre
            3 * self._width / 4,  # Medium right of centre
            5 * self._width / 6,  # Big right of centre
        ]

        self.y = [
            self._height / 6,  # Big above centre
            self._height / 4,  # Medium above centre
            self._height / 3,  # Small above centre
            self._height / 2,  # Middle of screen
            2 * self._height / 3,  # Small below centre
            3 * self._height / 4,  # Medium below centre
            5 * self._height / 6,  # Big below centre
            8 * self._height / 9,  # Massive below centre
        ]

        self.x = [int(pos) for pos in self.x]
        self.y = [int(pos) for pos in self.y]

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, val: int) -> None:
        old_width = self._width
        self._width = val

        scale_factor = self._width / old_width

        self.x = [int(x * scale_factor) for x in self.x]

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, val: int) -> None:
        old_height = self._height
        self._height = val

        scale_factor = self._height / old_height
        self.y = [int(y * scale_factor) for y in self.y]

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    @size.setter
    def size(self, val: tuple[int, int]) -> None:
        old_width = self._width
        old_height = self._height

        self._width, self._height = val

        x_scale_factor = self._width / old_width
        y_scale_factor = self._height / old_height

        self.x = [int(x * x_scale_factor) for x in self.x]
        self.y = [int(y * y_scale_factor) for y in self.y]


# Image class
class Image:
    # Load image
    def __init__(
            self, window: Screen, path: str | Path | None = None, pos: tuple[int, int] = (0, 0), size: tuple[int, int] | float | None = None,
            centre_flag: bool = True, alpha: float = 1
    ) -> None:

        if path is not None:
            self.img = pygame.image.load(path)
            self.img.set_alpha(int(alpha * 255))

        self.path = path

        self.c_flag = centre_flag

        self._alpha = alpha
        self._pos = pos

        self.WINDOW = window

        if size is not None:
            if isinstance(size, tuple):
                self.img = pygame.transform.scale(self.img, size)
            else:
                self.img = pygame.transform.scale(self.img, [*map(lambda x: int(x * size), self.img.get_rect().size)])

    # Display image to screen
    def draw(self, display: pygame.surface.Surface) -> None:
        if self.path is not None:
            if self.c_flag:
                x, y = self.WINDOW.x[self.pos[0]], self.WINDOW.y[self.pos[1]]
                wid, height = self.img.get_rect().size
                display.blit(self.img, (x - wid / 2, y - height / 2))
            else:
                display.blit(self.img, (self.WINDOW.x[self.pos[0]], self.WINDOW.y[self.pos[1]]))
        else:
            raise EmptyImageFilePath("Image cannot be drawn to screen, because it has no valid file path. (You did a little fucky wucky silly billy boo bah).")

    # Reload image
    def reloadImage(self, path: str | Path):
        self.img = pygame.image.load(path)
        self.img.set_alpha(int(self._alpha * 255))

        self.path = path

    def resizeImage(self, size: tuple[int, int] | float) -> None:
        self.img = pygame.image.load(self.path)

        if isinstance(size, tuple):
            self.img = pygame.transform.scale(self.img, size)
        else:
            self.img = pygame.transform.scale(self.img, [*map(lambda x: int(x * size), self.img.get_rect().size)])

    def fitToRect(self, rect: tuple[int, int]) -> None:
        wid, height = self.img.get_size()

        if wid < rect[0] and height < rect[1]:
            x_ratio = rect[0] / wid
            y_ratio = rect[1] / height

            if x_ratio < y_ratio:
                ratio = rect[0] / wid
                new_height = int(height * ratio)
                self.resizeImage((rect[0], new_height))
            else:
                ratio = rect[1] / height
                new_wid = int(wid * ratio)
                self.resizeImage((new_wid, rect[1]))

        elif wid > rect[0] and height < rect[1]:
            ratio = wid / rect[0]
            new_height = int(height / ratio)
            self.resizeImage((rect[0], new_height))

        elif height > rect[1] and wid < rect[0]:
            ratio = height / rect[1]
            new_wid = int(wid / ratio)
            self.resizeImage((new_wid, rect[1]))
        else:
            x_ratio = wid / rect[0]
            y_ratio = height / rect[1]

            if x_ratio > y_ratio:
                ratio = wid / rect[0]
                new_height = int(height / ratio)
                self.resizeImage((rect[0], new_height))
            else:
                ratio = height / rect[1]
                new_wid = int(wid / ratio)
                self.resizeImage((new_wid, rect[1]))

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, val: float) -> None:
        self._alpha = val
        self.img.set_alpha(int(self._alpha * 255))

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, val: tuple[int, int]) -> None:
        self._pos = val


# Button Class
class Button:
    def __init__(
            self, window: Screen, text: str, pos: tuple[int, int], size: tuple[int, int] | None = None, centre_flag: bool = True,
            border: int = 2, border_curve: bool = True, auto_size: bool = True, font_family: str = "Helvetica", font_size: int = 20
    ) -> None:
        self._text = text
        self._pos = pos
        self.dimensions = size

        self.c_flag = centre_flag
        self.border = border
        self.border_curve = border_curve
        self.auto_size = auto_size
        self.bg_colour = (255, 255, 255)

        self.WINDOW = window

        self.font = pygame.font.SysFont(font_family, font_size)

        # Render text
        self.rendText = self.font.render(self._text, True, (0, 0, 0))

        if self.dimensions is None and not self.auto_size:
            raise ValueError("Parameter size cannot be None while parameter auto_size is False. (Fuck you Matt you caused this stupid fucking error to occur this would not have to exist if you didn't want to do the silly billy math just put in some fucking dimensions it's just trial and error you fuck).")

        if self.auto_size:
            self.dimensions = [*map(lambda x: x + 8, self.rendText.get_rect().size)]

    def draw(self, display: pygame.surface.Surface):
        if self.c_flag:
            x_pos, y_pos = self.WINDOW.x[self.pos[0]], self.WINDOW.y[self.pos[1]]
            width, height = self.dimensions
            x_pos -= width / 2
            y_pos -= height / 2

        else:
            x_pos, y_pos = self.WINDOW.x[self.pos[0]], self.WINDOW.y[self.pos[1]]

        pygame.draw.rect(display, (0, 0, 0), (x_pos, y_pos, *self.dimensions), border_radius=2 * self.border_curve)
        pygame.draw.rect(display, self.bg_colour, (*map(lambda x: x + self.border, (x_pos, y_pos)), *map(lambda x: x - 2 * self.border, self.dimensions)), border_radius=2 * self.border_curve)

        current_text_dimensions = self.rendText.get_rect().size
        x_pos, y_pos = map(lambda x: x[0] + (x[1] - x[2]) / 2, zip((x_pos, y_pos), self.dimensions, current_text_dimensions))
        display.blit(self.rendText, (x_pos, y_pos))

    def hover(self, mouse_pos: tuple[int, int]) -> bool:
        if self.c_flag:
            highlight = (
                    (self.WINDOW.x[self.pos[0]] - self.dimensions[0] / 2 <= mouse_pos[0] <= self.WINDOW.x[self.pos[0]] + self.dimensions[0] / 2) and
                    (self.WINDOW.y[self.pos[1]] - self.dimensions[1] / 2 <= mouse_pos[1] <= self.WINDOW.y[self.pos[1]] + self.dimensions[1] / 2)
            )
        else:
            highlight = (
                    (self.WINDOW.x[self.pos[0]] <= mouse_pos[0] <= self.WINDOW.x[self.pos[0]] + self.dimensions[0]) and
                    (self.WINDOW.y[self.pos[1]] <= mouse_pos[1] <= self.WINDOW.y[self.pos[1]] + self.dimensions[1])
            )

        if highlight:
            self.bg_colour = (200, 200, 200)
        else:
            self.bg_colour = (255, 255, 255)

        return highlight

    def click(self, mouse_down: bool) -> bool:
        return self.hover(pygame.mouse.get_pos()) and mouse_down

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, val: str) -> None:
        self._text = val

        # Re-render text
        self.rendText = self.font.render(self._text, True, (0, 0, 0))

        if self.auto_size:
            self.dimensions = self.rendText.get_rect().size

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, val: tuple[int, int]) -> None:
        self._pos = val

    @property
    def width(self) -> int:
        return self.dimensions[0]

    @width.setter
    def width(self, val: int) -> None:
        self.dimensions = (val, self.dimensions[1])

    @property
    def height(self) -> int:
        return self.dimensions[1]

    @height.setter
    def height(self, val: int) -> None:
        self.dimensions = (self.dimensions[0], val)


class TextBox:
    def __init__(self, window: Screen, text: str, pos: tuple[int, int], centre_flag: bool = True, font_family: str = "Helvetica", font_size: int = 20) -> None:
        self._text = text
        self._pos = pos

        self.c_flag = centre_flag

        self.WINDOW = window

        self.font = pygame.font.SysFont(font_family, font_size)

        self.rendText = self.font.render(text, True, (0, 0, 0))

    def draw(self, screen: pygame.surface.Surface) -> None:
        if self.c_flag:
            x, y = self.WINDOW.x[self.pos[0]], self.WINDOW.y[self.pos[1]]
            width, height = self.rendText.get_rect().size
            screen.blit(self.rendText, (x - width / 2, y - height / 2))
        else:
            screen.blit(self.rendText, (self.WINDOW.x[self.pos[0]], self.WINDOW.y[self.pos[1]]))

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text
        self.rendText = self.font.render(text, True, (0, 0, 0))

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, val: tuple[int, int]) -> None:
        self._pos = val


class Paragraph:
    def __init__(
            self, window: Screen, text: str, pos: tuple[int, int],
            centre_flag: bool = True, font_family: str = "Helvetica", font_size: int = 20
    ) -> None:
        self.texts = [TextBox(window, line, (pos[0], pos[1] + i), centre_flag, font_family, font_size) for (i, line) in enumerate(text.split("\n"))]
        self.c_flag = centre_flag
        self.font_family = font_family
        self.font_size = font_size
        self.pos = pos

        self.WINDOW = window

    def draw(self, screen: pygame.surface.Surface) -> None:
        for text in self.texts:
            text.draw(screen)

    @property
    def text(self) -> str:
        total = ""
        for text in self.texts:
            total += text.text + '\n'

        total = total[:-1]

        return total

    @text.setter
    def text(self, val: str) -> None:
        self.texts = []
        for (i, line) in enumerate(val.split("\n")):
            self.texts.append(TextBox(self.WINDOW, line, (self.pos[0], self.pos[1] + i), self.c_flag, self.font_family, self.font_size))


# TODO Could add pos var to this to make paragraphs easier to move

# Function to get image file
def getFile() -> str:
    file_path = filedialog.askopenfilename(filetypes=(("JPEGs", "*.jpg .jpeg"),))

    return file_path
