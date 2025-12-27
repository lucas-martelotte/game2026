from dataclasses import dataclass

from pygame.event import Event
from pygame.surface import Surface


@dataclass
class EmbeddedSurface:
    sfc: Surface
    pos: tuple[int, int]


class Entity:
    def __init__(self):
        self.should_update_embedded_surface = False
        self._embedded_surface: EmbeddedSurface | None = None

    def update(self, time_elapsed: float) -> None:
        self.should_update_embedded_surface = True
        return

    def handle_event(self, event: Event) -> None:
        return

    def _update_embedded_surface(self) -> None:
        return

    def get_embedded_surface(self) -> EmbeddedSurface | None:
        if self.should_update_embedded_surface:
            self._update_embedded_surface()
        return self._embedded_surface
