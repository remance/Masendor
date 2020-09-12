import pygame
import pygame.freetype
import csv
from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

## Terrain base colour
Temperate = (166,255,107,255)
Tropical = (255,199,13,255)
Volcanic = (255,127,39,255)
Desert = (240,229,176,255)
Arctic = (211,211,211,255)
Blight = (163,73,164,255)
Void = (255,255,255,255)
Demonic = (237,28,36,255)
Death = (127,127,127,255)
ShallowWater = (153,217,235,255)
DeepWater = (100,110,214,255)

## Terrain Feature colour

Plain = (181,230,29,255)
Barren = (255,127,39,255)
PlantField = (167,186,139,255)
Forest = (16,84,36,255)
InlandWater = (133,254,239,255)
Road = (130,82,55,255)
UrbanBuilding = (147,140,136,255)
Farm = (255,242,0,255)
Wall = (102,92,118,255)
Mana = (101,109,214,255)
Rot = (200,191,231,255)
Wetground = (255)

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
        self.terraincolour = [Temperate,Tropical,Volcanic,Desert,Arctic,Blight,Void,Demonic,Death,ShallowWater,DeepWater]

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
        self.featurecolour = [Plain,Barren,PlantField,Forest,InlandWater,Road,UrbanBuilding,Farm,Wall,Mana,Rot,Wetground] ## forest, tall plant/grass, field, road/bridge, wall, urban building
        self.featuremod = {}
        with open(main_dir + "\data\map" + '\\unit_terrainbonus.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.featuremod[row[0]] = row[1:]
        unitfile.close()



    def changescale(self,scale):
        self.scale = scale
        self.image = self.image_original
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def getfeature(self, pos, gamemap):
        terrainindex = gamemap.getterrain(pos)
        feature = self.image.get_at((int(pos[0]), int(pos[1]))) ##get colour at pos to obtain the terrain type
        featureindex = None
        if feature in self.featurecolour:
            featureindex = self.featurecolour.index(feature)
            featureindex = featureindex + (terrainindex * 11)
        return terrainindex, featureindex

class mapheight(pygame.sprite.Sprite):
    images = []

    def __init__(self, scale):
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

    def changescale(self,scale):
        self.scale = scale
        self.image = self.image_original
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def getheight(self, pos):
        heightindex = 255 - self.image.get_at((int(pos[0]), int(pos[1])))[2] ##get colour at pos to obtain the terrain type
        return heightindex


class beautifulmap(pygame.sprite.Sprite):
    images = []

    def __init__(self, x, y, image):
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.containers)

