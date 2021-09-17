import ast
import csv
import os

import pygame
import pygame.freetype
from pygame.transform import scale


class PreviewBox(pygame.sprite.Sprite):
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
        with open(self.main_dir + os.path.join("data", "map", "colourchange.csv"), encoding="utf-8", mode="r") as unitfile:
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


class PreviewLeader(pygame.sprite.Sprite):
    baseimgposition = [(134, 185), (80, 235), (190, 235), (134, 283)]  # leader image position in command ui

    def __init__(self, leaderid, subunitpos, armyposition, leaderstat):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.state = 0
        self.subunit = None

        self.leaderid = leaderid

        self.subunitpos = subunitpos  # Squad position is the index of subunit in subunit sprite loop
        self.armyposition = armyposition  # position in the parentunit (e.g. general or sub-general)
        self.imgposition = self.baseimgposition[self.armyposition]  # image position based on armyposition

        self.change_leader(leaderid, leaderstat)

    def change_leader(self, leaderid, leaderstat):
        self.leaderid = leaderid  # leaderid is only used as reference to the leader data

        stat = leaderstat.leader_list[leaderid]
        leader_header = leaderstat.leader_list_header

        self.name = stat[0]
        self.authority = stat[2]
        self.social = leaderstat.leader_class[stat[leader_header["Social Class"]]]
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

    def change_subunit(self, subunit):
        self.subunit = subunit
        if subunit is None:
            self.subunitpos = 0
        else:
            self.subunitpos = subunit.slotnumber


class SelectedPresetBorder(pygame.sprite.Sprite):
    def __init__(self, width, height):
        self._layer = 16
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width + 1, height + 1), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (203, 176, 99), (0, 0, self.image.get_width(), self.image.get_height()), 6)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def changepos(self, pos):
        self.rect = self.image.get_rect(topleft=pos)


class Unitbuildslot(pygame.sprite.Sprite):
    sprite_width = 0  # subunit sprite width size get add from gamestart
    sprite_height = 0  # subunit sprite height size get add from gamestart
    images = []  # image related to subunit sprite, get add from loadgamedata in gamelongscript
    weapon_list = None
    armourlist = None
    stat_list = None
    genre = None

    def __init__(self, gameid, team, armyid, position, startpos, slotnumber, teamcolour):
        self.colour = teamcolour
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.selected = False
        self.gameid = gameid
        self.team = team
        self.armyid = armyid
        self.troopid = 0  # index according to sub-unit file
        self.name = "None"
        self.leader = None
        self.height = 100
        self.commander = False
        if self.armyid == 0:
            self.commander = True
        self.authority = 100
        self.state = 0
        self.ammo_now = 0

        self.terrain = 0
        self.feature = 0
        self.weather = 0

        self.coa = pygame.Surface((0, 0))  # empty coa to prevent leader ui error

        self.changeteam(False)

        self.slotnumber = slotnumber
        self.armypos = position  # position in parentunit sprite
        self.inspposition = (self.armypos[0] + startpos[0], self.armypos[1] + startpos[1])  # position in inspect ui
        self.rect = self.image.get_rect(topleft=self.inspposition)

    def changeteam(self, changetroop):
        self.image = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        whiteimage = pygame.Surface((self.sprite_width - 2, self.sprite_height - 2))
        whiteimage.fill(self.colour[self.team])
        whiterect = whiteimage.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(whiteimage, whiterect)
        self.image_original = self.image.copy()
        if changetroop:
            self.changetroop(self.troopid, self.terrain, self.feature, self.weather)

    def changetroop(self, troopindex, terrain, feature, weather):
        self.image = self.image_original.copy()
        if self.troopid != troopindex:
            self.troopid = troopindex
            self.create_troop_stat(self.stat_list.troop_list[troopindex].copy(), 100, 100, [1, 1])

        self.terrain = terrain
        self.feature = feature
        self.weather = weather
        if self.name != "None":
            # v subunit block team colour
            if self.subunit_type == 2:  # cavalry draw line on block
                pygame.draw.line(self.image, (0, 0, 0), (0, 0), (self.image.get_width(), self.image.get_height()), 2)
            # ^ End subunit block team colour

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
            image1 = self.weapon_list.imgs[self.weapon_list.weapon_list[self.primary_main_weapon[0]][-3]]  # image on subunit sprite
            image1rect = image1.get_rect(center=self.image.get_rect().center)
            self.image.blit(image1, image1rect)
            # ^ End weapon icon


class Warningmsg(pygame.sprite.Sprite):
    eightsubunit_warn = "- Require at least 8 sub-units for both test and employment"
    mainleader_warn = "- Require a gamestart leader for both test and employment"
    emptyrowcol_warn = "- Empty row or column will be removed when employed"
    duplicateleader_warn = "- Duplicated leader will be removed with No Duplicated leaer option enable"
    multifaction_warn = "- Leaders or subunits from multiple factions will not be usable with No Multiple Faction option enable"

    # outofmap_warn = "- There are sub-unit(s) outside of map border, they will retreat when test start"

    def __init__(self, main, pos):
        self.width_adjust = main.width_adjust
        self.height_adjust = main.height_adjust

        self._layer = 18
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("timesnewroman", int(20 * self.height_adjust))
        self.rowcount = 0
        self.warninglog = []
        self.fixwidth = int(230 * self.height_adjust)
        self.pos = pos

    def warning(self, warnlist):
        self.warninglog = []
        self.rowcount = len(warnlist)
        for warnitem in warnlist:
            if len(warnitem) > 25:
                newrow = len(warnitem) / 25
                if newrow.is_integer() is False:
                    newrow = int(newrow) + 1
                else:
                    newrow = int(newrow)
                self.rowcount += newrow

                cutspace = [index for index, letter in enumerate(warnitem) if letter == " "]
                startingindex = 0
                for run in range(1, newrow + 1):
                    textcutnumber = [number for number in cutspace if number <= run * 25]
                    cutnumber = textcutnumber[-1]
                    finaltextoutput = warnitem[startingindex:cutnumber]
                    if run == newrow:
                        finaltextoutput = warnitem[startingindex:]
                    self.warninglog.append(finaltextoutput)
                    startingindex = cutnumber + 1
            else:
                self.warninglog.append(warnitem)

        self.image = pygame.Surface((self.fixwidth, int(22 * self.height_adjust) * self.rowcount))
        self.image.fill((0, 0, 0))
        whiteimage = pygame.Surface((self.fixwidth - 2, (int(22 * self.height_adjust) * self.rowcount) - 2))
        whiteimage.fill((255, 255, 255))
        whiteimage_rect = whiteimage.get_rect(topleft=(1, 1))
        self.image.blit(whiteimage, whiteimage_rect)
        row = 5
        for index, text in enumerate(self.warninglog):
            textsurface = self.font.render(text, True, (0, 0, 0))
            textrect = textsurface.get_rect(topleft=(5, row))
            self.image.blit(textsurface, textrect)
            row += 20  # Whitespace between text row
        self.rect = self.image.get_rect(topleft=self.pos)


class PreviewChangeButton(pygame.sprite.Sprite):
    def __init__(self, main, pos, image, text):
        self.width_adjust = main.width_adjust
        self.height_adjust = main.height_adjust

        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("timesnewroman", int(30 * self.height_adjust))

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


class FilterBox(pygame.sprite.Sprite):
    def __init__(self, main, pos, image):
        self.width_adjust = main.width_adjust
        self.height_adjust = main.height_adjust

        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.width_adjust),
                                                    int(image.get_height() * self.height_adjust)))
        self.rect = self.image.get_rect(topleft=pos)
