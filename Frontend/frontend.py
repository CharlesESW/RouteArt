# Code to start program
from pathlib import Path

import pygame
import tkinter as tk
from tkinter import filedialog

pygame.font.init()

FONT = pygame.font.SysFont("Helvetica", 20)

root = tk.Tk()
root.withdraw()

# Image class
class Image:
    # Load image
    def __init__(
        self, path: str | Path | None = None, pos: tuple[int, int] = (0, 0), size: tuple[int, int] | None = None,
        center_flag: bool = False, alpha: float = 1
        ) -> None:

        if path is not None:
            self.img = pygame.image.load(path)
            self.img.set_alpha(int(alpha * 255))

        self.path = path

        self.c_flag = center_flag

        self._alpha = alpha
        self._pos = pos

        if size is not None:
            pygame.transform.scale(self.img, size)

    # Display image to screen
    def draw(self, display: pygame.surface.Surface) -> None:
        if self.path is not None:
            if self.c_flag:
                x, y = self.pos
                wid, height = self.img.get_rect().size
                display.blit(self.img, (x-wid/2, y-height/2))
            else:
                display.blit(self.img, self.pos)

    # Reload image
    def reloadImage(self, path: str | Path):
        self.img = pygame.image.load(path)
        self.img.set_alpha(int(self._alpha * 255))

    def resizeImage(self, size: tuple[int, int]) -> None:
        self.img = pygame.image.load(self.path)

        pygame.transform.scale(self.img, size)

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
        self, text: str, pos: tuple[int, int], size: tuple[int, int] | None = None, center_flag: bool = False,
        border: int = 2, border_curve: bool = False, auto_size: bool = True) -> None:
        self._text = text
        self._pos = pos
        self.dims = size

        self.c_flag = center_flag
        self.border = border
        self.border_curve = border_curve
        self.auto_size = auto_size
        self.bg_colour = (255, 255, 255)

        # Render text
        self.rendText = FONT.render(self._text, True, (0, 0, 0))

        if self.dims is None and not self.auto_size:
            raise BaseException("Fuck you Matt you caused this stupid fucking error to occur this would not have to exist if you didn't want to do the silly billy math just put in some fucking dimensions it's just trial and error you fuck")

        if self.auto_size:
            self.dims = [*map(lambda x: x+2, self.rendText.get_rect().size)]

    def draw(self, display: pygame.surface.Surface):
        if self.c_flag:
            x, y = self._pos
            width, height = self.dims
            x -= width/2
            y -= height/2

        else:
            x, y = self._pos

        pygame.draw.rect(display, (0, 0, 0), (x, y, *self.dims), 2*self.border_curve)
        pygame.draw.rect(display, self.bg_colour, (*map(lambda x: x + self.border, (x, y)), *map(lambda x: x - 2*self.border, self.dims)))
    
        text_dims = self.rendText.get_rect().size
        x, y = map(lambda x: x[0] + (x[1]-x[2])/2, zip((x, y), self.dims, text_dims))
        display.blit(self.rendText, (x, y))

    def hover(self, mouse_pos: tuple[int, int]) -> bool:
        # TODO add hover highlighting?
        if self.c_flag:
            highlight = (
                (self.pos[0]-self.dims[0]/2 <= mouse_pos[0] <= self.pos[0] + self.dims[0]/2) and 
                (self.pos[1]-self.dims[1]/2 <= mouse_pos[1] <= self.pos[1] + self.dims[1]/2)
                )
        else:
            highlight = (
                (self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.dims[0]) and 
                (self.pos[1] <= mouse_pos[1] <= self.pos[1] + self.dims[1])
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
        self.rendText = FONT.render(self._text, True, (0, 0, 0))

        if self.auto_size:
            self.dims = self.rendText.get_rect().size

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, val: tuple[int, int]) -> None:
        self._pos = val

    @property
    def width(self) -> int:
        return self.dims[0]

    @width.setter
    def width(self, val: int) -> None:
        self.dims = (val, self.dims[1])

    @property
    def height(self) -> int:
        return self.dims[1]

    @height.setter
    def height(self, val: int) -> None:
        self.dims = (self.dims[0], val)

class TextBox:
    def __init__(self, text: str, pos: tuple[int, int], centre_flag: bool = False) -> None:
        self._text = text
        self._pos = pos

        self.c_flag = centre_flag
        self.rendText = FONT.render(text, True, (0, 0, 0))
        
    def draw(self, screen) -> None:
        if self.c_flag:
            x, y = self._pos
            width, height = self.rendText.get_rect().size
            screen.blit(self.rendText, (x-width/2, y-height/2))
        else:
            screen.blit(self.rendText, self._pos)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text
        self.rendText = FONT.render(text, True, (0, 0, 0))

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, val: tuple[int, int]) -> None:
        self._pos = val

# Function to get image file
def getFile() -> str:
    file_path = filedialog.askopenfilename(filetypes=(("JPEGs", "*.jpg .jpeg"), ))

    return file_path