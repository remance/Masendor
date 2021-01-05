import pygame
import pygame.freetype
import csv
import ast

from gamescript import gamemap

terraincolour = gamemap.terraincolour
featurecolour = gamemap.featurecolour

class Teamcoa(pygame.sprite.Sprite):
    def __init__(self, pos, image, team, name):

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.selectedimage = pygame.Surface((200, 200))
        self.notselectedimage = pygame.Surface((200, 200))
        self.notselectedimage.fill((0, 0, 0)) # black border when not selected
        self.selectedimage.fill((230, 200, 15))  # gold border when selected

        whitebody = pygame.Surface((196, 196))
        whitebody.fill((255,255,255))
        whiterect = whitebody.get_rect(topleft = (2, 2))
        self.notselectedimage.blit(whitebody, whiterect)
        self.selectedimage.blit(whitebody, whiterect)

        #v Coat of arm image to image
        coaimage = pygame.transform.scale(image, (100, 100))
        coarect = coaimage.get_rect(center = (100, 70))
        self.notselectedimage.blit(coaimage, coarect)
        self.selectedimage.blit(coaimage, coarect)
        #^ End Coat of arm

        #v Faction name to image
        self.font = pygame.font.SysFont("oldenglishtext", 32)
        self.textsurface = self.font.render(str(name), 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center = (100, 150))
        self.notselectedimage.blit(self.textsurface, self.textrect)
        self.selectedimage.blit(self.textsurface, self.textrect)
        #^ End faction name

        self.image = self.notselectedimage
        self.rect = self.image.get_rect(center=pos)
        self.team = team
        self.selected = False

    def changeselect(self):
        if self.selected:
            self.image = self.selectedimage
        else:
            self.image = self.notselectedimage

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