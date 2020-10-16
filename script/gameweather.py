import pygame
import pygame.freetype
import random
from RTS import mainmenu

SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir

class Weather:
    def __init__(self, type, level, weatherlist):
        self.type = type
        stat = weatherlist[type]
        self.temperature = stat[16]
        self.level = level ## Weather level 0 = Light, 1 = Normal, 2 = Strong
        self.spawnrate = stat[18] * (level + 1)
        self.statuseffect = stat[19]
        self.spawnangle = stat[21]
        self.speed = stat[22] * (level + 1)

    # def weatherchange(self, level):
    #     self.level = level

class Mattersprite(pygame.sprite.Sprite):
    def __init__(self, pos, target, speed, image):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speed = speed
        # if type in (0,1,2):
        #     self.speed =
        self.pos = pygame.Vector2(pos)
        self.target = pygame.Vector2(target)
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        move = self.target - self.pos
        move_length = move.length()
        if move_length > 0.1:
            move.normalize_ip()
            move = move * self.speed  * dt
            self.pos += move
            self.rect.center = list(int(v) for v in self.pos)
            if move.length() > move_length:
                self.kill()
        else :
            self.kill()

class Specialeffect(pygame.sprite.Sprite):
    """Special effect from weather beyond sprite such as thunder, fog etc."""
    def __init__(self, pos, image):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface(SCREENRECT, pygame.SRCALPHA)
        imagerect = image.get_rect(topleft=(0,0))
        self.image.blit(image,imagerect)

class Supereffect(pygame.sprite.Sprite):
    """Super effect that affect whole screen"""
    def __init__(self, pos, image):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.containers)