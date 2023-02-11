# Code to start program
import pygame
import sys

pygame.init()
pygame.font.init()

FONT = pygame.font.SysFont("Helvetica", 20)

# Image class
class Image:
    # Load image
    def __init__(self, path: str, alpha: float = 1, pos: tuple[int, int] = (0, 0)) -> None:
        self.img = pygame.image.load(path)
        self.img.set_alpha(int(alpha * 255))

        self._alpha = alpha
        self._pos = pos

    # Display image to screen
    def blitImage(self, display: pygame.surface.Surface) -> None:
        display.blit(self.img, self.pos)

    # Reload image
    def reloadImage(self, path: str):
        self.img = pygame.image.load(path)
        self.img.set_alpha(int(self._alpha * 255))

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, val: float) -> None:
        self._alpha = val
        self.img.set_alpha(int(self._alpha * 255))

    @property
    def pos(self) -> tuple[int, int]:
        return self.pos

    @pos.setter
    def pos(self, val: tuple[int, int]) -> None:
        self._pos = val

# Button Class
class Button:
    def __init__(self, text: str, pos: tuple[int, int], dims: tuple[int, int]) -> None:
        self._text = text
        self._pos = pos
        self.dims = dims

        # Render text
        self.rendText = FONT.render(self._text, True, (0, 0, 0))

    def draw(self, display: pygame.surface.Surface):
        BORDER = 2
        pygame.draw.rect(display, (0, 0, 0), (*self._pos, *self.dims))
        pygame.draw.rect(display, (255, 255, 255), (*map(lambda x: x + BORDER, self._pos), *map(lambda x: x - 2*BORDER, self.dims)))
    
        text_dims = self.rendText.get_rect().size
        x, y = map(lambda x: x[0] + (x[1]-x[2])/2, zip(self.pos, self.dims, text_dims))
        display.blit(self.rendText, (x, y))

    def hover(self, mouse_pos: tuple[int, int]) -> bool:
        # TODO add hover highlighting?
        return (
            (self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.dims[0]) and 
            (self.pos[1] <= mouse_pos[1] <= self.pos[1] + self.dims[1])
        )

    def click(self, mouse_pos: tuple[int, int], mouse_state: bool) -> bool:
        # TODO Rate limit click button
        return self.hover(mouse_pos) and mouse_state

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, val: str) -> None:
        self._text = val

        # Re-render text
        self.rendText = FONT.render(self._text, True, (0, 0, 0))

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

# TODO Image input box

class ImageInput:
    def __init__(self) -> None:
        pass

# TODO Entry box?

## Test Area
screen = pygame.display.set_mode((400, 400))

buttons = [
    Button("hi", (10, 20), (30, 30)),
    Button("this button", (40, 100), (90, 20)),
]

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    for button in buttons:
        button.draw(screen)
        if button.click(pygame.mouse.get_pos(), pygame.mouse.get_pressed(3)[0]):
            print(button.text)

    pygame.display.flip()