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
        self.body = self.images[0]
        self.leftcorner = self.images[1]
        self.rightcorner = self.images[2]
        self.pos = (SCREENRECT.width/2, SCREENRECT.height/4)
        self.font = pygame.font.SysFont("helvetica", 70)
        self.queue = []

    def processqueue(self):
        self.slowdrama(self.queue[0])
        self.queue = self.queue[1:]

    def slowdrama(self, input):
        self.textblit = False
        self.timer = 0
        self.currentlength = 20
        self.textinput = input
        self.leftcornerrect = self.leftcorner.get_rect(topleft=(0,0))
        self.textsurface = self.font.render(self.textinput, 1, (0, 0, 0))  ## description
        self.textrect = self.textsurface.get_rect(topleft=(30, 1))
        self.image = pygame.Surface((self.textrect.width+70, self.textrect.height), pygame.SRCALPHA)
        self.image.blit(self.leftcorner, self.leftcornerrect)
        self.rect = self.image.get_rect(center=self.pos)
        self.maxlength = self.image.get_width() - 20

    def playanimation(self):
        if self.currentlength < self.maxlength:
            bodyrect = self.body.get_rect(topleft=(self.currentlength,0))
            self.image.blit(self.body, bodyrect)
            rightcornerrect = self.rightcorner.get_rect(topleft=(self.currentlength+30, 0))
            self.image.blit(self.rightcorner, rightcornerrect)
            self.currentlength += self.body.get_width()
        elif self.currentlength >= self.maxlength and self.textblit is False:
            self.image.blit(self.textsurface, self.textrect)
            self.textblit = True

