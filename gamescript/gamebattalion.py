import math
import random

import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale

from gamescript import gamelongscript

def rotationxy(origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)

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

    def update(self, viewmode):
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
        self.clickimage = self.image.copy()
        self.clickimage.fill((0, 0, 0, 128))
        self.notclickimage = self.image.copy()
        self.image_original, self.image_original2 = self.image.copy(), self.image.copy()
        self.image = pygame.transform.rotate(self.image_original, self.who.angle)
        self.oldpos = self.who.hitboxpos[self.side]
        self.rect = self.image.get_rect(center=self.who.hitboxpos[self.side])
        self.pos = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)
        self.clickcheck = False
        self.stillclick = False

    def update(self, viewmode):
        if self.viewmode != abs(viewmode - 11) or self.clickcheck:
            self.viewmode = abs(viewmode - 11)
            self.image_original = self.image_original2.copy()
            scalewidth = self.image_original.get_width()
            scaleheight = self.image_original.get_height() * abs(self.viewmode - 11) / self.maxviewmode
            if self.side in (0, 3):
                scalewidth = self.image_original.get_width() * abs(self.viewmode - 11) / self.maxviewmode
                scaleheight = self.image_original.get_height()
            self.dim = pygame.Vector2(scalewidth, scaleheight)
            self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
            self.mask = pygame.mask.from_surface(self.image)
            self.image_original = self.image.copy()
        if self.oldpos != self.who.hitboxpos[self.side] or self.clickcheck:
            self.image = pygame.transform.rotate(self.image_original, self.who.angle)
            self.rect = self.image.get_rect(center=self.who.hitboxpos[self.side])
            self.pos = self.rect.center
            self.mask = pygame.mask.from_surface(self.image)
            self.oldpos = self.who.hitboxpos[self.side]
        self.collide = 0

    def clicked(self):
        self.image_original2 = self.clickimage.copy()
        self.clickcheck = True
        self.update(abs(11 - self.viewmode))
        self.clickcheck = False
        self.stillclick = True

    def release(self):
        self.image_original2 = self.notclickimage.copy()
        self.clickcheck = True
        self.update(abs(11 - self.viewmode))
        self.clickcheck = False
        self.stillclick = False


class Unitarmy(pygame.sprite.Sprite):
    images = []
    gamemap = None
    gamemapfeature = None
    gamemapheight = None
    statuslist = None
    maxviewmode = 10
    maingame = None
    squadcombatcal = gamelongscript.squadcombatcal
    die = gamelongscript.die

    def __init__(self, startposition, gameid, squadlist, imgsize, colour, control, coa, commander=False, startangle=0):
        """Although battalion in code, this is referred as unit ingame"""
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
        self.icon = None  ## for linking with army selection ui, got linked when icon created in gameui.Armyicon
        self.justsplit = False
        self.viewmode = 10
        self.imgsize = imgsize
        self.widthbox, self.heightbox = len(self.armysquad[0]) * self.imgsize[0], len(self.armysquad) * self.imgsize[1]
        self.widthscale, self.heightscale = len(self.armysquad[0]) * self.imgsize[0] * self.viewmode, len(self.armysquad) * self.imgsize[
            1] * self.viewmode
        self.gameid = gameid
        self.control = control
        self.basepos = pygame.Vector2(startposition)  ## Basepos is for true pos that is used for ingame calculation
        self.baseattackpos = 0
        self.pos, self.attackpos = self.basepos * abs(self.viewmode - 11), self.baseattackpos * abs(
            self.viewmode - 11)  ## pos is for showing on screen
        self.angle = startangle
        self.newangle = self.angle
        self.moverotate, self.rotatecal, self.rotatecheck = 0, 0, 0
        self.walk = False
        self.run = False
        self.leaderchange = False
        self.directionarrow = False
        self.rotateonly = False
        self.charging = False
        self.forcedmelee = False
        self.forcedmarch = False
        self.changefaction = False
        self.brokenlimit = 50
        self.hold = 0  ## 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fireatwill = 0  ## 0 = fire at will, 1 = no fire
        self.retreatstart = 0
        self.retreattimer, self.retreatmax = 0, 0
        self.retreatway = None
        self.rangecombatcheck = 0
        self.attacktarget = 0
        self.neartarget = {}
        self.gotkilled = 0
        self.combatpreparestate = 0
        self.stopcombatmove = False
        self.troopnumber = 0
        self.stamina = 0
        self.morale = 0
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
        self.deadchange = False
        self.timer = random.random()
        self.squadimgchange = []
        self.zoomviewchange = False
        self.gamestart = False
        self.authrecalnow = False
        self.autosquadplace = True
        self.cansplitrow = False
        self.revert = False
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
        self.healthimagerect = self.images[0].get_rect(center=self.image.get_rect().center)
        self.image.blit(self.images[0], self.healthimagerect)
        self.staminaimagerect = self.images[5].get_rect(center=self.image.get_rect().center)
        self.image.blit(self.images[5], self.staminaimagerect)
        self.coa = coa
        self.faction = self.coa
        self.imagerect = self.coa.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.coa, self.imagerect)
        self.image_original, self.image_original2, self.image_original3 = self.image.copy(), self.image.copy(), self.image.copy()  ## original is for before image get rorated, original2 is for zoom closest, original3 is for zooming
        self.rect = self.image.get_rect(center=startposition)
        self.testangle = math.radians(360 - startangle)
        self.mask = pygame.mask.from_surface(self.image)
        self.offsetx = self.rect.x
        self.offsety = self.rect.y
        self.allsidepos = [(self.basepos[0], (self.basepos[1] - (self.heightbox / 10) / 2)),  ## Generate all four side position
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
        self.battleside = [None, None, None, None] #battleside with enemy sprite
        self.battlesideid = [0,0,0,0]  # index of battleside (index of enemy fighting at the side of battalion) and frontline: 0 = front 1 = left 2 =right 3 =rear
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
        self.widthscale, self.heightscale = len(self.armysquad[0]) * self.imgsize[0] * abs(self.viewmode - 11) / self.maxviewmode, len(
            self.armysquad) * self.imgsize[
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

    def squadtoarmy(self):
        """drawing squad into battalion sprite"""
        squadnum = 0
        truesquadnum = 0
        width, height = 0, 0
        for squad in self.armysquad.flat:
            if squad != 0:
                if self.zoomviewchange == True or squad in self.squadimgchange:
                    self.squadrect = self.squadsprite[truesquadnum].image.copy().get_rect(topleft=(width, height))
                    self.image_original.blit(self.squadsprite[truesquadnum].image.copy(), self.squadrect)
                truesquadnum += 1
            width += self.imgsize[0]
            squadnum += 1
            if squadnum >= len(self.armysquad[0]):
                width = 0
                height += self.imgsize[1]
                squadnum = 0

    def setuparmy(self):
        self.troopnumber = 0
        self.stamina = 0
        self.morale = 0
        allspeed = []
        self.ammo = 0
        howmany = 0
        allshootrange = []
        for squad in self.squadsprite:
            if squad.state != 100:
                self.troopnumber += squad.troopnumber
                self.stamina += squad.stamina
                self.morale += squad.morale
                allspeed.append(squad.speed)
                self.ammo += squad.ammo
                if squad.shootrange > 0:
                    allshootrange.append(squad.shootrange)
                squad.combatpos = self.basepos # Squad pos same as battalion pos (for now)
                squad.useskillcond = self.useskillcond
                squad.attacktarget = self.attacktarget
                squad.attackpos = self.baseattackpos
                if self.attacktarget != 0:
                    squad.attackpos = self.attacktarget.basepos
                if squad.charging and self.charging == False:
                    self.charging = True
                howmany += 1
        if self.troopnumber > 0:
            self.stamina = int(self.stamina/howmany)
            self.morale = int(self.morale/howmany)
            self.speed = min(allspeed)
            self.walkspeed, self.runspeed = self.speed / 15, self.speed / 10
            if len(allshootrange) > 0:
                self.maxrange = max(allshootrange)
                self.minrange = min(allshootrange)
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
            elif self.gamestart or specialcall:
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

    def combatprepare(self, enemyhitbox):
        print(self.gameid)
        self.stopcombatmove = False
        self.combatpreparestate = 1
        # side, side2 = enemy.allsidepos.copy(), {}
        # for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.allsidepos[0])
        # side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])}
        # self.attackpos = pygame.Vector2(side[list(side2.keys())[0]])
        self.attacktarget = enemyhitbox.who
        self.baseattackpos = self.attacktarget.allsidepos[enemyhitbox.side]
        self.attackpos = self.baseattackpos * abs(self.viewmode - 11)
        if enemyhitbox.side == 0:
            self.attacktarget.attacktarget = self
        else:
            if self.attacktarget.state not in (96,97,98,99):
                self.attacktarget.set_target(self.attacktarget.allsidepos[0]) ## stop moving when get hit
        # if list(side2.keys())[0] == 1:
        # self.commandtarget = enemyhitbox.who.allsidepos[enemyhitbox.side]
        # enemyhitbox.who.battleside[enemyhitbox.side] = self.gameid
        # self.battleside[0] = enemyhitbox.who.gameid
        self.set_target(enemyhitbox.who.allsidepos[enemyhitbox.side])

    def makeallsidepos(self):
        """generate all four side position"""
        self.allsidepos = [(self.basepos[0], (self.basepos[1] - (self.heightbox / 10) / 2)),
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

    def authrecal(self):
        self.authority = int(
            self.leader[0].authority + (self.leader[1].authority / 3) + (self.leader[2].authority / 3) + (self.leader[3].authority / 5))
        bigarmysize = self.armysquad > 0
        bigarmysize = bigarmysize.sum()
        if bigarmysize > 20:
            self.authority = int(
                (self.leader[0].authority * (100 - (bigarmysize)) / 100) + self.leader[1].authority / 2 + self.leader[2].authority / 2 +
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
        if self.autosquadplace:
            for leader in self.leader:
                if leader.gameid != 1:
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

    def viewmodechange(self):
        if self.viewmode != 1:  ## battalion view
            self.image_original = self.image_original3.copy()
            self.changescale()
        elif self.viewmode == 1:  ## Squad view when zoom closest (10 in other class without need zoom image)
            self.image_original = self.image_original2.copy()
            self.squadtoarmy()
            self.changescale()
        self.changeposscale()
        self.rotate()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, weather, squadgroup, dt, viewmode, mousepos, mouseup):
        if self.gamestart == False:
            self.startset(squadgroup)
            self.gamestart = True
        """redraw if troop num or stamina change"""
        if self.troopnumber != self.oldarmyhealth or self.stamina != self.oldarmystamina or self.viewmode != abs(viewmode - 11):
            if self.viewmode != abs(viewmode - 11):
                self.zoomviewchange = True
                self.viewmode = abs(viewmode - 11)
                self.viewmodechange()
            """Change health and stamina bar Function"""
            if self.viewmode != 1:
                if self.oldarmyhealth != self.troopnumber:
                    healthlist = (self.health75, self.health50, self.health25, 0, -1)
                    for index, health in enumerate(healthlist): ## Loop to find appropiate hp circle image
                        if self.troopnumber > health:
                            if self.lasthealthstate != abs(4 - index):
                                self.image_original3.blit(self.images[index], self.healthimagerect)
                                self.lasthealthstate = abs(4 - index)
                                self.viewmodechange()
                            break
                    self.oldarmyhealth = self.troopnumber
                if self.oldarmystamina != self.stamina:
                    staminalist = (self.stamina75, self.stamina50, self.stamina25, 0, -1)
                    for index, stamina in enumerate(staminalist): ## Loop to find appropiate stamina circle image
                        if self.stamina > stamina:
                            if self.laststaminastate != abs(4 - index):
                                if index != 3:
                                    self.image_original3.blit(self.images[index + 5], self.staminaimagerect)
                                    self.laststaminastate = abs(4 - index)
                                    self.viewmodechange()
                                else:
                                    if self.state != 97:
                                        self.image_original3.blit(self.images[8], self.staminaimagerect)
                                        self.laststaminastate = 1
                                        self.viewmodechange()
                            break
                    self.oldarmystamina = self.stamina
            else:
                if self.squadimgchange != [] or self.zoomviewchange == True:
                    self.squadtoarmy()
                    self.rotate()
                    self.squadimgchange = []
                    self.zoomviewchange = False
        if self.state != 100:
            if self.gameid < 2000:
                self.maingame.playerposlist[self.gameid] = self.basepos
                thisposlist = self.maingame.enemyposlist
            else:
                self.maingame.enemyposlist[self.gameid] = self.basepos
                thisposlist = self.maingame.playerposlist
            ## Mouse collision detect
            if self.rect.collidepoint(mousepos):
                posmask = int(mousepos[0] - self.rect.x), int(mousepos[1] - self.rect.y)
                try:
                    if self.mask.get_at(posmask) == 1:
                        self.maingame.lastmouseover = self
                        if mouseup and self.maingame.uicheck == 0:
                            self.maingame.lastselected = self
                            for hitbox in self.hitbox:
                                hitbox.clicked()
                            if self.maingame.beforeselected is not None and self.maingame.beforeselected != self:
                                for hitbox in self.maingame.beforeselected.hitbox:
                                    hitbox.release()
                            self.maingame.clickcheck = 1
                except: pass
            ## ^ End mouse detect
            self.offsetx = self.rect.x
            self.offsety = self.rect.y
            self.charging = False
            self.walk = False
            self.run = False
            if dt > 0: # Set timer for complex calculation that cannot happen every loop as it drop too much fps
                self.timer += dt
                if self.timer >= 1:
                    self.setuparmy()
                    ## Find near enemy target
                    self.neartarget = {}  # Near target is enemy that is nearest
                    for n, thisside in thisposlist.items():
                        self.neartarget[n] = pygame.Vector2(thisside).distance_to(self.basepos)
                    self.neartarget = {k: v for k, v in sorted(self.neartarget.items(), key=lambda item: item[1])}
                    for n in thisposlist:
                        self.neartarget[n] = thisposlist[n]  ## change back near target list value to vector with sorted order
                    ## ^ End find near target
                    self.timer -= 1
            if self.authrecalnow:
                self.authrecal()
                self.authrecalnow = False
            # Setup frontline again when any squad die
            if self.deadchange == True:
                self.setupfrontline()
                for squad in self.squadsprite:
                    squad.basemorale -= 30
                self.deadchange = False
            # ^End setup frontline when squad die
            ## Combat and unit update
            self.battleside = [None, None, None, None]
            self.battlesideid = [0, 0, 0, 0]
            for hitbox in self.hitbox:
                collidelist = pygame.sprite.spritecollide(hitbox, self.maingame.hitboxes, dokill=False, collided=pygame.sprite.collide_mask)
                for hitbox2 in collidelist:
                    if self.faction != hitbox2.who.faction:
                        hitbox.collide, hitbox2.collide = hitbox2.who.gameid, self.gameid
                        """run combatprepare when combat start if army is the attacker"""
                        self.battleside[hitbox.side] = hitbox2.who
                        self.battlesideid[hitbox.side] = hitbox2.who.gameid
                        hitbox2.who.battleside[hitbox2.side] = self
                        hitbox2.who.battlesideid[hitbox2.side] = self.gameid
                        """set up army position to the enemyside"""
                        if self.combatpreparestate == 0 and hitbox.side == 0 and hitbox2.who.combatpreparestate == 0 and self.state in (1, 2, 3, 4, 5, 6):
                            self.combatprepare(hitbox2)
                    elif self.gameid != hitbox2.who.gameid:  ##colide battalion in same faction
                        hitbox.collide, hitbox2.collide = hitbox2.who.gameid, hitbox.who.gameid
            for index, battle in enumerate(self.battleside):
                if battle is not None:
                    self.squadcombatcal(self.maingame.squad, self.maingame.squadindexlist, battle, index,
                                        battle.battlesideid.index(self.gameid))
            ## ^End combat update
            if self.attacktarget != 0: self.baseattackpos = self.attacktarget.basepos
            self.attackpos = self.baseattackpos * abs(self.viewmode - 11)
            ## Recal stat involve leader if one die
            if self.leaderchange:
                self.authrecal()
                for leader in self.leader:
                    if leader.gameid != 0:
                        self.squadsprite[leader.squadpos].leader = leader
                self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                                    (self.leader[0].cavcommand - 5) * 0.1]
                self.startauth = self.authority
                self.leaderchange = False
            ## ^End recal stat when leader die
            if self.battlesideid != [0,0,0,0]:
                self.rangecombatcheck = 0 # can not use range attack in melee combat
                """enter melee combat state when check"""
                if self.state not in (96, 98, 99):
                    self.state = 10
            if self.rangecombatcheck == 1: self.state = 11
            # Retreat function
            if round(self.morale) <= 20 and self.state != 97:  ## Retreat state when morale lower than 20
                self.state = 98
                if self.retreatstart == 0:
                    self.retreatstart = 1
                    self.retreattimer = 0.1
                if self.morale <= 10:  ## Broken state
                    self.morale, self.state = 0, 99
                if 0 not in self.battlesideid:  ## Fight to the death
                    self.state = 10
                    for squad in self.squadsprite:
                        if 9 not in squad.statuseffect:
                            squad.statuseffect[9] = self.statuslist[9].copy()
                    if random.randint(0, 100) > 99: ## change side via surrender or betrayal
                        if self.gameid < 2000:
                            self.maingame.allunitindex = self.switchfaction(self.maingame.playerarmy, self.maingame.enemyarmy,
                                                                            self.maingame.playerposlist, self.maingame.allunitindex, self.maingame.enactment)
                        else:
                            self.maingame.allunitindex = self.switchfaction(self.maingame.enemyarmy, self.maingame.playerarmy,
                                                                            self.maingame.enemyposlist, self.maingame.allunitindex, self.maingame.enactment)
                        self.maingame.eventlog.addlog([0, str(self.leader[0].name) + "'s battalion surrender"], [0, 1])
                        self.maingame.setuparmyicon()
            elif self.state == 98 and self.morale >= self.brokenlimit/2:  # quit retreat when morale reach increasing limit
                self.state = 0
                self.retreattimer = 0
                self.retreatstart = 0
                self.retreatway = None
                self.set_target(self.basepos)
                self.brokenlimit += random.randint(1,10)
            elif self.state == 99 and self.morale >= self.brokenlimit: # quit broken when morale reach increasing limit
                self.state = 0
                self.retreattimer = 0
                self.retreatstart = 0
                self.retreatway = None
                self.set_target(self.basepos)
                self.brokenlimit += random.randint(5,15)
            """only start retreating when ready"""
            if self.retreattimer > 0:
                self.retreattimer += dt
            if self.retreatstart == 1 and 0 in self.battlesideid:
                retreatside = [hitbox.side for hitbox in self.hitbox if hitbox.collide == 0]
                self.retreatmax = (4 - len(retreatside)) * 2
                if self.retreattimer >= self.retreatmax:
                    if self.state in (98, 99):
                        if self.retreatway is None or self.retreatway[1] not in retreatside:
                            if 3 in retreatside: # prioritise rear retreat
                                self.retreatway = [self.allsidepos[3], 3]
                            else:
                                getrandom = random.randint(0, len(retreatside) - 1)
                                self.retreatway = [self.allsidepos[retreatside[getrandom]], retreatside[getrandom]]
                            target = self.basepos + ((self.retreatway[0] - self.basepos)*100)
                            self.set_target(target)
                        self.combatpreparestate = 0
                    self.retreattimer = self.retreatmax
            if self.hold == 1 and self.state not in (97,98,99):  ## skirmishing
                minrange = self.minrange
                if minrange < 50: minrange = 50
                if list(self.neartarget.values())[0].distance_to(self.basepos) <= minrange:
                    self.state = 96
                    target = self.basepos - (list(self.neartarget.values())[0] - self.basepos)
                    if target[0] < 1:
                        target[0] = 1
                    elif target[0] > 998:
                        target[0] = 998
                    if target[1] < 1:
                        target[1] = 1
                    elif target[1] > 998:
                        target[1] = 998
                    self.set_target(target)
            if self.state == 10 and self.battlesideid == [0,0,0,0]: # Fight state but no collided enemy
                if self.nocombat > 0:  # For avoiding battalion bobble between two collided enemy
                    self.nocombat += dt
                    if self.nocombat > 1:
                        self.nocombat = 0
                        self.combatpreparestate = 0
                        self.state = self.commandstate
                        if type(self.attacktarget) != int:
                            if self.attacktarget.state == 100:
                                self.attacktarget = 0
                            else:
                                if self.commandstate in (3,4,5,6) and self.hold == 0:
                                    self.set_target(self.attacktarget.basepos)
                else:
                    self.nocombat = 0.1
            else:
                self.nocombat = 0
            ##Rotate Function
            if self.combatpreparestate == 1 and self.stopcombatmove == False: # Rotate army side to the enemyside
                # and [round(elem,2) for elem in self.allsidepos[0]] != [round(elem,2) for elem in self.basetarget]
                self.setrotate(self.attacktarget.pos)
            if self.angle != round(self.newangle) and self.stamina > 0 and (
                    self.hitbox[0].collide == 0 or self.combatpreparestate == 1):
                self.rotatecal = abs(round(self.newangle) - self.angle)
                self.rotatecheck = 360 - self.rotatecal
                self.moverotate = 1
                self.testangle = math.radians(360 - self.angle)
                if self.angle < 0:
                    self.testangle = math.radians(-self.angle)
                ## Rotate logic to continuously rotate based on angle and shortest length
                if self.state in (1, 3, 5):
                    self.rotatespeed = round(self.walkspeed * 50 / (self.armysquad.size / 2))
                    self.walk = True
                else:
                    self.rotatespeed = round(self.runspeed * 50 / (self.armysquad.size / 2))
                    self.run = True
                if self.rotatespeed > 10: self.rotatespeed = 10
                if self.rotatespeed < 1:
                    self.rotatespeed = 1
                rotatetiny = self.rotatespeed * dt
                if round(self.newangle) > self.angle:
                    if self.rotatecal > 180: # rotate with the smallest angle direction
                        self.angle -= rotatetiny
                        self.rotatecheck -= rotatetiny
                        if self.rotatecheck <= 0: self.angle = round(self.newangle)
                    else:
                        self.angle += rotatetiny
                        if self.angle >= self.newangle: self.angle = round(self.newangle)
                elif round(self.newangle) < self.angle:
                    if self.rotatecal > 180:
                        self.angle += rotatetiny
                        self.rotatecheck -= rotatetiny
                        if self.rotatecheck <= 0: self.angle = round(self.newangle)
                    else:
                        self.angle -= rotatetiny
                        if self.angle < self.newangle: self.angle = round(self.newangle)
                self.rotate()
                self.makeallsidepos()
                self.mask = pygame.mask.from_surface(self.image)
            elif self.moverotate == 1 and self.angle == round(self.newangle):  # Finish rotate
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
                    self.setrotate(self.target)
            ## ^End rotate function
            ## Move function
            if self.allsidepos[0] != self.basetarget and self.rangecombatcheck != 1:
                # """Setup target to move to give target position, this can be changed in move fuction (i.e. stopped due to fight and resume moving after finish fight)"""
                # if self.state not in [10]: self.target = self.commandtarget
                if self.state in (3, 4, 5, 6, 10) and self.commandstate in (3,4,5,6) and self.attacktarget != 0 \
                        and self.basetarget != self.attacktarget.basepos and self.hold == 0:  ## Chase target and rotate accordingly
                    cantchase = False
                    for side in self.battlesideid:
                        if (side != 0 and side != self.attacktarget.gameid) or (side == self.attacktarget.gameid and self.combatpreparestate == 1):
                            cantchase = True
                    if cantchase == False and self.forcedmelee:
                        self.state = self.commandstate
                        self.set_target(self.attacktarget.basepos)
                        self.setrotate(self.target)
                """check for hitbox collide according to which ever closest to the target position""" ## TODO try testing whether make charge ignore collide work well or not
                if self.state not in (0, 97) and self.stamina > 0 and (self.retreattimer == 0 or self.retreattimer >= self.retreatmax):
                    side, side2 = self.allsidepos.copy(), {}
                    for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.basetarget)
                    side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])}
                    if (self.hitbox[list(side2.keys())[0]].collide == 0 or self.combatpreparestate == 1) \
                            and self.moverotate == 0 and self.rotateonly != True:
                        move = self.basetarget - self.allsidepos[0]
                        move_length = move.length()
                        # if self.state == 5: self.target = self.pos
                        if move_length > 0.1:
                            # if self.state != 3 and self.retreatcommand == 1:
                            heightdiff = (self.height / self.sideheight[0]) ** 2
                            if self.state in (96, 98, 99) or self.revert:
                                heightdiff = (self.height / self.sideheight[list(side2.keys())[0]]) ** 2
                            move.normalize_ip()
                            if self.state in (1, 3, 5):
                                move = move * self.walkspeed * heightdiff * dt
                                self.walk = True
                            else: #  self.state in (2, 4, 6, 10, 96, 98, 99)
                                move = move * self.runspeed * heightdiff * dt
                                self.run = True
                            # elif self.state == 10:
                            #     move = move * 3 * heightdiff * dt
                            if move.length() <= move_length:
                                self.basepos += move
                                self.pos = self.basepos * abs(self.viewmode - 11)
                                self.rect.center = list(int(v) for v in self.pos)
                            else:
                                move = self.basetarget - self.allsidepos[0]
                                self.basepos += move
                                self.pos = self.basepos * abs(self.viewmode - 11)
                                self.rect.center = self.pos
                                if self.combatpreparestate == 0:
                                    if self.battlesideid == [0,0,0,0] and self.attacktarget == 0 and self.rangecombatcheck == 0:
                                        self.allsidepos[0] = self.commandtarget
                                        self.state = 0
                                        self.revert = False
                                        self.commandstate = self.state
                                else:  # Rotate army to the enemy sharply to stop in combat prepare
                                    self.stopcombatmove = True
                                    self.setrotate(self.attacktarget.pos)
                                    self.angle = self.newangle
                                    self.rotate()
                            if self.state in (5, 6):
                                shootrange = self.maxrange
                                if self.useminrange == 0:
                                    shootrange = self.minrange
                                if (self.attacktarget != 0 and self.basepos.distance_to(self.attacktarget.basepos) <= shootrange) or \
                                        self.basepos.distance_to(self.baseattackpos) <= shootrange:
                                    self.set_target(self.allsidepos[0])
                                    self.rangecombatcheck = 1
                        elif move_length < 0.1 and self.battlesideid == [0,0,0,0] and self.attacktarget == 0 and self.rangecombatcheck == 0:
                            """Stop moving when reach target and go to idle"""
                            self.allsidepos[0] = self.commandtarget
                            self.state = 0
                            self.commandstate = self.state
                        self.terrain, self.feature = self.getfeature(self.basepos, self.gamemap)
                        self.height = self.gamemapheight.getheight(self.basepos)
                        self.makeallsidepos()
                        self.sidefeature = [self.getfeature(self.allsidepos[0], self.gamemap), self.getfeature(self.allsidepos[1], self.gamemap),
                                            self.getfeature(self.allsidepos[2], self.gamemap), self.getfeature(self.allsidepos[3], self.gamemap)]
                        self.sideheight = [self.gamemapheight.getheight(self.allsidepos[0]), self.gamemapheight.getheight(self.allsidepos[1]),
                                           self.gamemapheight.getheight(self.allsidepos[2]), self.gamemapheight.getheight(self.allsidepos[3])]
                        self.mask = pygame.mask.from_surface(self.image)
                    elif self.moverotate == 0 and self.rotateonly:
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
                        self.mask = pygame.mask.from_surface(self.image)
            ## ^End move function
            if self.stamina <= 0:
                self.state = 97
            if self.state == 97:
                awake = True
                for squad in self.squadsprite:
                    if squad.state == 97:
                        awake = False
                        break
                if awake == True:
                    if self.morale > self.brokenlimit:
                        self.state = self.commandstate
                    else: self.state = 98
            if self.combatpreparestate == 1 and self.battlesideid == [0,0,0,0] and self.state != 10:
                self.combatpreparestate = 0
                self.stopcombatmove = False
            if self.troopnumber <= 0:
                self.stamina, self.morale, self.speed = 0, 0, 0
                for leader in self.leader:
                    if leader.state not in (96, 97, 98, 100):  ## leader get captured/flee/die when squad destroyed
                        leader.state = 96
                        for hitbox in self.hitbox:
                            if hitbox.collide != 0 and random.randint(0, 1) == 0:
                                leader.state = 97
                                if random.randint(0, 1) == 0:
                                    leader.state = 100
                self.state = 100
            if self.basepos[0] < 0 or self.basepos[0] > 999 or self.basepos[1] < 0 or self.basepos[
                1] > 999:  ## remove unit when it go out of battlemap
                self.maingame.allunitindex.remove(self.gameid)
                self.leader[0].state = 98
                self.leader[0].health = 0
                self.leader[0].gone()
                self.kill()
                for hitbox in self.hitbox:
                    hitbox.kill()
        else:
            if self.gotkilled == 0:
                if self.gameid < 2000:
                    self.die(self.maingame, self.maingame.playerarmy, self.maingame.enemyarmy)
                    self.maingame.setuparmyicon()
                else:
                    self.die(self.maingame, self.maingame.enemyarmy, self.maingame.playerarmy)
                    self.maingame.setuparmyicon()
                self.maingame.eventlog.addlog([0, str(self.leader[0].name) + "'s battalion is destroyed"], [0, 1])

    def set_target(self, pos):
        self.basetarget = pygame.Vector2(pos)
        self.target = self.basetarget * abs(self.viewmode - 11)

    def rotate(self):
        # Rotate the image.
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        # Rotate the offset vector.
        # offset_rotated = self.offset.rotate(self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=self.pos)  # +offset_rotated)

    def setrotate(self, settarget=0):
        """settarget should be in non-base"""
        self.previousposition = self.pos
        if settarget == 0: # For auto chase rotate
            myradians = math.atan2(self.commandtarget[1] - self.previousposition[1], self.commandtarget[0] - self.previousposition[0])
        else: # Command move or rotate
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

    def processcommand(self, mouse_pos, double_mouse_right, whomouseover, keystate):
        self.state = 1
        self.rotateonly = False
        self.forcedmelee = False
        self.revert = False
        self.attacktarget = 0
        self.baseattackpos = 0
        self.attackpos = 0
        if keystate[pygame.K_LALT] or (whomouseover != 0 and (
                (self.gameid < 2000 and whomouseover.gameid >= 2000) or (self.gameid >= 2000 and whomouseover.gameid < 2000))):
            if self.ammo <= 0 or keystate[pygame.K_LCTRL]:
                self.forcedmelee = True
                self.state = 3
            elif self.ammo > 0:  ##Move to range attack
                self.state = 5
            if keystate[pygame.K_LALT]:
                self.set_target(mouse_pos[1])
                if self.ammo > 0:
                    self.baseattackpos = mouse_pos[1]
            else:
                self.attacktarget = whomouseover
                self.baseattackpos = whomouseover.basepos
        if double_mouse_right:
            self.state += 1
        self.commandstate = self.state
        self.rangecombatcheck = 0
        if keystate[pygame.K_LSHIFT]: self.rotateonly = True
        self.set_target(mouse_pos[1])
        self.commandtarget = self.target
        self.setrotate()
        if keystate[pygame.K_z] == True: ## Revert unit without rotate, cannot run in this state
            self.newangle = self.angle
            self.moverotate = 0
            self.revert = True
            if double_mouse_right:
                self.state -= 1
        if self.charging:
            self.leader[0].authority -= self.authpenalty
            self.authrecal()

    def processretreat(self, mouse_pos, whomouseover):
        if whomouseover == 0:
            self.state = 96
            self.commandstate = self.state
            self.rotateonly = False
            self.forcedmelee = False
            self.attacktarget = 0
            self.baseattackpos = 0
            self.attackpos = 0
            if self.retreattimer == 0:
                self.leader[0].authority -= self.authpenalty
                self.authrecal()
                self.retreattimer = 0.1
                self.retreatstart = 1
            self.set_target(mouse_pos[1])
            self.commandtarget = self.target
            self.combatpreparestate = 0

    def command(self, mouse_pos, mouse_right, double_mouse_right, whomouseover, keystate, othercommand=0):
        """othercommand is special type of command such as stop all action, raise flag, decimation, duel and so on"""
        if self.control and self.state != 100:
            """check if right click in mask or not. if not, move unit"""
            posmask = mouse_pos[0][0] - self.rect.x, mouse_pos[0][1] - self.rect.y
            if mouse_right and mouse_pos[1][0] >= 1 and mouse_pos[1][0] < 998 and mouse_pos[1][1] >= 1 and mouse_pos[1][1] < 998:
                if self.state not in (10, 97, 98, 99, 100):
                    try:  ## if click within rect but not in mask
                        if self.mask.get_at(posmask) == 0:
                            self.processcommand(mouse_pos, double_mouse_right, whomouseover, keystate)
                    except:  ## if click outside of rect and mask
                        self.processcommand(mouse_pos, double_mouse_right, whomouseover, keystate)
                elif self.state == 10:  ##Enter Fall back state if in combat and move command issue
                    try:
                        if self.mask.get_at(posmask) == 0:
                            self.processretreat(mouse_pos, whomouseover)
                    except:
                        self.processretreat(mouse_pos, whomouseover)
            elif othercommand == 1 and self.state not in (10, 97, 98, 99, 100):  ## Pause all action except combat
                if self.charging:
                    self.leader[0].authority -= self.authpenalty
                    self.authrecal()
                self.state = 0
                self.commandstate = self.state
                self.set_target(self.allsidepos[0])
                self.commandtarget = self.target
                self.rangecombatcheck = 0
                self.setrotate()

    def switchfaction(self, oldgroup, newgroup, oldposlist, allunitindex, enactment):
        """Change army group and gameid when change side"""
        self.colour = (144, 167, 255)
        self.control = True
        if self.gameid < 2000:
            self.colour = (255, 114, 114)
            if enactment == False:
                self.control = False
        newgameid = newgroup[-1].gameid + 1
        oldgroup.remove(self)
        newgroup.append(self)
        oldposlist.pop(self.gameid)
        allunitindex = [newgameid if index == self.gameid else index for index in allunitindex]
        self.gameid = newgameid
        self.recreatesprite()
        self.changescale()
        return allunitindex


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
