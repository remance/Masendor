import pygame
import pygame.freetype
from RTS import mainmenu

SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir



class Lorebook(pygame.sprite.Sprite):

    def __init__(self, image):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.image_original = self.image.copy()
        self.section = 0 ## 0 = intro, 1 = concept, 2 = faction, 3 = unit, 4 = equipment, 5 = unit status, 6 = unit skill, 7 = unit trait, 8 = leader, 9 terrain, 10 = landmark
        self.subsection = 0 ## subsection of that section e.g. swordmen unit in unit section
        self.page = 0
        self.rect = self.image.get_rect(center=(SCREENRECT.width/2, SCREENRECT.height/2))

    def changepage(self, page):
        self.page = page
        self.image = self.image_original.copy()

    def changesection(self, section):
        self.section = section
        self.page = 0

    def changesubsection(self, subsection):
        self.subsection = subsection
        self.page = 0
    # def intropage(self):
    #
    # def conceptpage(self):
    #
    # def factionpage(self):
    #
    # def unitpage(self, unitimage, stat, description, lore):
    #
    # def equipmentpage(self):
    #
    # def leaderpage(self, leaderimage, stat, description, lore):
    #
    # def statuspage(self, image, stat, description, lore):
    #
    # def skillpage(self, image, stat, description, lore):
    #
    # def traitpage(self, image, stat, description, lore):
    #
    # def terrainpage(self):
    #
    # def landmarkpage(self):

class searchbox(pygame.sprite.Sprite):
    def __init__(self, textsize=16):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.image = pygame.Surface(100,50)