import pygame
import pygame.freetype
import random
from RTS import mainmenu

SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir

class Weather:
    def __init__(self, type, level, allweather):
        self.stat = allweather[type]
        self.temperature
        self.statuseffect
        self.level = level ## Weather level 0 = Light, 1 = Normal, 2 = Strong
        self.spawnrate = level + 1

    def weatherchange(self, level):
        self.level = level

class Mattersprite(pygame.sprite.Sprite):
    def __init__(self, pos, target, images, type):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.type = type
        self.speed = 100
        # if type in (0,1,2):
        #     self.speed =
        self.pos = pos
        self.image = images[random.randint(0,len(images)-1)]
        self.rect = self.image.get_rect(center=self.pos)
        self.target = target

    def update(self, dt):
        move = self.target - self.pos
        move_length = move.length()
        if move_length > 0.1:
            move.normalize_ip()
            move = move * self.speed  * dt
            if move.length() > move_length:
                move = self.target - self.pos
                move.normalize_ip()
            self.pos += move
            self.rect.center = list(int(v) for v in self.pos)
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