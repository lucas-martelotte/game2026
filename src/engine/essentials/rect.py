from numpy import array, ndarray
from pygame.rect import Rect as PygameRect

from .pos import FPos, Pos


class Rect:
    def __init__(self, x: int, y: int, width: int, height: int):
        assert width > 0 and height > 0
        self.width, self.height = width, height
        self.x, self.y = x, y

    def move(self, vector: Pos) -> "Rect":
        return Rect(self.x + vector.x, self.y + vector.y, self.width, self.height)

    def pos(self) -> Pos:
        return Pos((self.x, self.y))

    def to_tuple(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.width, self.height

    def to_array(self) -> ndarray:
        array_list = [
            [self.x, self.y],
            [self.x + self.width, self.y],
            [self.x + self.width, self.y + self.height],
            [self.x, self.y + self.height],
        ]
        return array(array_list)

    @staticmethod
    def from_pygame(rect: PygameRect) -> "Rect":
        return Rect(rect[0], rect[1], rect[2], rect[3])

    @staticmethod
    def from_tuple(pos: tuple[int, int, int, int]) -> "Rect":
        return Rect(pos[0], pos[1], pos[2], pos[3])

    @property
    def center(self) -> Pos:
        return Pos((self.x_middle, self.y_middle))

    @property
    def x_middle(self) -> int:
        return self.x + self.width // 2

    @property
    def y_middle(self) -> int:
        return self.y + self.height // 2

    @property
    def top_left(self) -> Pos:
        return Pos((self.left, self.top))

    @property
    def top_right(self) -> Pos:
        return Pos((self.right, self.top))

    @property
    def bottom_left(self) -> Pos:
        return Pos((self.left, self.bottom))

    @property
    def bottom_right(self) -> Pos:
        return Pos((self.right, self.bottom))

    @property
    def left(self) -> int:
        return self.x

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + self.height
