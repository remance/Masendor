import pygame
import pygame.freetype

from .. import main

main_dir = main.main_dir
SCREENRECT = main.SCREENRECT


class Camera():
    def __init__(self, startpos, viewmode):
        self.viewmode = viewmode
        self.pos = startpos
        self.image = pygame.Surface((SCREENRECT.width, SCREENRECT.height))

    def update(self, pos, surfaces):
        self.image.fill((0, 0, 0))
        self.pos = pos
        camera_w, camera_h = self.image.get_rect().size
        camera_x = self.pos[0] - camera_w / 2
        camera_y = self.pos[1] - camera_h / 2
        for surface in surfaces:
            surface_x, surface_y = surface.rect.left, surface.rect.top
            surface_w, surface_h = surface.image.get_rect().size
            rect = pygame.Rect(surface_x - camera_x, surface_y - camera_y, surface_w, surface_h)
            # if hasattr(surface, 'gameid'):
            #     print(surface.gameid, surface.pos, rect.center)
            self.image.blit(surface.image, rect)
