import ast
import csv
import random

import pygame
import pygame.freetype
from PIL import Image, ImageFilter

## Terrain base colour
Temperate = (166, 255, 107, 255)
Tropical = (255, 199, 13, 255)
Volcanic = (255, 127, 39, 255)
Desert = (240, 229, 176, 255)
Arctic = (211, 211, 211, 255)
Blight = (163, 73, 164, 255)
Void = (255, 255, 255, 255)
Demonic = (237, 28, 36, 255)
Death = (127, 127, 127, 255)
ShallowWater = (153, 217, 235, 255)
DeepWater = (100, 110, 214, 255)

## Terrain Feature colour

Plain = (181, 230, 29, 255)
Barren = (255, 127, 39, 255)
PlantField = (167, 186, 139, 255)
Forest = (16, 84, 36, 255)
InlandWater = (133, 254, 239, 255)
Road = (130, 82, 55, 255)
UrbanBuilding = (147, 140, 136, 255)
Farm = (255, 242, 0, 255)
Wall = (102, 92, 118, 255)
Mana = (101, 109, 214, 255)
Rot = (200, 191, 231, 255)
Wetground = (186, 184, 109, 255)


class Basemap(pygame.sprite.Sprite):
    images = []
    maxviewmode = 10

    def __init__(self, scale):
        """image file of map should be at size 1000x1000 then it will be scaled in game"""
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.trueimage = self.image.copy()
        self.scale = scale
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.terraincolour = (Temperate, Tropical, Volcanic, Desert, Arctic, Blight, Void, Demonic, Death, ShallowWater, DeepWater)

    def getterrain(self, pos):
        terrain = self.trueimage.get_at((int(pos[0]), int(pos[1])))  ##get colour at pos to obtain the terrain type
        terrainindex = self.terraincolour.index(terrain)
        return terrainindex

    # def update(self, dt, pos, scale):


class Mapfeature(pygame.sprite.Sprite):
    images = []
    maxviewmode = 10
    main_dir = None

    def __init__(self, scale):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.trueimage = self.image.copy()
        self.scale = scale
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.featurecolour = (Plain, Barren, PlantField, Forest, InlandWater, Road, UrbanBuilding, Farm, Wall, Mana, Rot, Wetground)
        self.featuremod = {}
        with open(self.main_dir + "\data\map" + '\\unit_terrainbonus.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                for n, i in enumerate(row):
                    if run != 0:
                        if n == 11:
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif n in (2, 3, 4, 5, 6, 7):
                            if i != "":
                                row[n] = float(i) / 100
                            else:
                                i = 1.0
                        elif i.isdigit() or "-" in i:
                            row[n] = int(i)
                run += 1
                self.featuremod[row[0]] = row[1:]
        unitfile.close()

    def getfeature(self, pos, gamemap):
        terrainindex = gamemap.getterrain(pos)
        feature = self.trueimage.get_at((int(pos[0]), int(pos[1])))  ##get colour at pos to obtain the terrain type
        featureindex = None
        if feature in self.featurecolour:
            featureindex = self.featurecolour.index(feature)
            featureindex = featureindex + (terrainindex * 12)
        return terrainindex, featureindex


class Mapheight(pygame.sprite.Sprite):
    images = []
    maxviewmode = 10

    def __init__(self, scale):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.trueimage = self.image.copy()
        self.scale = scale
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(topleft=(0, 0))

    def changescale(self, scale):
        self.scale = scale
        self.image = self.image_original.copy()
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def getheight(self, pos):
        colour = self.trueimage.get_at((int(pos[0]), int(pos[1])))[2]
        if colour == 0: colour = 255
        heightindex = 255 - colour  ##get colour at pos to obtain the terrain type
        return heightindex


class Beautifulmap(pygame.sprite.Sprite):
    textureimages = []
    emptyimage = None
    effectimage = None
    placename = None
    loadtexturelist = None
    main_dir = None

    def __init__(self, scale, basemap, featuremap, gamemapheight):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = featuremap.image.copy()
        self.scale = scale
        self.mode = 0
        self.newcolourlist = {}
        with open(self.main_dir + "\data\map" + '\\colourchange.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif "," in i:
                        row[n] = ast.literal_eval(i)
                self.newcolourlist[row[0]] = row[1:]
        for rowcount, rowpos in enumerate(range(0, 1000)):  ## Recolour the map
            for colcount, colpos in enumerate(range(0, 1000)):
                terrain, feature = featuremap.getfeature((rowpos, colpos), basemap)
                newcolour = self.newcolourlist[feature][1]
                rect = pygame.Rect(rowpos, colpos, 1, 1)
                self.image.fill(newcolour, rect)
        ## Comment out this part and import PIL above if not want to use blur filtering
        data = pygame.image.tostring(self.image, 'RGB')  ## Convert image to string data for filtering effect
        img = Image.frombytes('RGB', (1000, 1000), data)  ## Use PIL to get image data
        img = img.filter(ImageFilter.GaussianBlur(radius=2))  ## Blue Image (or apply other filter in future)
        img = img.tobytes()
        img = pygame.image.fromstring(img, (1000, 1000), 'RGB')  ## Convert image back to a pygame surface
        self.image = pygame.Surface(
            (1000, 1000))  ## For unknown reason using the above surface cause a lot of fps drop so make a new one and blit the above here
        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(img, rect)
        ## PIL module code till here
        for rowpos in range(0, 991):  ## Put in terrain texture
            for colpos in range(0, 991):
                if rowpos % 20 == 0 and colpos % 20 == 0:
                    randompos = (rowpos + random.randint(0, 19), colpos + random.randint(0, 19))
                    terrain, thisfeature = featuremap.getfeature((randompos), basemap)
                    feature = self.textureimages[self.loadtexturelist.index(self.newcolourlist[thisfeature][0].replace(" ", "").lower())]
                    choose = random.randint(0, len(feature) - 1)
                    if thisfeature - (terrain * 12) in (0, 1, 4, 5, 7) and random.randint(0,
                                                                                          100) < 60:  ## reduce speical texture in empty terrain like glassland
                        thistexture = self.emptyimage  ## empty texture
                    else:
                        thistexture = feature[choose]
                    rect = thistexture.get_rect(center=(randompos))
                    self.image.blit(thistexture, rect)
        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(self.effectimage, rect)  ## Add special filter effect that make it look like old map
        self.image.blit(self.placename, rect)  ## Add placename layer to map
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.trueimage = self.image.copy()
        self.image_original = self.image.copy()
        self.imagewithheight_original = self.image.copy()
        self.imagewithheight_original.blit(gamemapheight.image, rect)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(topleft=(0, 0))

    def changemode(self, mode):
        self.mode = mode
        self.changescale(self.scale)

    def changescale(self, scale):
        self.scale = scale
        scalewidth = self.image_original.get_width() * self.scale
        scaleheight = self.image_original.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        if self.mode == 0:
            self.image = self.image_original.copy()
            self.image = pygame.transform.scale(self.image, (int(self.dim[0]), int(self.dim[1])))
        else:
            self.image = self.imagewithheight_original.copy()
            self.image = pygame.transform.scale(self.image, (int(self.dim[0]), int(self.dim[1])))
