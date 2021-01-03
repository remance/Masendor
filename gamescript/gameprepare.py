import pygame
import pygame.freetype
import csv
import ast

from gamescript import gamemap

terraincolour = gamemap.terraincolour
featurecolour = gamemap.featurecolour

class Mapshow(pygame.sprite.Sprite):
    def __init__(self, pos, basemap, featuremap):
        import main
        self.main_dir = main.main_dir

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((310, 310))
        self.image.fill((0, 0, 0)) # draw black colour for black corner
        # pygame.draw.rect(self.image, self.colour, (2, 2, self.widthbox - 3, self.heightbox - 3)) # draw block colour

        self.newcolourlist = {}
        with open(self.main_dir + "/data/map" + '/colourchange.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif "," in i:
                        row[n] = ast.literal_eval(i)
                self.newcolourlist[row[0]] = row[1:]

        self.changemap(basemap,featuremap)
        self.rect = self.image.get_rect(center=pos)


    def changemap(self, basemap, featuremap):
        newbasemap = pygame.transform.scale(basemap, (300,300))
        newfeaturemap = pygame.transform.scale(featuremap, (300,300))

        mapimage = pygame.Surface((300, 300))
        for rowpos in range(0, 300):  ## Recolour the map
            for colpos in range(0, 300):
                terrain = newbasemap.get_at((rowpos, colpos))  ##get colour at pos to obtain the terrain type
                terrainindex = terraincolour.index(terrain)

                feature = newfeaturemap.get_at((rowpos, colpos))  ##get colour at pos to obtain the terrain type
                featureindex = None
                if feature in featurecolour:
                    featureindex = featurecolour.index(feature)
                    featureindex = featureindex + (terrainindex * 12)
                newcolour = self.newcolourlist[featureindex][1]
                rect = pygame.Rect(rowpos, colpos, 1, 1)
                mapimage.fill(newcolour, rect)

        imagerect = mapimage.get_rect(topleft=(5,5))
        self.image.blit(mapimage,imagerect)
        self.image_original = self.image.copy()

    def changepos(self, newpos):
        self.rect = self.image.get_rect(center=newpos)