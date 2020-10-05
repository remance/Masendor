import csv
import math
import random
from statistics import mean

import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale

from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT


def rotationxy(origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)


class Weaponstat():
    def __init__(self, img):
        """Armour has dmg, penetration and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.weaponlist = {}
        with open(main_dir + "\data\war" + '\\unit_weapon.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.weaponlist[row[0]] = row[1:]
        unitfile.close()
        self.quality = (25, 50, 75, 100, 125, 150, 175)


class Armourstat():
    def __init__(self, img):
        """Armour has base defence and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.armourlist = {}
        with open(main_dir + "\data\war" + '\\unit_armour.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if n == 5:
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                    elif i.isdigit():
                        row[n] = int(i)
                self.armourlist[row[0]] = row[1:]
        unitfile.close()
        self.quality = (25, 50, 75, 100, 125, 150, 175)


class Unitstat():
    def __init__(self):
        """Unit stat data read"""
        self.statuslist = {}
        with open(main_dir + "\data\war" + '\\unit_status.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if (i.isdigit() or "-" in i and n not in (1, 20)):
                        row[n] = int(i)
                    elif i == "":
                        row[n] = 100
                        if n in (2, 3):
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                    # elif i.isdigit(): row[n] = [int(i)]
                self.statuslist[row[0]] = row[1:]
        unitfile.close()
        """Unit grade list"""
        self.gradelist = {}
        with open(main_dir + "\data\war" + '\\unit_grade.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                    if n == 12:
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.gradelist[row[0]] = row[1:]
        unitfile.close()
        self.abilitylist = {}  ## Unit skill list
        with open(main_dir + "\data\war" + '\\unit_ability.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                for n, i in enumerate(row):
                    # print(n, type(n))
                    if run != 0:
                        if n in (2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30):
                            if i == "":
                                row[n] = 100
                            else:
                                row[n] = float(i)
                        elif n in (6, 7, 28, 31):
                            """Convert all condition and status to list"""
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif n == 0:
                            row[n] = int(i)
                run += 1
                self.abilitylist[row[0]] = row[1:]
        unitfile.close()
        """Unit property list"""
        self.traitlist = {}
        with open(main_dir + "\data\war" + '\\unit_property.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if (i.isdigit() or "-" in i) and n not in (1, 34, 35):
                        row[n] = float(i)
                    elif i == "":
                        row[n] = 100
                    if n in (19, 33):
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                    # elif i.isdigit(): row[n] = [int(i)]
                self.traitlist[row[0]] = row[1:]
        unitfile.close()
        """unit role list"""
        self.role = {}
        with open(main_dir + "\data\war" + '\\unit_type.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                self.role[row[0]] = row[1:]
        unitfile.close()
        """unit mount list"""
        self.mountlist = {}
        with open(main_dir + "\data\war" + '\\unit_mount.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if n == 6:
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                    elif i.isdigit(): row[n] = int(i)
                self.mountlist[row[0]] = row[1:]
        unitfile.close()

class Directionarrow(pygame.sprite.Sprite):
    def __init__(self, who):
        """Layer must be called before sprite_init"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = who
        self.pos = self.who.pos
        self.who.directionarrow = self
        self.lengthgap = self.who.image.get_height() / 2
        self.length = self.who.pos.distance_to(self.who.target) + self.lengthgap
        self.previouslength = self.length
        self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        # self.image_original = self.image.copy()
        # pygame.draw.line(self.image, (0, 0, 0), (self.image.get_width()/2, 0),(self.image.get_width()/2,self.image.get_height()), 5)
        self.image = pygame.transform.rotate(self.image, self.who.angle)
        self.rect = self.image.get_rect(midbottom=self.who.allsidepos[0])

    def update(self, who, enmy, squad, hitbox, squadindex, dt):
        self.length = self.who.pos.distance_to(self.who.target) + self.lengthgap
        distance = self.who.allsidepos[0].distance_to(self.who.target) + self.lengthgap
        if self.length != self.previouslength and distance > 2 and self.who.state != 0:
            self.pos = self.who.pos
            self.image = pygame.Surface((5, self.length), pygame.SRCALPHA)
            self.image.fill((0, 0, 0))
            self.image = pygame.transform.rotate(self.image, self.who.angle)
            self.rect = self.image.get_rect(midbottom=self.who.allsidepos[0])
            self.previouslength = self.length
        elif distance < 2 or self.who.state in (0, 10, 11, 100):
            self.who.directionarrow = False
            self.kill()


class Hitbox(pygame.sprite.Sprite):
    maxviewmode = 10

    def __init__(self, who, side, width, height):
        self._layer = 3
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.viewmode = 1
        self.who = who
        self.side = side
        self.collide = 0
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 128))
        self.image_original,self.image_original2 = self.image.copy(), self.image.copy()
        self.image = pygame.transform.rotate(self.image_original, self.who.angle)
        self.oldpos = self.who.hitboxpos[self.side]
        self.rect = self.image.get_rect(center=self.who.hitboxpos[self.side])
        self.pos = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, statuslist, squadgroup, dt, viewmode, playerposlist, enemyposlist):
        if self.viewmode != abs(viewmode - 11):
            self.viewmode = abs(viewmode - 11)
            self.image_original = self.image_original2.copy()
            scalewidth = self.image_original.get_width()
            scaleheight = self.image_original.get_height() * abs(self.viewmode - 11) / self.maxviewmode
            if self.side in (0,3):
                scalewidth = self.image_original.get_width() * abs(self.viewmode - 11) / self.maxviewmode
                scaleheight = self.image_original.get_height()
            self.dim = pygame.Vector2(scalewidth, scaleheight)
            self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
            self.image_original = self.image.copy()
        if self.oldpos != self.who.hitboxpos[self.side]:
            self.image = pygame.transform.rotate(self.image_original, self.who.angle)
            self.rect = self.image.get_rect(center=self.who.hitboxpos[self.side])
            self.pos = self.rect.center
            self.mask = pygame.mask.from_surface(self.image)
            self.oldpos = self.who.hitboxpos[self.side]
        self.collide = 0


class Unitarmy(pygame.sprite.Sprite):
    images = []
    gamemap = None
    gamemapfeature = None
    gamemapheight = None
    maxviewmode = 10

    def __init__(self, startposition, gameid, squadlist, imgsize, colour, control, coa, commander=False, startangle=0):
        # super().__init__()
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        # self.unitarray = unitarray
        self.armysquad = squadlist
        self.colour = colour
        self.commander = commander
        """Alive state array 0 = not exist, 1 = dead, 2 = alive"""
        self.squadalive = np.copy(self.armysquad)
        self.squadalive = np.where(self.squadalive > 0, 2, self.squadalive)
        self.startwhere = []
        self.hitbox = []
        self.squadsprite = []  ##list of squad sprite(not index)
        self.justsplit = False
        self.viewmode = 10
        self.imgsize = imgsize
        self.widthbox, self.heightbox = len(self.armysquad[0]) * self.imgsize[0], len(self.armysquad) * self.imgsize[1]
        self.widthscale, self.heightscale = len(self.armysquad[0]) * self.imgsize[0] * self.viewmode, len(self.armysquad) * self.imgsize[
            1] * self.viewmode
        self.gameid = gameid
        self.control = control
        self.basepos = pygame.Vector2(startposition) ## Basepos is for true pos that is used for ingame calculation
        self.baseattackpos = 0
        self.pos, self.attackpos = self.basepos * abs(self.viewmode - 11), self.baseattackpos * abs(self.viewmode - 11) ## pos is for showing on screen
        self.angle, self.newangle = startangle, startangle
        self.moverotate, self.rotatecal, self.rotatecheck = 0, 0, 0
        self.pause = False
        self.leaderchange = False
        self.directionarrow = False
        self.rotateonly = False
        self.charging = False
        self.forcedmelee = False
        self.forcedmarch = False
        self.changefaction = False
        self.hold = 0  ## 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fireatwill = 0  ## 0 = fire at will, 1 = no fire
        self.retreatstart = 0
        self.retreattimer, self.retreatmax = 0, 0
        self.retreatway = None
        self.combatcheck = 0
        self.rangecombatcheck = 0
        self.attacktarget = 0
        self.neartarget = 0
        self.gotkilled = 0
        self.combatpreparestate = 0
        self.ammo = 0
        self.minrange = 0
        self.maxrange = 0
        self.useminrange = 0
        self.useskillcond = 0
        self.terrain = 0
        self.height = 0
        self.feature = None
        self.sidefeature = []
        self.sideheight = []
        self.getfeature = self.gamemapfeature.getfeature
        self.set_target(startposition)
        self.basepreviousposition = pygame.Vector2(startposition)
        self.previousposition = self.basepreviousposition * abs(self.viewmode - 11)
        self.state = 0  ##  0 = idle, 1 = walking, 2 = running, 3 = attacking/walk, 4 = attacking/walk, 5 = melee combat, 6 = range attack
        self.commandstate = self.state
        self.deadchange = 0
        self.gamestart = False
        self.authrecalnow = False
        self.autosquadplace = True
        self.cansplitrow = False
        if np.array_split(self.armysquad, 2)[0].size > 10 and np.array_split(self.armysquad, 2)[1].size > 10: self.cansplitrow = True
        self.cansplitcol = False
        if np.array_split(self.armysquad, 2, axis=1)[0].size > 10 and np.array_split(self.armysquad, 2, axis=1)[1].size > 10: self.cansplitcol = True
        self.authpenalty = 0
        self.tacticeffect = {}
        self.image = pygame.Surface((self.widthbox, self.heightbox), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 128))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.widthbox, self.heightbox), 2)
        pygame.draw.rect(self.image, self.colour, (1, 1, self.widthbox - 2, self.heightbox - 2))
        self.imagerect = self.images[10].get_rect(center=self.image.get_rect().center)
        self.image.blit(self.images[10], self.imagerect)
        self.healthimage = self.images[0]
        self.healthimagerect = self.healthimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.healthimage, self.healthimagerect)
        self.staminaimage = self.images[5]
        self.staminaimagerect = self.staminaimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.staminaimage, self.staminaimagerect)
        self.coa = coa
        self.imagerect = self.coa.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.coa, self.imagerect)
        self.image_original, self.image_original2, self.image_original3 = self.image.copy(), self.image.copy(), self.image.copy() ## original is for before image get rorated, original2 is for zoom closest, original3 is for zooming
        self.rect = self.image.get_rect(center=startposition)
        self.testangle = math.radians(360 - startangle)
        self.mask = pygame.mask.from_surface(self.image)
        self.offsetx = self.rect.x
        self.offsety = self.rect.y
        self.allsidepos = [(self.basepos[0], (self.basepos[1] - (self.heightbox / 10) / 2)), ## Generate all four side position
                           ((self.basepos[0] - (self.widthbox / 10) / 2), self.basepos[1]),
                           ((self.basepos[0] + (self.widthbox / 10) / 2), self.basepos[1]),
                           (self.basepos[0], (self.basepos[1] + (self.heightbox / 10) / 2))]
        self.allsidepos = [rotationxy(self.basepos, self.allsidepos[0], self.testangle),  ## generate again but with rotation in calculation
                           rotationxy(self.basepos, self.allsidepos[1], self.testangle),
                           rotationxy(self.basepos, self.allsidepos[2], self.testangle),
                           rotationxy(self.basepos, self.allsidepos[3], self.testangle)]
        self.hitboxpos = [(self.rect.center[0], (self.rect.center[1] - self.heightscale / 2)),
                           ((self.rect.center[0] - self.widthscale / 2), self.rect.center[1]),
                           ((self.rect.center[0] + self.widthscale / 2), self.rect.center[1]),
                           (self.rect.center[0], (self.rect.center[1] + self.heightscale / 2))]
        self.hitboxpos = [rotationxy(self.rect.center, self.hitboxpos[0], self.testangle),
                           rotationxy(self.rect.center, self.hitboxpos[1], self.testangle)
            , rotationxy(self.rect.center, self.hitboxpos[2], self.testangle), rotationxy(self.rect.center, self.hitboxpos[3], self.testangle)]
        self.squadpositionlist = []
        self.battleside = [0, 0, 0,
                           0]  ## index of battleside (index of enemy fighting at the side of battalion) and frontline: 0 = front 1 = left 2 =right 3 =rear
        self.frontline = {0: [], 1: [], 2: [], 3: []}  ## frontline keep list of squad at the front of each side in combat
        width, height = 0, 0
        squadnum = 0
        for squad in self.armysquad.flat:  ## Set up squad position list for drawing
            width += self.imgsize[0]
            self.squadpositionlist.append((width, height))
            squadnum += 1
            if squadnum >= len(self.armysquad[0]):
                width = 0
                height += self.imgsize[1]
                squadnum = 0

    def changescale(self):
        scalewidth = self.image_original.get_width() * abs(self.viewmode - 11) / self.maxviewmode
        scaleheight = self.image_original.get_height() * abs(self.viewmode - 11) / self.maxviewmode
        self.widthscale, self.heightscale = len(self.armysquad[0]) * self.imgsize[0] * abs(self.viewmode - 11) / self.maxviewmode, len(self.armysquad) * self.imgsize[
            1] * abs(self.viewmode - 11) / self.maxviewmode
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.rotate()

    def changeposscale(self):
        self.target = self.basetarget * abs(self.viewmode - 11)
        self.previousposition = self.basepreviousposition * abs(self.viewmode - 11)
        self.pos = self.basepos * abs(self.viewmode - 11)
        self.rect = self.image.get_rect(center=self.pos)
        self.attackpos = self.baseattackpos * abs(self.viewmode - 11)
        self.makeallsidepos()

    def recreatesprite(self):
        """redrawing sprite for when split happen since the size will change"""
        self.widthbox, self.heightbox = len(self.armysquad[0]) * self.imgsize[0], len(self.armysquad) * self.imgsize[1]
        self.image = pygame.Surface((self.widthbox, self.heightbox), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 128))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.widthbox, self.heightbox), 2)
        pygame.draw.rect(self.image, self.colour, (1, 1, self.widthbox - 2, self.heightbox - 2))
        self.imagerect = self.images[10].get_rect(center=self.image.get_rect().center)
        self.image.blit(self.images[10], self.imagerect)
        self.healthimage = self.images[0]
        self.healthimagerect = self.healthimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.healthimage, self.healthimagerect)
        self.staminaimage = self.images[5]
        self.staminaimagerect = self.staminaimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.staminaimage, self.staminaimagerect)
        self.imagerect = self.coa.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.coa, self.imagerect)
        self.image_original, self.image_original2, self.image_original3 = self.image.copy(), self.image.copy(), self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.testangle = math.radians(360 - self.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.offsetx = self.rect.x
        self.offsety = self.rect.y
        self.setuparmy()

    def squadtoarmy(self, squads):
        """drawing squad into battalion sprite"""
        squadnum = 0
        truesquadnum = 0
        width, height = 0, 0
        for squad in self.armysquad.flat:
            if squad != 0:
                # def drawtobattalion(self, startposition, battalion):
                # self.rect = self.image.get_rect(topleft=(battalion.image.get_rect(startposition)))
                # self.image.blit(self.image, self.rect)
                self.squadrect = self.squadsprite[truesquadnum].image.copy().get_rect(topleft=(width, height))
                self.image_original.blit(self.squadsprite[truesquadnum].image.copy(), self.squadrect)
                # squad.pos = pygame.Vector2((width,height))
                # squads[self.groupsquadindex[truesquadnum]].drawtobattalion(startposition=(width,height),battalion=self.image)
                # squads[self.groupsquadindex[truesquadnum]].pos = pygame.Vector2(width,height)
                truesquadnum += 1
            width += self.imgsize[0]
            squadnum += 1
            if squadnum >= len(self.armysquad[0]):
                width = 0
                height += self.imgsize[1]
                squadnum = 0

    def setuparmy(self):
        self.stat = {'troop': [], 'stamina': [], 'morale': [], 'speed': [], 'disci': [], 'ammo': [], 'range': [], 'novice': [], 'militant': [],
                     'pro': [], 'vet': [], 'elite': [], 'champ': [], 'hero': [], 'religmili': [], 'religelite': [], 'merc': [], 'noble': []}
        for squad in self.squadsprite:
            self.stat['troop'].append(squad.troopnumber)
            if squad.state != 100:
                self.stat['stamina'].append(squad.stamina)
                self.stat['morale'].append(squad.morale)
                self.stat['speed'].append(squad.speed)
                self.stat['disci'].append(squad.discipline)
                self.stat['ammo'].append(squad.ammo)
                if squad.shootrange > 0:
                    self.stat['range'].append(squad.shootrange)
                squad.combatpos = self.basepos
                squad.useskillcond = self.useskillcond
                if squad.charging == True and self.charging != True:
                    self.charging == True
            # self.stat['speed'].append(squad.troopnumber)
            # self.stat['speed'].append(squad.troopnumber)
            else:
                """Update squad alive list if squad die"""
                deadindex = np.where(self.armysquad == squad.gameid)
                deadindex = [deadindex[0], deadindex[1]]
                if self.squadalive[deadindex[0], deadindex[1]] != 1:
                    self.squadalive[deadindex[0], deadindex[1]] = 1
                    self.deadchange = 1
            # self.squadindex = np.where(self.squadalive > -1, self.armysquad, self.squadalive)
        self.troopnumber = int(sum(self.stat['troop']))
        if self.troopnumber > 0:
            self.stamina = int(mean(self.stat['stamina']))
            self.morale = int(mean(self.stat['morale']))
            self.speed = min(self.stat['speed'])
            self.discipline = mean(self.stat['disci'])
            self.ammo = int(sum(self.stat['ammo']))
            if len(self.stat['range']) > 0:
                self.maxrange = max(self.stat['range'])
                self.minrange = min(self.stat['range'])
        if self.gamestart == False:
            self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 75 / 100), round(
                self.stamina * 50 / 100), round(self.stamina * 25 / 100)
            self.lasthealthstate, self.laststaminastate = 4, 4
            self.maxmorale = self.morale
            self.maxhealth, self.health75, self.health50, self.health25, = self.troopnumber, round(self.troopnumber * 75 / 100), round(
                self.troopnumber * 50 / 100), round(self.troopnumber * 25 / 100)
        self.moralestate = round((self.morale * 100) / self.maxmorale)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)

    def setupfrontline(self, specialcall=False):
        """Setup frontline"""
        gotanother = 0
        startwhere = 0
        whoarray = np.where(self.squadalive > 1, self.armysquad, self.squadalive)
        """rotate the array based on the side being attack"""
        fullwhoarray = [whoarray, np.fliplr(whoarray.swapaxes(0, 1)), np.rot90(whoarray), np.fliplr([whoarray])[0]]
        whoarray = [whoarray[0], fullwhoarray[1][0], fullwhoarray[2][0],
                    fullwhoarray[3][0]]
        for index, whofrontline in enumerate(whoarray):
            if self.gamestart == False and specialcall == False:
                """Add zero to the frontline so it become 8 row array"""
                emptyarray = np.array([0, 0, 0, 0, 0, 0, 0, 0])
                """Adjust the position of frontline to center of empty 8 array"""
                whocenter = (8 - len(whofrontline)) / 2
                if len(whofrontline) == 7:
                    whocenter = random.randint(0, 1)
                elif len(whofrontline) == 5:
                    whocenter = random.randint(1, 2)
                elif len(whofrontline) == 3:
                    whocenter = random.randint(2, 3)
                emptyarray[int(whocenter):int(len(whofrontline) + whocenter)] = whofrontline
                newwhofrontline = emptyarray.copy()
                self.startwhere.append(int(whocenter))
            elif self.gamestart == True or specialcall == True:
                newwhofrontline = whofrontline.copy()
                emptyarray = np.array([0, 0, 0, 0, 0, 0, 0, 0])
                """replace the dead in frontline with other squad in the same column"""
                dead = np.where((newwhofrontline == 0) | (newwhofrontline == 1))
                for deadsquad in dead[0]:
                    run = 0
                    while gotanother == 0:
                        if fullwhoarray[index][run, deadsquad] not in (0, 1):
                            newwhofrontline[deadsquad] = fullwhoarray[index][run, deadsquad]
                            gotanother = 1
                        else:
                            run += 1
                            if len(fullwhoarray[index]) == run:
                                newwhofrontline[deadsquad] = 1  # Only use number 1 for dead squad (0 mean not existed in the first place)
                                gotanother = 1
                    gotanother = 0
                whocenter = self.startwhere[startwhere]
                emptyarray[int(whocenter):int(len(newwhofrontline) + whocenter)] = newwhofrontline
                newwhofrontline = emptyarray.copy()
            startwhere += 1
            # print('whofrontline', whofrontline)
            self.frontline[index] = newwhofrontline
        self.authpenalty = 0
        for squad in self.squadsprite:
            if squad.state != 100:
                self.authpenalty += squad.authpenalty

    # def useskill(self,whichskill):
    #     ##charge skill
    #     skillstat = self.skill[list(self.skill)[0]].copy()
    #     if whichskill == 0:
    #         self.skilleffect[self.chargeskill] = skillstat
    #         if skillstat[26] != 0:
    #             self.statuseffect[self.chargeskill] = skillstat[26]
    #         self.skillcooldown[self.chargeskill] = skillstat[4]
    #     ##other skill
    #     else:
    #         if skillstat[1] == 1:
    #             self.skill[whichskill]
    #         self.skillcooldown[whichskill] = skillstat[4]
    # self.skillcooldown[whichskill] =

    # def receiveskill(self,whichskill):
    #
    # def draw(self,gamescreen):
    #     pygame.draw.rect(gamescreen, (0, 0, 0), self.rect,2)

    def statusupdate(self, statuslist):
        """calculate stat from stamina and morale state"""
        self.moralestate = round((self.morale * 100) / self.maxmorale)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        if self.troopnumber > 0 and self.staminastate != self.laststaminastate:
            self.walkspeed, self.runspeed = (self.speed + self.discipline / 100) / 15, (self.speed + self.discipline / 100) / 10
            self.rotatespeed = round(self.runspeed * 6) / (self.troopnumber / 100)
            if self.rotatespeed > 4: self.rotatespeed = 4
            if self.state in (1, 3, 5):
                self.rotatespeed = round(self.walkspeed * 6) / (self.troopnumber / 100)
                if self.rotatespeed > 3: self.rotatespeed = 3
            if self.rotatespeed < 1:
                self.rotatespeed = 1

    def combatprepare(self, enemyhitbox):
        self.combatpreparestate = 1
        # side, side2 = enemy.allsidepos.copy(), {}
        # for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.allsidepos[0])
        # side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])}
        # self.attackpos = pygame.Vector2(side[list(side2.keys())[0]])
        self.baseattackpos = enemyhitbox.who.allsidepos[enemyhitbox.side]
        self.attackpos = self.baseattackpos * abs(self.viewmode - 11)
        # if list(side2.keys())[0] == 1:
        # self.commandtarget = enemyhitbox.who.allsidepos[enemyhitbox.side]
        # enemyhitbox.who.battleside[enemyhitbox.side] = self.gameid
        # self.battleside[0] = enemyhitbox.who.gameid
        self.set_target(enemyhitbox.who.allsidepos[enemyhitbox.side])

    def makeallsidepos(self):
        """generate all four side position"""
        self.allsidepos = [(self.basepos[0], (self.basepos[1] - (self.heightbox / 10) / 2)),
                       ((self.basepos[0] - (self.widthbox / 10) / 2), self.basepos[1]), ((self.basepos[0] + (self.widthbox / 10) / 2), self.basepos[1]),
                       (self.basepos[0], (self.basepos[1] + (self.heightbox / 10) / 2))]
        self.allsidepos = [rotationxy(self.basepos, self.allsidepos[0], self.testangle),  ## generate again but with rotation in calculation
                       rotationxy(self.basepos, self.allsidepos[1], self.testangle),
                       rotationxy(self.basepos, self.allsidepos[2], self.testangle),
                       rotationxy(self.basepos, self.allsidepos[3], self.testangle)]
        self.hitboxpos = [(self.rect.center[0], (self.rect.center[1] - self.heightscale / 2)),
                          ((self.rect.center[0] - self.widthscale / 2), self.rect.center[1]),
                          ((self.rect.center[0] + self.widthscale / 2), self.rect.center[1]),
                          (self.rect.center[0], (self.rect.center[1] + self.heightscale / 2))]
        self.hitboxpos = [rotationxy(self.rect.center, self.hitboxpos[0], self.testangle),
                          rotationxy(self.rect.center, self.hitboxpos[1], self.testangle)
            , rotationxy(self.rect.center, self.hitboxpos[2], self.testangle), rotationxy(self.rect.center, self.hitboxpos[3], self.testangle)]

    def authrecal(self):
        self.authority = round(
            self.leader[0].authority + (self.leader[1].authority / 3) + (self.leader[2].authority / 3) + (self.leader[3].authority / 5))
        if self.armysquad.size > 20:
            self.authority = round(
                (self.leader[0].authority * (100 - (self.armysquad.size)) / 100) + self.leader[1].authority / 2 + self.leader[2].authority / 2 +
                self.leader[3].authority / 4)

    def startset(self, squadgroup):
        self.setuparmy()
        self.setupfrontline()
        self.setupfrontline(specialcall=True)
        self.oldarmyhealth, self.oldarmystamina = self.troopnumber, self.stamina
        self.rotate()
        self.makeallsidepos()
        self.set_target(self.allsidepos[0])
        self.commandtarget = self.target
        self.spritearray = self.armysquad
        self.leadersocial = self.leader[0].social
        if self.autosquadplace == True:
            for leader in self.leader:
                if leader.gameid != 0:
                    self.squadsprite[leader.squadpos].leader = leader  ## put in leader to squad with the set pos
        self.authrecal()
        self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                            (self.leader[0].cavcommand - 5) * 0.1]
        self.startauth = self.authority
        self.terrain, self.feature = self.getfeature(self.basepos, self.gamemap)
        self.sidefeature = [self.getfeature(self.allsidepos[0], self.gamemap), self.getfeature(self.allsidepos[1], self.gamemap),
                            self.getfeature(self.allsidepos[2], self.gamemap), self.getfeature(self.allsidepos[3], self.gamemap)]
        self.height = self.gamemapheight.getheight(self.basepos)
        self.sideheight = [self.gamemapheight.getheight(self.allsidepos[0]), self.gamemapheight.getheight(self.allsidepos[1]),
                           self.gamemapheight.getheight(self.allsidepos[2]), self.gamemapheight.getheight(self.allsidepos[3])]
        for squad in squadgroup:
            self.spritearray = np.where(self.spritearray == squad.gameid, squad, self.spritearray)
        self.changescale()
        self.changeposscale()

    def viewmodechange(self, squadgroup):
        if self.viewmode != 1:  ## battalion view
            self.image_original = self.image_original3.copy()
            self.changescale()
        elif self.viewmode == 1:  ## Squad view when zoom closest
            self.image_original = self.image_original2.copy()
            self.squadtoarmy(squadgroup)
            self.changescale()
        self.changeposscale()
        self.rotate()

    def update(self, statuslist, squadgroup, dt, viewmode, playerposlist, enemyposlist):
        if self.gamestart == False:
            self.startset(squadgroup)
            self.gamestart = True
        """redraw if troop num or stamina change"""
        if (self.troopnumber != self.oldarmyhealth or self.stamina != self.oldarmystamina) or self.viewmode != abs(viewmode - 11):
            if self.viewmode != abs(viewmode - 11):
                self.viewmode = abs(viewmode - 11)
                self.viewmodechange(squadgroup)
            else:
                """Change health and stamina bar Function"""
                if self.viewmode != 1:
                    if self.oldarmyhealth != self.troopnumber:
                        if self.troopnumber > self.health75:
                            if self.lasthealthstate != 4:
                                self.healthimage = self.images[0]
                                self.image_original3.blit(self.healthimage, self.healthimagerect)
                                self.lasthealthstate = 4
                                self.rotate()
                        elif self.troopnumber > self.health50:
                            if self.lasthealthstate != 3:
                                self.healthimage = self.images[1]
                                self.image_original3.blit(self.healthimage, self.healthimagerect)
                                self.lasthealthstate = 3
                                self.rotate()
                        elif self.troopnumber > self.health25:
                            if self.lasthealthstate != 2:
                                self.healthimage = self.images[2]
                                self.image_original3.blit(self.healthimage, self.healthimagerect)
                                self.lasthealthstate = 2
                                self.rotate()
                        elif self.troopnumber > 0:
                            if self.lasthealthstate != 1:
                                self.healthimage = self.images[3]
                                self.image_original3.blit(self.healthimage, self.healthimagerect)
                                self.lasthealthstate = 1
                                self.rotate()
                        elif self.troopnumber <= 0:
                            if self.lasthealthstate != 0:
                                self.healthimage = self.images[4]
                                self.image_original3.blit(self.healthimage, self.healthimagerect)
                                self.lasthealthstate = 0
                                self.rotate()
                        self.oldarmyhealth = self.troopnumber
                    if self.oldarmystamina != self.stamina:
                        if self.stamina > self.stamina75:
                            if self.laststaminastate != 4:
                                self.staminaimage = self.images[5]
                                self.image_original3.blit(self.staminaimage, self.staminaimagerect)
                                self.laststaminastate = 4
                                self.rotate()
                        elif self.stamina > self.stamina50:
                            if self.laststaminastate != 3:
                                self.staminaimage = self.images[6]
                                self.image_original3.blit(self.staminaimage, self.staminaimagerect)
                                self.laststaminastate = 3
                                self.rotate()
                        elif self.stamina > self.stamina25:
                            if self.laststaminastate != 2:
                                self.staminaimage = self.images[7]
                                self.image_original3.blit(self.staminaimage, self.staminaimagerect)
                                self.laststaminastate = 2
                                self.rotate()
                        elif self.stamina > 0:
                            if self.laststaminastate != 1:
                                self.staminaimage = self.images[8]
                                self.image_original3.blit(self.staminaimage, self.staminaimagerect)
                                self.laststaminastate = 1
                                self.rotate()
                        elif self.stamina <= 0:
                            if self.laststaminastate != 0:
                                self.staminaimage = self.images[9]
                                self.image_original3.blit(self.staminaimage, self.staminaimagerect)
                                self.laststaminastate = 0
                                self.rotate()
                        self.oldarmystamina = self.stamina
                else:
                    self.squadtoarmy(squadgroup)
                    self.rotate()
        if self.state != 100:
            if self.basepos[0] < 0 or self.basepos[0] > 1000 or self.basepos[1] < 0 or self.basepos[1] > 1000: ## remove unit when it go out of battlemap
                self.kill()
                for hitbox in self.hitbox:
                    hitbox.kill()
            self.offsetx = self.rect.x
            self.offsety = self.rect.y
            self.charging = False
            self.setuparmy()
            self.statusupdate(statuslist)
            if self.authrecalnow == True:
                self.authrecal()
                self.authrecalnow = False
            """setup frontline again when any squad die"""
            if self.deadchange == 1:
                self.setupfrontline()
                for squad in self.squadsprite:
                    squad.basemorale -= 10
                self.deadchange = 0
            if self.attacktarget != 0: self.attackpos = self.attacktarget.pos
            """recal stat involve leader if one die"""
            if self.leaderchange == True:
                self.authrecal()
                for leader in self.leader:
                    if leader.gameid != 0:
                        self.squadsprite[leader.squadpos].leader = leader
                self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                                    (self.leader[0].cavcommand - 5) * 0.1]
                self.startauth = self.authority
                self.leaderchange = False
            """near target is enemy that is nearest"""
            thisposlist = enemyposlist.copy()
            if self.gameid >= 2000: thisposlist = playerposlist.copy()
            self.neartarget = {}
            for n, thisside in thisposlist.items(): self.neartarget[n] = pygame.Vector2(thisside).distance_to(self.allsidepos[0])
            self.neartarget = {k: v for k, v in sorted(self.neartarget.items(), key=lambda item: item[1])}
            for n in thisposlist:
                self.neartarget[n] = thisposlist[n]
            if self.battleside != [0, 0, 0, 0]:
                """can not use range attack in melee combat"""
                self.rangecombatcheck = 0
                """enter melee combat state when check"""
                if self.state not in (96, 98, 99):
                    self.state = 10
            if self.rangecombatcheck == 1: self.state = 11
            self.mask = pygame.mask.from_surface(self.image)
            if round(self.morale) <= 20:  ## Retreat state
                self.state = 98
                if self.retreatstart == 0:
                    self.retreatstart = 1
                    self.retreattimer = 0.1
                if self.morale <= 0:  ## Broken state
                    self.morale, self.state = 0, 99
                if 0 not in self.battleside: ## Fight to the death
                    self.state = 10
                    for squad in self.squadsprite:
                        if 9 not in squad.statuseffect:
                            squad.statuseffect[9] = self.gameunitstat.statuslist[9].copy()
                    if random.randint(0, 100) > 99: self.changefaction = True
                """only start retreating when ready"""
                if self.retreattimer > 0:
                    self.retreattimer += dt
                if self.retreatstart == 1 and 0 in self.battleside:
                    retreatside = [hitbox.side for hitbox in self.hitbox if hitbox.collide == 0]
                    self.retreatmax = (4 - len(retreatside)) * 2
                    # print("count", self.retreattimer, self.retreatmax, retreatside)
                    if self.retreattimer >= self.retreatmax:
                        if self.state in (98,99):
                            if self.retreatway is None or self.retreatway[1] not in retreatside:
                                getrandom = random.randint(0, len(retreatside) - 1)
                                self.retreatway = [self.allsidepos[retreatside[getrandom]], retreatside[getrandom]]
                                target = self.basepos + (self.retreatway[0] - self.basepos)
                                if target[0] < self.basepos[0] and target[0] > 0: target[0] *= -100
                                else:target[0] *= 100
                                if target[1] < self.basepos[1] and target[1] > 0: target[1] *= -100
                                else:target[1] *= 100
                                self.set_target(target)
                            self.combatcheck = 0
                        self.retreattimer = self.retreatmax
            elif self.state in (98,99) and self.morale >= 20: ## state become normal again when morale reach 20
                self.state = 0
                self.retreattimer = 0
                self.retreatstart = 0
            if self.hold == 1: ## skirmishing
                minrange = self.minrange
                if minrange == 0: minrange = 100
                if list(self.neartarget.values())[0].distance_to(self.basepos) <= minrange / 5:
                    self.state = 96
                    target = self.basepos - (list(self.neartarget.values())[0] - self.basepos)
                    if target[0] < 0: target[0] = 0
                    elif target[0] > 1000: target[0] = 1000
                    if target[1] < 0: target[1] = 0
                    elif target[1] > 1000: target[1] = 1000
                    self.set_target(target)
            if self.state == 10 and self.battleside == [0, 0, 0, 0] and (
                    self.attacktarget == 0 or (self.attacktarget != 0 and self.attacktarget.state == 100)):
                if self.target == self.allsidepos[0]:
                    self.state = 0
                else: self.state = self.commandstate
                self.attacktarget = 0
            """Rotate Function"""
            if self.angle != round(self.newangle) and self.stamina > 0 and (
                    (self.hitbox[0].collide == 0 and self.hitbox[3].collide == 0) or self.combatpreparestate == 1):
                self.rotatecal = abs(round(self.newangle) - self.angle)
                self.rotatecheck = 360 - self.rotatecal
                self.moverotate = 1
                self.testangle = math.radians(360 - self.angle)
                if self.angle < 0:
                    self.testangle = math.radians(-self.angle)
                ## Rotate logic to continuously rotate based on angle and shortest length
                if round(self.newangle) > self.angle:
                    if self.rotatecal > 180:
                        self.angle -= self.rotatespeed * dt * 50
                        self.rotatecheck -= self.rotatespeed * dt * 50
                        if self.rotatecheck <= 0: self.angle = round(self.newangle)
                    else:
                        self.angle += self.rotatespeed * dt * 50
                        if self.angle >= self.newangle: self.angle = round(self.newangle)
                elif round(self.newangle) < self.angle:
                    if self.rotatecal > 180:
                        self.angle += self.rotatespeed * dt * 50
                        self.rotatecheck -= self.rotatespeed * dt * 50
                        if self.rotatecheck <= 0: self.angle = round(self.newangle)
                    else:
                        self.angle -= self.rotatespeed * dt * 50
                        if self.angle < self.newangle: self.angle = round(self.newangle)
                self.rotate()
                self.makeallsidepos()
            else:
                self.moverotate = 0
                """Can only enter range attack state after finishing rotate"""
                shootrange = self.maxrange
                if self.useminrange == 0:
                    shootrange = self.minrange
                if self.state in (5, 6) and ((self.attacktarget != 0 and self.basepos.distance_to(self.attacktarget.basepos) <= shootrange)
                                             or self.basepos.distance_to(self.baseattackpos) <= shootrange):
                    self.set_target(self.allsidepos[0])
                    self.rangecombatcheck = 1
                elif self.state == 11 and self.attacktarget != 0 and self.basepos.distance_to(
                        self.attacktarget.basepos) > shootrange and self.hold == 0:  ## chase target if it go out of range and hold condition not hold
                    self.state = self.commandstate
                    self.rangecombatcheck = 0
                    self.set_target(self.attacktarget.basepos)
                    self.setrotate(self.target, instant=True)
            """Move Function"""
            if self.allsidepos[0] != self.basetarget and self.rangecombatcheck != 1:
                # """Setup target to move to give target position, this can be changed in move fuction (i.e. stopped due to fight and resume moving after finish fight)"""
                # if self.state not in [10]: self.target = self.commandtarget
                if self.state in (0, 3, 4, 5,6,10) and self.attacktarget != 0 \
                        and self.basetarget != self.attacktarget.basepos and self.hold == 0:  ## Chase target and rotate accordingly
                    cantchase = False
                    for hitbox in self.hitbox:
                        if hitbox.collide != 0: cantchase = True
                    if cantchase == False and self.forcedmelee == True:
                        self.state = self.commandstate
                        self.set_target(self.attacktarget.basepos)
                        self.setrotate(self.target, instant=True)
                """check for hitbox collide according to which ever closest to the target position"""
                if self.state not in (0, 97) and self.stamina > 0 and (self.retreattimer == 0 or self.retreattimer >= self.retreatmax):
                    side, side2 = self.allsidepos.copy(), {}
                    for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.basetarget)
                    side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])}
                    if ((self.hitbox[list(side2.keys())[0]].collide == 0 and self.hitbox[list(side2.keys())[1]].collide == 0) or self.combatpreparestate == 1) \
                            and self.moverotate == 0 and self.rotateonly != True:
                        self.pause = False
                        move = self.basetarget - self.allsidepos[0]
                        move_length = move.length()
                        if move_length < 0.1 and self.battleside == [0, 0, 0,
                                0] and self.attacktarget == 0 and self.rangecombatcheck == 0:
                            """Stop moving when reach target and go to idle"""
                            self.allsidepos[0] = self.commandtarget
                            self.state = 0
                            self.commandstate = self.state
                        # if self.state == 5: self.target = self.pos
                        elif move_length > 0.1:
                            # if self.state != 3 and self.retreatcommand == 1:
                            heightdiff = (self.height / self.sideheight[0]) ** 2
                            if self.state in (96,98,99):
                                heightdiff = (self.height / self.sideheight[list(side2.keys())[0]]) ** 2
                            move.normalize_ip()
                            if self.state in (2, 4, 6, 96, 98, 99):
                                move = move * self.runspeed * heightdiff * dt
                            elif self.state in (1, 3, 5):
                                move = move * self.walkspeed * heightdiff * dt
                            elif self.state == 10:
                                move =  move * 3 * heightdiff * dt
                            if move.length() > move_length:
                                move = self.basetarget - self.allsidepos[0]
                                move.normalize_ip()
                            self.basepos += move
                            self.pos = self.basepos * abs(self.viewmode - 11)
                        self.rect.center = list(int(v) for v in self.pos)
                        self.terrain, self.feature = self.getfeature(self.basepos, self.gamemap)
                        self.height = self.gamemapheight.getheight(self.basepos)
                        self.makeallsidepos()
                        self.sidefeature = [self.getfeature(self.allsidepos[0], self.gamemap), self.getfeature(self.allsidepos[1], self.gamemap),
                                            self.getfeature(self.allsidepos[2], self.gamemap), self.getfeature(self.allsidepos[3], self.gamemap)]
                        self.sideheight = [self.gamemapheight.getheight(self.allsidepos[0]), self.gamemapheight.getheight(self.allsidepos[1]),
                                           self.gamemapheight.getheight(self.allsidepos[2]), self.gamemapheight.getheight(self.allsidepos[3])]
                    elif (self.hitbox[
                              list(side2.keys())[0]].collide != 0 and self.combatpreparestate == 0) and self.moverotate == 0 and self.rotateonly != True:
                        self.pause = True
                    elif self.moverotate == 0 and self.rotateonly == True:
                        self.state = 0
                        self.commandstate = self.state
                        self.set_target(self.allsidepos[0])
                        self.commandtarget = self.target
                        self.rotateonly = False
                        self.makeallsidepos()
                        self.sidefeature = [self.getfeature(self.allsidepos[0], self.gamemap), self.getfeature(self.allsidepos[1], self.gamemap),
                                            self.getfeature(self.allsidepos[2], self.gamemap), self.getfeature(self.allsidepos[3], self.gamemap)]
                        self.sideheight = [self.gamemapheight.getheight(self.allsidepos[0]), self.gamemapheight.getheight(self.allsidepos[1]),
                                           self.gamemapheight.getheight(self.allsidepos[2]), self.gamemapheight.getheight(self.allsidepos[3])]
            if self.stamina <= 0:
                self.state = 97
                self.set_target(self.allsidepos[0])
                # self.target = self.allsidepos[0]
                self.rangecombatcheck = 0
            if self.state == 97 and self.stamina > 1000: self.state = 0
            if self.battleside == [0, 0, 0, 0] and self.hold == 0 and self.attacktarget == 0:
                self.combatpreparestate = 0
            self.battleside = [0, 0, 0, 0]
            if self.troopnumber <= 0:
                self.stamina, self.morale, self.speed, self.discipline = 0, 0, 0, 0
                for leader in self.leader:
                    if leader.state not in (96, 97, 98, 100):  ## leader get captured/flee/die when squad destroyed
                        leader.state = 96
                        for hitbox in self.hitbox:
                            if hitbox.collide != 0 and random.randint(0, 1) == 0:
                                leader.state = 97
                                if random.randint(0, 1) == 0:
                                    leader.state = 100
                self.state = 100
            # self.rect.topleft = self.pos[0],self.pos[1]

    def set_target(self, pos):
        self.basetarget = pygame.Vector2(pos)
        self.target = self.basetarget * abs(self.viewmode - 11)
        # print(self.target)

    def rotate(self):
        # Rotate the image.
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        # Rotate the offset vector.
        # offset_rotated = self.offset.rotate(self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=self.pos)  # +offset_rotated)

    def setrotate(self, settarget=0, instant=False):
        self.previousposition = [self.rect.centerx, self.rect.centery]
        if settarget == 0:
            myradians = math.atan2(self.commandtarget[1] - self.previousposition[1], self.commandtarget[0] - self.previousposition[0])
        else:
            myradians = math.atan2(settarget[1] - self.previousposition[1], settarget[0] - self.previousposition[0])
        self.newangle = math.degrees(myradians)
        # """upper left -"""
        if self.newangle >= -180 and self.newangle <= -90:
            self.newangle = -self.newangle - 90
        # """upper right +"""
        elif self.newangle > -90 and self.newangle < 0:
            self.newangle = (-self.newangle) - 90
        # """lower right -"""
        elif self.newangle >= 0 and self.newangle <= 90:
            self.newangle = -(self.newangle + 90)
        # """lower left +"""
        elif self.newangle > 90 and self.newangle <= 180:
            self.newangle = 270 - self.newangle
        if instant == True:
            self.rotate()

    def processcommand(self, mouse_pos, mouse_up, mouse_right, double_mouse_right, whomouseover, enemyposlist, keystate):
        self.state = 1
        self.rotateonly = False
        self.forcedmelee = False
        self.attacktarget = 0
        self.baseattackpos = 0
        self.attackpos = 0
        if keystate[pygame.K_LALT] == True or (whomouseover != 0 and (
                (self.gameid < 2000 and whomouseover.gameid >= 2000) or (self.gameid >= 2000 and whomouseover.gameid < 2000))):
            if self.ammo <= 0 or keystate[pygame.K_LCTRL] == True:
                self.state = 3
            elif self.ammo > 0:  ##Move to range attack
                self.state = 5
            if keystate[pygame.K_LALT] == True:
                self.set_target(mouse_pos[1])
            else:
                self.attacktarget = whomouseover
                self.baseattackpos = whomouseover.basepos
        if double_mouse_right:
            self.state += 1
        self.commandstate = self.state
        self.rangecombatcheck = 0
        if keystate[pygame.K_LSHIFT] == True: self.rotateonly = True
        self.set_target(mouse_pos[1])
        self.commandtarget = self.target
        self.setrotate()
        if self.charging == True:
            self.leader[0].authority -= self.authpenalty
            self.authrecal()

    def processretreat(self, mouse_pos, mouse_up, mouse_right, double_mouse_right, whomouseover, enemyposlist, keystate):
        if whomouseover == 0:
            self.state = 96
            self.commandstate = self.state
            if self.retreattimer == 0:
                self.leader[0].authority -= self.authpenalty
                self.authrecal()
                self.retreattimer = 0.1
                self.retreatstart = 1
            self.set_target(mouse_pos[1])
            self.commandtarget = self.target
            self.combatpreparestate = 0

    def command(self, mouse_pos, mouse_up, mouse_right, double_mouse_right, whomouseover, enemyposlist, keystate, othercommand=0):
        """othercommand is special type of command such as stop all action, raise flag, decimation, duel and so on"""
        if self.control == True and self.state != 100:
            """check if right click in mask or not. if not, move unit"""
            posmask = mouse_pos[0][0] - self.rect.x, mouse_pos[0][1] - self.rect.y
            if mouse_right and mouse_pos[1][0] >= 0 and mouse_pos[1][0] <= 1000 and mouse_pos[1][1] >= 0 and mouse_pos[1][1] <= 1000:
                if self.state not in (10, 97, 98, 99, 100):
                    try:  ## if click within rect but not in mask
                        if self.mask.get_at(posmask) == 0:
                            self.processcommand(mouse_pos, mouse_up, mouse_right, double_mouse_right, whomouseover, enemyposlist, keystate)
                    except:  ## if click outside of rect and mask
                        self.processcommand(mouse_pos, mouse_up, mouse_right, double_mouse_right, whomouseover, enemyposlist, keystate)
                elif self.state == 10:  ##Enter Fall back state if in combat and move command issue
                    try:
                        if self.mask.get_at(posmask) == 0:
                            self.processretreat(mouse_pos, mouse_up, mouse_right, double_mouse_right, whomouseover, enemyposlist, keystate)
                    except:
                        self.processretreat(mouse_pos, mouse_up, mouse_right, double_mouse_right, whomouseover, enemyposlist, keystate)
                            # self.combatcheck = 0
            elif othercommand == 1 and self.state not in (10,96,97,98,99,100):  ## Pause all action except combat
                if self.charging == True:
                    self.leader[0].authority -= self.authpenalty
                    self.authrecal()
                self.state = 0
                self.commandstate = self.state
                self.set_target(self.allsidepos[0])
                self.commandtarget = self.target
                self.rangecombatcheck = 0
                self.setrotate()


class Deadarmy(pygame.sprite.Sprite):
    def __init__(self):
        # super().__init__()
        pygame.sprite.Sprite.__init__(self, self.containers)

    # def command(self, mouse_pos, mouse_up, wholastselect):
    #     self.wholastselect = wholastselect
    #     self.rect = self.rect.clamp(SCREENRECT)
    #     if self.rect.collidepoint(mouse_pos):
    #         self.mouse_over = True
    #         self.whomouseover = self.gameid
    #         if mouse_up:
    #             self.selected = True
    #             self.wholastselect = self.gameid
    # self.image = self.images[2] 100))
