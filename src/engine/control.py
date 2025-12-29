import pygame
from pygame.surface import Surface
from pygame.time import Clock

from .entities import Scene
from .essentials import BLACK


class Control:
    def __init__(
        self,
        display: Surface,
        screen_size: tuple[int, int],
        fps: int,
        scenes: dict[str, Scene],
        initial_scene_id: str,
    ) -> None:
        self.display = display
        self.screen_size = screen_size
        self.screen = Surface(screen_size)
        self.clock, self.fps = Clock(), fps
        self.scenes = scenes
        self.active_scene = self.scenes[initial_scene_id]

    def main_loop(self) -> bool:  # Returns if should relaunch
        while True:
            time_elapsed = self.clock.tick(self.fps) / 1000  # in seconds
            self.active_scene.update(time_elapsed)
            self.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                self.active_scene.handle_event(event)

    def render(self) -> None:
        self.screen.fill(BLACK)
        if sprite := self.active_scene.get_embedded_surface():
            self.screen.blit(sprite.sfc, sprite.pos)
        scaled = pygame.transform.smoothscale(self.screen, self.display.get_size())
        scaled_rect = scaled.get_rect(center=self.display.get_rect().center)
        self.display.blit(scaled, scaled_rect)
        pygame.display.update()
