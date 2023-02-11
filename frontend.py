# Want to display images and have image overlay with varying visability
# Simple to do, just use canvas with alpha colour enabled and then display on top of one another

# Want buttons
# Simple class

# Want entry?
# Similar to butttons

# Want image input
# Not sure how this will work

# Using JPEGs

# Prototype 1: Just getting images to display with varying visability
import pygame

pygame.init()

screen = pygame.display.set_mode((400, 400))

class Image:
    # Load image
    def __init__(self, path: str, alpha: float = 1) -> None:
        self.img = pygame.image.load(path)
        self.img.set_alpha(int(alpha * 255))

        self._alpha = alpha

    # Display image to screen
    def blitImage(self, display: pygame.surface.Surface, loc: tuple[int, int]) -> None:
        display.blit(self.img, loc)

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, val: float) -> None:
        self._alpha = val