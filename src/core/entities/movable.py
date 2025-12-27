from ..essentials import FPos, Pos
from .entity import EmbeddedSurface, Entity


class MovableEntity(Entity):
    def __init__(self):
        super().__init__()
        self.fpos = FPos((0, 0))
        self.fvel = FPos((0, 0))
        self.facc = FPos((0, 0))

    def update(self, time_elapsed: float) -> None:
        super().update(time_elapsed)
        self.fpos += self.fvel * time_elapsed
        self.fvel += self.facc * time_elapsed

    @property
    def pos(self) -> Pos:
        return Pos(self.fpos.rounded())
