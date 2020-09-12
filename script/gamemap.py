import pygame
import pygame.freetype

from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class map(pygame.sprite.Sprite):
    images = []

    def __init__(self, scale):
        """image file of map should be at size 1000x1000 then it will be scaled in game"""
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.scale = scale
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(topleft=(0,0))
        self.terraincolour = [(166,255,107,255),(255,199,13,255),(196,196,196,255),(240,229,176,255),(212,194,173,255),(112,145,189,255),(148,140,135,255),(153,217,235,255),(100,110,214,255)] ## grassland, plain, snow, desert, tundra, ice, barren, shallow water, deep water

    def changescale(self,scale):
        self.scale = scale
        self.image = self.image_original
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def getterrain(self, pos):
        terrain = self.image.get_at((int(pos[0]), int(pos[1]))) ##get colour at pos to obtain the terrain type
        terrainindex = self.terraincolour.index(terrain)
        return terrainindex

    # def update(self, dt, pos, scale):

class mapfeature(pygame.sprite.Sprite):
    images = []

    def __init__(self, scale):
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.scale = scale
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(topleft=(0,0))
        self.featurecolour = [(16,84,36,255),(167,186,139,255),(255,242,0,255),(130,82,55,255),(102,92,118,255),(147,140,136,255)] ## forest, tall plant/grass, field, bridge, wall, urban building

    def changescale(self,scale):
        self.scale = scale
        self.image = self.image_original
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def getfeature(self, pos):
        feature = self.image.get_at((int(pos[0]), int(pos[1]))) ##get colour at pos to obtain the terrain type
        featureindex = None
        if feature in self.featurecolour:
            featureindex = self.featurecolour.index(feature)
        return featureindex

class beautifulmap(pygame.sprite.Sprite):
    images = []

    def __init__(self, x, y, image):
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.containers)

