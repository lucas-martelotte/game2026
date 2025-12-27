from math import cos, pi, sin

import pygame
from pygame.surface import Surface

from src.engine import Control
from src.engine.entities import EmbeddedSurface, Entity, MovableEntity
from src.engine.essentials import RED, WHITE, FPos


class Oscilator(MovableEntity):
    def __init__(self):
        super().__init__()
        self._sfc = Surface((20, 20))
        self._sfc.fill(RED)
        self._phase = 0

    def update(self, time_elapsed: float) -> None:
        super().update(time_elapsed)
        self._phase += time_elapsed
        while self._phase > 2 * pi:
            self._phase -= 2 * pi
        self.fvel = FPos((100 * sin(self._phase), (-100 * cos(self._phase))))

    def get_embedded_surface(self) -> EmbeddedSurface | None:
        rect = self._sfc.get_rect(center=self.pos.to_tuple())
        return EmbeddedSurface(self._sfc, (rect.left, rect.top))


class SimpleScene(Entity):
    def __init__(self):
        super().__init__()
        sfc = Surface((480, 270))
        sfc.fill(WHITE)
        self._embedded_surface = EmbeddedSurface(sfc, (240, 135))
        self.oscilator = Oscilator()
        self.oscilator.fpos = FPos((135, 125))  # SQUARE OF SIDE LENGTH = 20

    def update(self, time_elapsed: float) -> None:
        super().update(time_elapsed)
        self.oscilator.update(time_elapsed)

    def _update_embedded_surface(self) -> None:
        assert self._embedded_surface is not None
        sfc = self._embedded_surface.sfc
        sfc.fill(WHITE)
        oscilator_embsfc = self.oscilator.get_embedded_surface()
        assert oscilator_embsfc is not None
        sfc.blit(oscilator_embsfc.sfc, oscilator_embsfc.pos)


if __name__ == "__main__":
    display_size, fullscreen = (1920, 1080), False
    display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    control = Control(display, (960, 540), 24, {"scene": SimpleScene()}, "scene")
    control.main_loop()
