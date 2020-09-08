import pygame
import pygame.freetype

from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class camera():
    def __init__(self, startpos, zoom):
        self.scale = zoom
        self.pos = startpos
        self.image = pygame.Surface((SCREENRECT.width,SCREENRECT.height))

    def update(self, pos, surfaces):
        self.image.fill((0,0,0))
        self.pos = pos
        for surface in surfaces:
            surface_x, surface_y = surface.pos
            surface_w, surface_h = surface.image.get_rect().size
            rect = pygame.Rect(surface_x - self.pos[0], surface_y - self.pos[1], surface_w, surface_h)
            self.image.blit(surface.image, rect)