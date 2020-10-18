import pygame
import pygame.freetype
from RTS import mainmenu

SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir

class Lorebook(pygame.sprite.Sprite):
    conceptlore = None
    historylore = None
    factionlore = None
    unitstat = None
    unitlore = None
    armourstat = None
    weaponstat = None
    mountstat = None
    statusstat = None
    skillstat = None
    traitstat = None
    leaderstat = None
    leaderlore = None
    terrainstat = None
    landmarkstat = None

    def __init__(self, image, textsize=18):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.fontheader = pygame.font.SysFont("oldenglish", 48)
        self.image = image
        self.image_original = self.image.copy()
        self.section = 0 ## 0 = welcome/concept, 1 world history, 2 = faction, 3 = unit, 4 = equipment, 5 = unit status, 6 = unit skill, 7 = unit trait, 8 = leader, 9 terrain, 10 = landmark
        self.subsection = 1 ## subsection of that section e.g. swordmen unit in unit section Start with 1 instead of 0
        self.statdata = None ## for getting the section stat data
        self.loredata = None ## for getting the section lore data
        self.showsubsection = None ## Subsection stat showing
        self.showsubsection2 = None ## Subsection lore showing
        self.subsectionlist = None
        self.equipmentstat = {}
        run = 1
        for statlist in (self.weaponstat, self.armourstat, self.mountstat): ## Make new equipment list that contain all type
            for index in statlist:
                self.equipmentstat[run] = statlist[index]
                run += 1
        self.sectionlist = ((self.conceptlore,None),(self.historylore,None),(self.factionlore,None),(self.unitstat,self.unitlore),
                            (self.equipmentstat,None),(self.statusstat,None),(self.skillstat,None),
                            (self.traitstat,None),(self.leaderstat,self.leaderlore),(self.terrainstat,None))
        self.currentsubsectionrow = 0
        self.maxsubsectionshow = 20
        self.logsize = 0
        self.page = 0
        self.rect = self.image.get_rect(center=(SCREENRECT.width/1.9, SCREENRECT.height/1.9))
        self.qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")

    def changepage(self, page):
        self.page = page
        self.image = self.image_original.copy()
        self.pagedesign()

    def changesection(self, section, listsurface, listgroup, lorescroll):
        self.section = section
        self.page = 0
        self.subsection = 1
        self.statdata = self.sectionlist[self.section][0]
        self.loredata = self.sectionlist[self.section][1]
        thislist = self.statdata.values()
        self.subsectionlist = [name[0] for name in thislist][1:]
        self.logsize = len(self.subsectionlist)
        self.setupsubsectionlist(listsurface, listgroup)
        self.image = self.image_original.copy()
        lorescroll.changeimage(logsize=self.logsize)
        self.pagedesign()

    def changesubsection(self, subsection):
        self.subsection = subsection
        self.showsubsection = self.statdata[self.subsection]
        if self.loredata is not None:
            self.showsubsection2 = self.loredata[self.subsection]
        self.page = 0
        self.image = self.image_original.copy()
        self.pagedesign()

    def blit_text(self, surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  ## 2D array where each row is a list of words
        space = font.size(' ')[0]  ## the width of a space
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  ## reset x
                    y += word_height  ## start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  ## reset x
            y += word_height  ## start on new row

    def setupsubsectionlist(self, listsurface, listgroup):
        row = 15
        column = 15
        list = self.statdata
        pos = listsurface.rect.topleft
        if self.currentsubsectionrow > self.logsize - self.maxsubsectionshow:
            self.currentsubsectionrow = self.logsize - self.maxsubsectionshow
        # self.selectscroll.changeimage(newrow=self.lorenamelist.currentrow)
        if len(listgroup) > 0:
            for stuff in listgroup:
                stuff.kill()
                del stuff
        for index, item in enumerate(list.values()):
            if index != 0 and index >= self.currentsubsectionrow:
                name = item[0]
                listgroup.add(Subsectionname((pos[0] + column, pos[1] + row),name, index))
                row += 30
                if len(listgroup) > self.maxsubsectionshow: break

        # self.selectscroll.changeimage(logsize=self.lorenamelist.logsize)

    def pagedesign(self): #, portrait
        """Lore book format position of the text"""
        firstpagecol = 50
        secondpagecol = 650
        stat = self.statdata[self.subsection]
        name = stat[0]
        textsurface = self.fontheader.render(str(name), 1, (0, 0, 0))
        textrect = textsurface.get_rect(topleft=(30, 10))
        self.image.blit(textsurface, textrect)  ## Add name of item to the top of page
        # portraitrect = portrait.get_rect(topleft=(20, 60))
        # self.image.blit(portrait, portraitrect)
        description = stat[-1]
        descriptionsurface = pygame.Surface((300, 200), pygame.SRCALPHA)
        descriptionrect = descriptionsurface.get_rect(topleft=(100, 60))
        self.blit_text(descriptionsurface, description, (5, 5), self.font)
        self.image.blit(descriptionsurface, descriptionrect)
        if self.page == 0:
            frontstattext = self.statdata[self.subsection]

        # else:

class Subsectionlist(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topright=pos)

class Subsectionname(pygame.sprite.Sprite):
    def __init__(self, pos, name, subsection, textsize=16):
        self._layer = 14
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.image = pygame.Surface((100,25))
        self.image.fill((0,0,0))
        smallimage = pygame.Surface((98,23))
        smallimage.fill((255,255,255))
        smallrect = smallimage.get_rect(topleft=(1,1))
        self.image.blit(smallimage,smallrect)
        textsurface = self.font.render(str(name), 1, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(3, self.image.get_height()/2))
        self.image.blit(textsurface,textrect)
        self.subsection = subsection
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

class Selectionbox(pygame.sprite.Sprite):
    def __init__(self, pos, lorebook):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface(300, lorebook.image.get_height())

class Searchbox(pygame.sprite.Sprite):
    def __init__(self, textsize=16):
        self._layer = 14
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.image = pygame.Surface(100,50)
        self.text = ""
        self.textsurface = self.font.render(str(self.text), 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(centerleft=(3, self.image.get_height()/2))

    def textchange(self, input):
        newcharacter = pygame.key.name(input)
        self.text += newcharacter