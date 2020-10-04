import pygame
import pygame.freetype
from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class Menubox(pygame.sprite.Sprite):
    images = []

    def __init__(self):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (SCREENRECT.width/2, SCREENRECT.height/2)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.mode = 0

    def changemode(self, mode):
        self.mode = mode
        self.image = self.images[mode]


class Menubutton(pygame.sprite.Sprite):
    def __init__(self, images, pos, text="", size=16):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.images = [image.copy() for image in images]
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", size)
        if text != "":
            self.textsurface = self.font.render(self.text, 1, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(self.textsurface, self.textrect)
            self.images[1].blit(self.textsurface, self.textrect)
            self.images[2].blit(self.textsurface, self.textrect)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.event = False
