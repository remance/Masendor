import random, os.path, glob, csv, math
import pygame
from pygame.transform import scale
from pygame.locals import *
import pygame.freetype
from RTS import mainmenu

main_dir = mainmenu.main_dir

class map(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        """Scrollable and zoomable map"""
        self.image = image
        MAP_WIDTH = self.image.get_width()
        MAP_HEIGHT = self.image.get_height()
        self.pos = pygame.Vector2(x,y)
        self.dim = pygame.Vector2(MAP_WIDTH,MAP_HEIGHT)

    def update(self, dt, pos):
        self.pos.x = pos[0]
        self.pos.y = pos[1]
    def getPos(self):
        return self.pos

    def getDim(self):
        return self.dim

# Surface.get_at((x, y)) ##get colour at pos maybe can be used to create map from just picture?
