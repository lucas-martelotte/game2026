from dataclasses import dataclass

from pygame.surface import Surface

from ..essentials import Anchor


@dataclass
class SpriteFrame:
    sfc: Surface
    anchor: Anchor
    audio: str | None


@dataclass
class SpriteSheet:
    animation_sequence_dict: dict[str, list[SpriteFrame]]
    sequence_transition_dict: dict[str, str]
    initial_animation_sequence: str


class Sprite:
    def __init__(self, sprite_sheet: SpriteSheet, fps: int):
        self.sprite_sheet = sprite_sheet
        self.fps = fps
        # TODO!!
