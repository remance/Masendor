import ast
import csv

import pygame
import pygame.freetype
from gamescript import gamelongscript
from pygame.transform import scale


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

        self.font = pygame.font.SysFont("timesnewroman", int(24 * self.heightadjust))

        self.newcolourlist = {}
        with open(self.main_dir + "/data/map" + "/colourchange.csv", encoding="utf-8", mode="r") as unitfile:
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
        self.image.blit(self.effectimage, rect)  # add special filter effect that make it look like old map

        textsurface = self.font.render(newterrain[0], True, (0, 0, 0))
        textrect = textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() - (textsurface.get_height() / 2)))
        self.image.blit(textsurface, textrect)


class Previewleader(pygame.sprite.Sprite):
    baseimgposition = [(134, 65), (80, 115), (190, 115), (134, 163)]  # leader image position in command ui

    def __init__(self, leaderid, squadposition, armyposition, leaderstat):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.state = 0
        self.squad = None

        self.squadpos = squadposition  # Squad position is the index of subunit in subunit sprite loop

        self.armyposition = armyposition  # position in the parentunit (e.g. general or sub-general)

        self.imgposition = self.baseimgposition[self.armyposition]  # image position based on armyposition

        self.changeleader(leaderid, leaderstat)

    def changeleader(self, leaderid, leaderstat):
        self.gameid = leaderid  # Different than subunit game id, leadergameid is only used as reference to the id data

        stat = leaderstat.leader_list[leaderid]

        self.name = stat[0]
        self.authority = stat[2]
        self.social = leaderstat.leader_class[stat[7]]
        self.description = stat[-1]

        try:  # Put leader image into leader slot
            self.fullimage = leaderstat.imgs[leaderstat.imgorder.index(leaderid)].copy()
        except:  # Use Unknown leader image if there is none in list
            self.fullimage = leaderstat.imgs[-1].copy()

        self.image = pygame.transform.scale(self.fullimage, (50, 50))
        self.rect = self.image.get_rect(center=self.imgposition)
        self.image_original = self.image.copy()

        self.commander = False  # army commander
        self.originalcommander = False  # the first army commander at the start of battle


class Armybuildslot(pygame.sprite.Sprite):  # TODO change build slot from this class to use sub-unit sprite directly
    squadwidth = 0  # subunit sprite width size get add from main
    squadheight = 0  # subunit sprite height size get add from main
    images = []  # image related to subunit sprite, get add from loadgamedata in gamelongscript
    weaponlist = None
    armourlist = None
    statlist = None

    def __init__(self, gameid, team, armyid, colour, position, startpos):
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.selected = False
        self.gameid = gameid
        self.team = team
        self.armyid = armyid
        self.troopindex = 0
        self.name = "None"
        self.leader = None
        self.height = 100
        self.commander = False
        if self.armyid == 0:
            self.commander = True
        self.authority = 100

        self.coa = pygame.Surface((0, 0))  # empty coa to prevent leader ui error

        self.image = pygame.Surface((self.squadwidth, self.squadheight), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        whiteimage = pygame.Surface((self.squadwidth - 2, self.squadheight - 2))
        whiteimage.fill(colour)
        whiterect = whiteimage.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(whiteimage, whiterect)
        self.image_original = self.image.copy()

        self.armypos = position  # position in parentunit array (0 to 63)
        self.inspposition = (self.armypos[0] + startpos[0], self.armypos[1] + startpos[1])  # position in inspect ui
        self.rect = self.image.get_rect(topleft=self.inspposition)

    def changetroop(self, troopindex, terrain, feature, weather):
        self.image = self.image_original.copy()
        if self.troopindex != troopindex:
            self.troopindex = troopindex
            # self.createtroopstat(self.team, self.statlist.unit_list[troopindex].copy(), [1, 1], 100, 100)

        self.terrain = terrain
        self.feature = feature
        self.weather = weather
        if self.name != "None":
            # v subunit block team colour
            if self.unittype == 2:  # cavalry draw line on block
                pygame.draw.line(self.image, (0, 0, 0), (0, 0), (self.image.get_width(), self.image.get_height()), 2)
            # ^ End subunit block team colour

            # v armour circle colour (grey = light, gold = heavy)
            image1 = self.images[1]
            if self.basearmour <= 50: image1 = self.images[2]
            image1rect = image1.get_rect(center=self.image.get_rect().center)
            self.image.blit(image1, image1rect)
            # ^ End armour colour

            # v health circle image setup
            healthimage = self.images[1]
            healthimagerect = healthimage.get_rect(center=self.image.get_rect().center)
            self.image.blit(healthimage, healthimagerect)
            # ^ End health circle

            # v stamina circle image setup
            staminaimage = self.images[6]
            staminaimagerect = staminaimage.get_rect(center=self.image.get_rect().center)
            self.image.blit(staminaimage, staminaimagerect)
            # ^ End stamina circle

            # v weapon class icon in middle circle
            if self.unitclass == 0:
                image1 = self.weaponlist.imgs[self.weaponlist.weapon_list[self.meleeweapon[0]][-3]]
            else:
                image1 = self.weaponlist.imgs[self.weaponlist.weapon_list[self.rangeweapon[0]][-3]]
            image1rect = image1.get_rect(center=self.image.get_rect().center)
            self.image.blit(image1, image1rect)
            # ^ End weapon icon


class Warningmsg(pygame.sprite.Sprite):
    factionwarn = "Multiple factions subunit will not be usable with No Multiple Faction option enable"
    tenrequire = "Require at least 10 sub-units to be usable"
    emptyrowcol = "Empty row or column will be removed when employed"
    duplicateleader = "Duplicated leader will be removed with No Duplicated leaer option enable"
    leaderwarn = "Leaders from multiple factions subunit will not be usable with No Multiple Faction option enable"
    hardwarn = (tenrequire)
    softwarn = (factionwarn, duplicateleader, leaderwarn, emptyrowcol)

    def __init__(self, pos, image):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("timesnewroman", int(20 * self.heightadjust))
    #
    # def addwarning(self):
    #     self.image = self.image_original.copy()
    #     self.text = text
    #     self.textsurface = self.font.render(text, True, (0, 0, 0))
    #     self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
    #     self.image.blit(self.textsurface, self.textrect)
    #
    #
    # def removewarning(self):
    #
    #     self.image = self.image_original.copy()
    #     self.text = text
    #     self.textsurface = self.font.render(text, True, (0, 0, 0))
    #     self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
    #     self.image.blit(self.textsurface, self.textrect)


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
    def __init__(self, gamebattle, position, gameid, squadlist, colour, leader, leaderpos, coa, startangle, team):
        self = gamelongscript.addarmy(squadlist, position, gameid,
                                      colour, (gamebattle.squadwidth, gamebattle.squadheight), leader + leaderpos, gamebattle.leader_stat,
                                      gamebattle.gameunitstat, True,
                                      coa, False, startangle, 100, 100, team)
