from enum import Enum, IntEnum, auto

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class MouseButtons(IntEnum):
    """Numbers are specific to match with the pygame convention"""

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5


class Anchor(Enum):
    TOPRIGHT = auto()
    MIDRIGHT = auto()
    BOTTOMRIGHT = auto()
    TOPLEFT = auto()
    MIDLEFT = auto()
    BOTTOMLEFT = auto()
    CENTER = auto()
    MIDTOP = auto()
    MIDBOTTOM = auto()
