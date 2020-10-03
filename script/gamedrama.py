import pygame
import pygame.freetype
from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class Textdrama(pygame.sprite.Sprite):
    images = []

    def __init__(self):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (SCREENRECT.width/2, SCREENRECT.height/4)
        self.font = pygame.font.SysFont("helvetica", 102)

    def slowdrama(self, input):
        self.textinput = input
        textsurface = self.font.render(self.textinput, 1, (0, 0, 0))  ## description
        textrect = textsurface.get_rect(topleft=(1, 1))
        self.image = pygame.Surface((textrect.width, textrect.height), pygame.SRCALPHA)
        self.image.blit(textsurface, textrect)
        self.rect = self.image.get_rect(topleft=self.pos)