import math
import random

import numpy as np
import csv
import ast
import pygame
import pygame.freetype
from pygame.transform import scale

from gamescript import gamelongscript, gamebattalion, gameleader, gamemap

class Previewbox(pygame.sprite.Sprite):
    main_dir = None
    effectimage = None

    def __init__(self, pos):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.maxwidth = int(500 * self.widthadjust)
        self.maxheight = int(500 * self.heightadjust)
        self.image = pygame.Surface((self.maxwidth, self.maxheight))

        self.font = pygame.font.SysFont("timesnewroman", int(40 * self.heightadjust))

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

        self.changeterrain(self.newcolourlist[0])

        self.rect = self.image.get_rect(center=pos)

    def changeterrain(self, newterrain):
        self.image.fill(newterrain[1])

        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(self.effectimage, rect)  ## Add special filter effect that make it look like old map

        textsurface = self.font.render(newterrain[0], True, (0, 0, 0))
        textrect = textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(textsurface, textrect)

class Previewchangebutton(pygame.sprite.Sprite):
    def __init__(self, pos, image, text):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("timesnewroman", int(30 * self.heightadjust))

        self.image = image.copy()
        self.image_original = self.image.copy()

        self.text = text
        self.textsurface = self.font.render(text, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.textsurface, self.textrect)

        self.rect = self.image.get_rect(midbottom=pos)

    def changetext(self, text):
        self.image = self.image_original.copy()
        self.text = text
        self.textsurface = self.font.render(text, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.textsurface, self.textrect)



class Filterbox(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                    int(image.get_height() * self.heightadjust)))
        self.rect = self.image.get_rect(topleft=pos)


class Unitpreview(pygame.sprite.Sprite):
    def __init__(self, maingame, position, gameid, squadlist, colour, leader, leaderpos, coa, startangle, team):
        self = gamelongscript.addarmy(squadlist, position, gameid,
                       colour, (maingame.squadwidth, maingame.squadheight), leader+leaderpos, maingame.leaderstat, maingame.gameunitstat, True,
                       coa, False, startangle, 100, 100, team)