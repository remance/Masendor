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

class Directionarrow(pygame.sprite.Sprite): #TODO make it work so it can be implemented again
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
        self.image = pygame.Surface((width, height), pygame.SRCALPHA) # Default image
        self.image.fill((0, 0, 0, 128)) # Hitbox when unit not selected (black)
        self.clickimage = self.image.copy() # Image used when click
        self.clickimage.fill((255, 0, 0, 128)) # Hitbox when unit selected (red)
        self.notclickimage = self.image.copy() # save not click image
        self.image_original, self.image_original2 = self.image.copy(), self.image.copy() # original 2 is true original at cloest zoom
        self.image = pygame.transform.rotate(self.image_original, self.who.angle) # Rotate
        self.oldpos = self.who.hitboxpos[self.side] # For checking if hitbox pos change
        self.rect = self.image.get_rect(center=self.who.hitboxpos[self.side])
        self.pos = self.rect.center
        self.mask = pygame.mask.from_surface(self.image)
        self.clickcheck = False # For checking if battalion just get selected
        self.stillclick = False # For checking if battalion is still selected, if not change back image

    def update(self, viewmode):
        if self.viewmode != abs(viewmode - 11) or self.clickcheck:
            self.viewmode = abs(viewmode - 11) # change zoomview number for scaling image
            self.image_original = self.image_original2.copy()
            scalewidth = self.image_original.get_width() * abs(self.viewmode - 11) / self.maxviewmode
            scaleheight = self.image_original.get_height() * abs(self.viewmode - 11) / self.maxviewmode
            self.dim = pygame.Vector2(scalewidth, scaleheight)
            self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
            self.mask = pygame.mask.from_surface(self.image) # make new mask for collision
            self.image_original = self.image.copy()
        if self.oldpos != self.who.hitboxpos[self.side] or self.clickcheck: # battalion change pos or rotate
            self.image = pygame.transform.rotate(self.image_original, self.who.angle)
            self.rect = self.image.get_rect(center=self.who.hitboxpos[self.side])
            self.pos = self.rect.center # new pos at new center
            self.mask = pygame.mask.from_surface(self.image) # make new mask for collision
            self.oldpos = self.who.hitboxpos[self.side]

    def clicked(self):
        """change variable of hitbox when battalion get clicked"""
        self.image_original2 = self.clickimage.copy()
        self.clickcheck = True
        self.update(abs(11 - self.viewmode))
        self.clickcheck = False
        self.stillclick = True

    def release(self):
        """change variable of hitbox when battalion no longer clicked"""
        self.image_original2 = self.notclickimage.copy()
        self.clickcheck = True
        self.update(abs(11 - self.viewmode))
        self.clickcheck = False
        self.stillclick = False


class Unitarmy(pygame.sprite.Sprite):
    images = []
    gamemap = None # base map
    gamemapfeature = None # feature map
    gamemapheight = None # height map
    statuslist = None # status effect list
    maxviewmode = 10 # max zoom allow
    maingame = None
    squadcombatcal = gamelongscript.squadcombatcal
    die = gamelongscript.die # die script

    def __init__(self, startposition, gameid, squadlist, imgsize, colour, control, coa, commander, startangle, starthp=100, startstamina=100):
        """Although battalion in code, this is referred as unit ingame"""
        # super().__init__()
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        # self.unitarray = unitarray
        self.starthp = starthp # starting hp percentage
        self.startstamina = startstamina # starting stamina percentage
        self.armysquad = squadlist # squad array
        self.colour = colour # box colour according to team
        self.commander = commander # commander battalion if true
        self.teamcommander = None # commander leader
        self.squadalive = np.copy(self.armysquad) # Array for checking which squad still alive
        self.squadalive = np.where(self.squadalive > 0, 2, self.squadalive) # Alive state array 0 = not exist, 1 = dead, 2 = alive
        self.startwhere = []
        self.hitbox = [] # for keeping hitbox object list
        self.squadsprite = []  # list of squad object(not index), name is squadsprite because I am too lazy to change now
        self.icon = None  ## for linking with army selection ui, got linked when icon created in gameui.Armyicon
        self.justsplit = False
        self.viewmode = 10 # start with closest zoom
        self.imgsize = imgsize
        self.widthbox, self.heightbox = len(self.armysquad[0]) * self.imgsize[0], len(self.armysquad) * self.imgsize[1]
        self.basewidthbox, self.baseheightbox = self.widthbox / 10, self.heightbox / 10
        self.widthscale, self.heightscale = len(self.armysquad[0]) * self.imgsize[0] * self.viewmode, len(self.armysquad) * self.imgsize[
            1] * self.viewmode
        self.gameid = gameid # id of battalion for reference in many function
        self.control = control # player control or not
        self.basepos = pygame.Vector2(startposition)  # Basepos is for true pos that is used for ingame calculation
        self.baseattackpos = 0 # position of attack target
        self.pos = self.basepos * (11- self.viewmode) # Pos is for showing on screen
        self.angle = startangle # start at this angle
        self.newangle = self.angle
        self.moverotate = False # for checking if the movement require rotation first or not
        self.rotatecal = 0 # for calculate how much angle to rotate to the target
        self.rotatecheck = 0 # for checking if the new angle rotate pass the target angle or not
        self.walk = False # currently walking
        self.run = False # currently running
        self.leaderchange = False
        self.directionarrow = False
        self.rotateonly = False # Order battalion to rotate to target direction
        self.charging = False # For squad charge skill activation
        self.forcedmelee = False # Force battalion to melee attack
        self.forcedmarch = False
        self.changefaction = False # For initiating change faction function
        self.runtoggle = 0 # 0 = double right click to run, 1 = only one right click will make battalion run
        self.shoothow = 0 # 0 = both arc and non-arc shot, 1 = arc shot only, 2 = forbid arc shot
        self.brokenlimit = 50 # morale require for battalion to stop broken state, will increase everytime broken state stop
        self.formchangetimer = 10
        self.hold = 0  # 0 = not hold, 1 = skirmish/scout/avoid, 2 = hold
        self.fireatwill = 0  # 0 = fire at will, 1 = no fire
        self.retreatstart = False
        self.retreattimer, self.retreatmax = 0, 0
        self.retreatway = None
        self.rangecombatcheck = False
        self.attacktarget = 0 # attack target, can be either int or battalion object
        self.neartarget = {} # list dict of nearby enemy battalion, sorted by distance
        self.gotkilled = False # for checking if die() was performed when unit die yet
        self.combatpreparestate = False # for initialise auto placement in melee combat
        self.gotcombatprepare = False # for checking if the enemy is the one doing auto placement or not
        self.stopcombatmove = False
        self.troopnumber = 0 # sum
        self.stamina = 0 # average from all squad
        self.morale = 0 # average from all squad
        self.ammo = 0 # total ammo left of the whole battalion
        self.oldammo = 0 # previous number of ammo for ammo bar checking
        self.minrange = 0 # minimum shoot range of all squad inside this battalion
        self.maxrange = 0 # maximum shoot range of all squad inside this battalion
        self.useminrange = 0 # use min or max range for walk/run (range) command
        self.useskillcond = 0 # skill condition for stamina reservation
        self.sidefeature = []
        self.sideheight = []
        self.getfeature = self.gamemapfeature.getfeature # get terrain feature fuction
        self.set_target(startposition)
        self.basepreviousposition = pygame.Vector2(startposition)
        self.previousposition = self.basepreviousposition * (11 - self.viewmode)
        self.state = 0  # see gameui.py topbar for name of each state
        self.commandstate = self.state
        self.deadchange = False # for checking when squad dead and run related code
        self.timer = random.random()
        self.squadimgchange = []
        self.zoomchange = False
        self.gamestart = False # for running code that only require at the start of game or when battalion spawn
        self.authrecalnow = False # for recalculate authority of the battalion
        self.cansplitrow = False
        self.revert = False
        if np.array_split(self.armysquad, 2)[0].size > 10 and np.array_split(self.armysquad, 2)[1].size > 10: self.cansplitrow = True
        self.cansplitcol = False
        if np.array_split(self.armysquad, 2, axis=1)[0].size > 10 and np.array_split(self.armysquad, 2, axis=1)[1].size > 10: self.cansplitcol = True
        self.authpenalty = 0 # authority penalty
        self.tacticeffect = {}
        self.image = pygame.Surface((self.widthbox, self.heightbox), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 128)) # draw black colour for black corner
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.widthbox, self.heightbox), 2) # draw black corner
        pygame.draw.rect(self.image, self.colour, (1, 1, self.widthbox - 2, self.heightbox - 2)) # draw block colour
        self.imagerect = self.images[-1].get_rect(center=self.image.get_rect().center) # battalion ring
        self.image.blit(self.images[-1], self.imagerect) # draw battalion ring into battalion image
        self.healthimagerect = self.images[0].get_rect(center=self.image.get_rect().center) # hp bar
        self.image.blit(self.images[0], self.healthimagerect) # draw hp bar into battalion image
        self.staminaimagerect = self.images[5].get_rect(center=self.image.get_rect().center) # stamina bar
        self.image.blit(self.images[5], self.staminaimagerect) # draw stamina bar into battalion image
        self.ammoimagerect = self.images[14].get_rect(center=self.image.get_rect().center)  # ammo bar
        self.image.blit(self.images[14], self.ammoimagerect) # draw ammo bar into battalion image
        self.coa = coa # coat of arm image
        self.team = 1 # team1
        if self.gameid >= 2000: # team2
            self.team = 2
        # self.imagerect = self.coa.get_rect(center=self.image.get_rect().center)
        # self.image.blit(self.coa, self.imagerect)
        self.image_original, self.image_original2, self.image_original3 = self.image.copy(), self.image.copy(), self.image.copy()  ## original is for before image get rorated, original2 is for zoom closest, original3 is for zooming
        self.rect = self.image.get_rect(center=startposition)
        self.radians_angle = math.radians(360 - startangle) # radians for apply angle to position (allsidepos and squad)
        self.mask = pygame.mask.from_surface(self.image)
        self.allsidepos = [(self.basepos[0], (self.basepos[1] - self.baseheightbox / 2)),  # Generate all four side position
                           ((self.basepos[0] - self.basewidthbox / 2), self.basepos[1]),
                           ((self.basepos[0] + self.basewidthbox / 2), self.basepos[1]),
                           (self.basepos[0], (self.basepos[1] + self.baseheightbox / 2))]
        self.allsidepos = [rotationxy(self.basepos, self.allsidepos[0], self.radians_angle),  # generate again but with rotation in calculation
                           rotationxy(self.basepos, self.allsidepos[1], self.radians_angle),
                           rotationxy(self.basepos, self.allsidepos[2], self.radians_angle),
                           rotationxy(self.basepos, self.allsidepos[3], self.radians_angle)]
        self.hitboxpos = [(self.rect.center[0], (self.rect.center[1] - self.heightscale / 2)), # Generate pos for all hitbox side
                          ((self.rect.center[0] - self.widthscale / 2), self.rect.center[1]),
                          ((self.rect.center[0] + self.widthscale / 2), self.rect.center[1]),
                          (self.rect.center[0], (self.rect.center[1] + self.heightscale / 2))]
        self.hitboxpos = [rotationxy(self.rect.center, self.hitboxpos[0], self.radians_angle),  # Generate hitbox pos with current angle
                          rotationxy(self.rect.center, self.hitboxpos[1], self.radians_angle)
            , rotationxy(self.rect.center, self.hitboxpos[2], self.radians_angle), rotationxy(self.rect.center, self.hitboxpos[3], self.radians_angle)]
        self.frontpos = self.allsidepos[0] # The front center pos
        self.squadpositionlist = []
        self.battleside = [None, None, None, None] # battleside with enemy object
        self.battlesideid = [0,0,0,0]  # index of battleside (enemy gameid fighting at the side of battalion), list index: 0 = front 1 = left 2 =right 3 =rear
        self.frontline = {0: [], 1: [], 2: [], 3: []}  ## frontline keep list of squad at the front of each side in combat, same list index as above

        #v Set up squad position list for drawing
        width, height = 0, 0
        squadnum = 0 # Number of squad based on the position in row and column
        for squad in self.armysquad.flat:
            width += self.imgsize[0]
            self.squadpositionlist.append((width, height))
            squadnum += 1
            if squadnum >= len(self.armysquad[0]): # Reach the last squad in the row, go to the next one
                width = 0
                height += self.imgsize[1]
                squadnum = 0
        #^ End squad position list

    def changescale(self):
        """Change image based on current camera scale"""
        scalewidth = self.image_original.get_width() * (11 - self.viewmode) / self.maxviewmode
        scaleheight = self.image_original.get_height() * (11 - self.viewmode) / self.maxviewmode
        self.widthscale, self.heightscale = len(self.armysquad[0]) * self.imgsize[0] * (11 - self.viewmode) / self.maxviewmode, len(
            self.armysquad) * self.imgsize[1] * (11 - self.viewmode) / self.maxviewmode
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.rotate()

    def changeposscale(self):
        """Change position variable to new camera scale"""
        self.target = self.basetarget * (11 - self.viewmode)
        self.previousposition = self.basepreviousposition * (11 - self.viewmode)
        self.pos = self.basepos * (11 - self.viewmode)
        self.rect = self.image.get_rect(center=self.pos)
        self.makeallsidepos()
        self.frontpos = self.allsidepos[0]

    def recreatesprite(self):
        """redrawing sprite for when split happen since the size will change"""
        self.widthbox, self.heightbox = len(self.armysquad[0]) * self.imgsize[0], len(self.armysquad) * self.imgsize[1]
        self.basewidthbox, self.baseheightbox = self.widthbox / 10, self.heightbox / 10
        self.image = pygame.Surface((self.widthbox, self.heightbox), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 128))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.widthbox, self.heightbox), 2)
        pygame.draw.rect(self.image, self.colour, (1, 1, self.widthbox - 2, self.heightbox - 2))
        self.imagerect = self.images[-1].get_rect(center=self.image.get_rect().center)  # battalion ring
        self.image.blit(self.images[-1], self.imagerect)
        self.healthimage = self.images[0] # health bar
        self.healthimagerect = self.healthimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.healthimage, self.healthimagerect)
        self.staminaimage = self.images[5] # stamina bar
        self.staminaimagerect = self.staminaimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.staminaimage, self.staminaimagerect)
        self.ammoimage = self.images[10] # ammo bar
        self.ammoimagerect = self.ammoimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.ammoimage, self.ammoimagerect)
        self.image_original, self.image_original2, self.image_original3 = self.image.copy(), self.image.copy(), self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.radians_angle = math.radians(360 - self.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.setuparmy()

    def squadtoarmy(self):
        """drawing squad into battalion sprite"""
        squadnum = 0
        truesquadnum = 0
        width, height = 0, 0
        for squad in self.armysquad.flat:
            if squad != 0:
                if self.zoomchange == True or squad in self.squadimgchange:
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
        """Grab stat from all squad in the battalion"""
        self.troopnumber = 0
        self.stamina = 0
        self.morale = 0
        allspeed = [] # list of squad spped, use to get the slowest one
        self.ammo = 0
        howmany = 0
        allshootrange = [] # list of shoot range, use to get the shortest and longest one

        #v Grab squad stat
        for squad in self.squadsprite:
            if squad.state != 100: # only get stat from alive squad
                self.troopnumber += squad.troopnumber
                self.stamina += squad.stamina
                self.morale += squad.morale
                allspeed.append(squad.speed)
                self.ammo += squad.ammo
                if squad.shootrange > 0:
                    allshootrange.append(squad.shootrange)
                squad.combatpos = self.basepos
                squad.useskillcond = self.useskillcond
                squad.attacktarget = self.attacktarget
                squad.attackpos = self.baseattackpos
                if self.attacktarget != 0:
                    squad.attackpos = self.attacktarget.basepos
                howmany += 1
        #^ End grab squad stat

        #v calculate stat for battalion related calculation
        if self.troopnumber > 0:
            self.stamina = int(self.stamina/howmany) # Average stamina of all squad
            self.morale = int(self.morale/howmany) # Average moorale of all squad
            self.speed = min(allspeed) # use slowest squad
            self.walkspeed, self.runspeed = self.speed / 20, self.speed / 15
            if len(allshootrange) > 0:
                self.maxrange = max(allshootrange) # Max shoot range of all squad
                self.minrange = min(allshootrange) # Min shoot range of all squad
            if self.gamestart == False: # Only do once when game start
                self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 0.75), round(
                    self.stamina * 0.50), round(self.stamina * 0.25)
                self.ammo75, self.ammo50, self.ammo25 = round(self.ammo * 0.75), round(self.ammo * 0.50), round(self.ammo * 0.25)
                self.lasthealthstate, self.laststaminastate, self.lastammostate = 4, 4, 0
                self.maxmorale = self.morale
                self.maxhealth, self.health75, self.health50, self.health25, = self.troopnumber, round(self.troopnumber * 0.75), round(
                    self.troopnumber * 0.50), round(self.troopnumber * 0.25)
            self.moralestate = round((self.morale * 100) / self.maxmorale)
            self.staminastate = round((self.stamina * 100) / self.maxstamina)
        #^ End cal

    def setupfrontline(self, specialcall=False):
        """Setup frontline array"""
        gotanother = True # keep finding another squad while true
        startwhere = 0
        whoarray = np.where(self.squadalive > 1, self.armysquad, self.squadalive)
        fullwhoarray = [whoarray, np.fliplr(whoarray.swapaxes(0, 1)), np.rot90(whoarray), np.fliplr([whoarray])[0]] # rotate the array based on the side
        whoarray = [whoarray[0], fullwhoarray[1][0], fullwhoarray[2][0],
                    fullwhoarray[3][0]]
        for index, whofrontline in enumerate(whoarray):
            if self.gamestart == False and specialcall == False: # only need to do this once
                emptyarray = np.array([0, 0, 0, 0, 0, 0, 0, 0]) # Add zero to the frontline so it become 8 row array
                whocenter = (8 - len(whofrontline)) / 2 # find the center of frontline
                ## odd number frontline will be placed either 1 slot further to the right or not
                ## for example, 5 squads [0, 1, 1, 1, 1, 1, 0, 0] or [0, 0, 1, 1, 1, 1, 1, 0]
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
                dead = np.where((newwhofrontline == 0) | (newwhofrontline == 1)) # replace the dead in frontline with other squad in the same column
                for deadsquad in dead[0]:
                    run = 0
                    while gotanother == True:
                        if fullwhoarray[index][run, deadsquad] not in (0, 1):
                            newwhofrontline[deadsquad] = fullwhoarray[index][run, deadsquad]
                            gotanother = False
                        else:
                            run += 1
                            if len(fullwhoarray[index]) == run:
                                newwhofrontline[deadsquad] = 1  # Only use number 1 for dead squad (0 mean not existed in the first place)
                                gotanother = False
                    gotanother = True # reset for another loop
                whocenter = self.startwhere[startwhere]
                emptyarray[int(whocenter):int(len(newwhofrontline) + whocenter)] = newwhofrontline
                newwhofrontline = emptyarray.copy()
            startwhere += 1
            self.frontline[index] = newwhofrontline

        self.authpenalty = 0
        for squad in self.squadsprite:
            if squad.state != 100:
                self.authpenalty += squad.authpenalty # add authority penalty of all alive squad

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
        """The attacker will enter combatprepare state to allow auto placement move to the center of enemy side"""
        self.stopcombatmove = False # allow moving during melee combat for auto placement
        self.combatpreparestate = True # start auto placement
        self.enemyprepareside = enemyhitbox.side # get the enemy side that is being auto place to
        enemyhitbox.who.gotcombatprepare = True # enemy got combat prepare by this battalion
        self.attacktarget = enemyhitbox.who # set attack target
        self.baseattackpos = self.attacktarget.allsidepos[self.enemyprepareside] # set attack target position
        if enemyhitbox.side == 0: # enemy can attack back if defend from the front
            self.attacktarget.attacktarget = self
        else: # enemy cannot attack back when getting flanked or reared
            if self.attacktarget.state not in (96,97,98,99): # retreat will not stop moving
                self.attacktarget.set_target(self.attacktarget.allsidepos[0]) # stop moving when get hit
        self.set_target(enemyhitbox.who.allsidepos[enemyhitbox.side]) # set new target to the position of enemy side for auto placement

    def makeallsidepos(self):
        """generate all four side, hitbox and squad positions"""
        self.allsidepos = [(self.basepos[0], (self.basepos[1] - self.baseheightbox / 2)),  # Generate all four side position
                           ((self.basepos[0] - self.basewidthbox / 2), self.basepos[1]),
                           ((self.basepos[0] + self.basewidthbox / 2), self.basepos[1]),
                           (self.basepos[0], (self.basepos[1] + self.baseheightbox / 2))]
        self.allsidepos = [rotationxy(self.basepos, self.allsidepos[0], self.radians_angle),  # rotate the new four side according to sprite rotation
                           rotationxy(self.basepos, self.allsidepos[1], self.radians_angle),
                           rotationxy(self.basepos, self.allsidepos[2], self.radians_angle),
                           rotationxy(self.basepos, self.allsidepos[3], self.radians_angle)]
        self.hitboxpos = [(self.rect.center[0], (self.rect.center[1] - self.heightscale / 2)), # generate new hitbox position for each side
                          ((self.rect.center[0] - self.widthscale / 2), self.rect.center[1]),
                          ((self.rect.center[0] + self.widthscale / 2), self.rect.center[1]),
                          (self.rect.center[0], (self.rect.center[1] + self.heightscale / 2))]
        self.hitboxpos = [rotationxy(self.rect.center, self.hitboxpos[0], self.radians_angle),  # rotate the four hitboxes according to sprite rotation
                          rotationxy(self.rect.center, self.hitboxpos[1], self.radians_angle),
                          rotationxy(self.rect.center, self.hitboxpos[2], self.radians_angle),
                          rotationxy(self.rect.center, self.hitboxpos[3], self.radians_angle)]
        battaliontopleft = pygame.Vector2(self.basepos[0] - self.basewidthbox / 2, # get the top left corner of sprite to generate squad position
                                         self.basepos[1] - self.baseheightbox / 2)
        for squad in self.squadsprite: # generate position of each squad
            squad.truepos = (battaliontopleft[0] + (squad.armypos[0] / 10), battaliontopleft[1] + (squad.armypos[1] / 10))
            squad.truepos = pygame.Vector2(rotationxy(self.basepos, squad.truepos, self.radians_angle)) # rotate according to sprite current rotation
            squad.terrain, squad.feature = self.getfeature(squad.truepos, self.gamemap) # get new terrain and feature at each squad position
            squad.height = self.gamemapheight.getheight(squad.truepos) # get new height

    def authrecal(self):
        """recalculate authority from all alive leaders"""
        self.authority = int(self.teamcommander.authority + (self.leader[0].authority / 2) + (self.leader[1].authority / 4) +
                              (self.leader[2].authority / 4) + (self.leader[3].authority / 10))
        bigarmysize = self.armysquad > 0
        bigarmysize = bigarmysize.sum()
        if bigarmysize > 20:
            self.authority = int(
                (self.leader[0].authority * (100 - (bigarmysize)) / 100) + self.leader[1].authority / 2 + self.leader[2].authority / 2 +
                self.leader[3].authority / 4)

    def startset(self, squadgroup):
        """Setup stuff at the start of game or when battalion spawn"""
        self.setuparmy()
        self.setupfrontline()
        self.setupfrontline(specialcall=True)
        self.oldarmyhealth, self.oldarmystamina = self.troopnumber, self.stamina
        self.rotate()
        self.makeallsidepos()
        self.frontpos = self.allsidepos[0]
        self.set_target(self.frontpos)
        self.commandtarget = self.basetarget
        self.spritearray = self.armysquad
        self.leadersocial = self.leader[0].social
        for leader in self.leader:
            if leader.gameid != 1:
                print(self.gameid,leader.squadpos, leader.name)
                self.squadsprite[leader.squadpos].leader = leader  ## put in leader to squad with the set pos
        if self.commander:
            # v assign team commander to every battalion in team if this is commander battalion
            whicharmy = self.maingame.team1army
            if self.team == 2:  # team2
                whicharmy = self.maingame.team2army
            for army in whicharmy:
                army.teamcommander = self.leader[0]
            # ^ End assign
        self.authrecal()
        self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                            (self.leader[0].cavcommand - 5) * 0.1] # battalion leader command buff
        self.height = self.gamemapheight.getheight(self.basepos)
        self.sideheight = [self.gamemapheight.getheight(self.allsidepos[0]), self.gamemapheight.getheight(self.allsidepos[1]),
                           self.gamemapheight.getheight(self.allsidepos[2]), self.gamemapheight.getheight(self.allsidepos[3])]
        for squad in squadgroup:
            self.spritearray = np.where(self.spritearray == squad.gameid, squad, self.spritearray)
        self.changescale()
        self.changeposscale()

    def viewmodechange(self):
        """camera zoom change and rescale the sprite and position scale"""
        if self.viewmode != 1:  ## battalion view
            self.image_original = self.image_original3.copy() # reset image for new scale
            self.changescale()
        elif self.viewmode == 1:  ## Squad view when zoom closest (10 in other class without need zoom image)
            self.image_original = self.image_original2.copy() # reset image to the closest zoom original
            self.squadtoarmy()
            self.changescale()
        self.changeposscale()
        self.rotate()
        self.mask = pygame.mask.from_surface(self.image) # create new mask

    def update(self, weather, squadgroup, dt, viewmode, mousepos, mouseup):
        if self.gamestart == False:
            self.startset(squadgroup)
            self.gamestart = True
        #v redraw if troop num or stamina change
        if self.troopnumber != self.oldarmyhealth or self.stamina != self.oldarmystamina or self.ammo != self.oldammo or self.viewmode != (11 - viewmode):
            if self.viewmode != (11 - viewmode): # camera zoom is changed
                self.zoomchange = True
                self.viewmode = (11 - viewmode) # save scale
                self.viewmodechange() # update battalion sprite according to new scale

            if self.viewmode != 1: # any camera scale except the closest zoom
                #v hp bar
                if self.oldarmyhealth != self.troopnumber: # troop number change since last update
                    healthlist = (self.health75, self.health50, self.health25, 0, -1)
                    for index, health in enumerate(healthlist): # Loop to find appropiate hp circle image
                        if self.troopnumber > health: # found where health bar level is at
                            if self.lasthealthstate != abs(4 - index): # current health bar is not yet updated to this new level
                                self.image_original3.blit(self.images[index], self.healthimagerect) # blit new health bar image
                                self.lasthealthstate = abs(4 - index) # change last health level
                                self.viewmodechange() # update sprite image at this camera scale
                            break # found appropiate hp level, break loop
                    self.oldarmyhealth = self.troopnumber # save current troop number for next check
                #^ End hp bar

                #v Stamina bar, slightly similar as hp bar
                if self.oldarmystamina != self.stamina: # stamina change since last update
                    staminalist = (self.stamina75, self.stamina50, self.stamina25, 0, -1)
                    for index, stamina in enumerate(staminalist):
                        if self.stamina > stamina:
                            if self.laststaminastate != abs(4 - index):
                                if index != 3: # not at the collapse level
                                    self.image_original3.blit(self.images[index + 5], self.staminaimagerect)
                                    self.laststaminastate = abs(4 - index)
                                    self.viewmodechange()
                                else: # at the collapse stamina level (0% stamina)
                                    if self.state != 97: # no longer in collaspe state
                                        self.image_original3.blit(self.images[8], self.staminaimagerect) # blit new stamina bar image back to 25% level
                                        self.laststaminastate = 1
                                        self.viewmodechange()
                            break
                    self.oldarmystamina = self.stamina # save current stamina for next check
                #^ End stamina bar

                #v ammunition bar, do similar to hp bar
                if self.oldammo != self.ammo: # ammunition change since last update
                    ammolist = (self.ammo75, self.ammo50, self.ammo25, 0, -1)
                    for index, ammo in enumerate(ammolist):
                        if self.ammo > ammo:
                            if self.lastammostate != abs(4 - index):
                                self.image_original3.blit(self.images[index + 10], self.ammoimagerect)
                                self.lastammostate = abs(4 - index)
                                self.viewmodechange()
                            break
                    self.oldammo = self.ammo # save current ammunition for next check
                #^ End ammunition bar

            else: # closest camera zoom
                if self.squadimgchange != [] or self.zoomchange == True: # update squad image inside battalion sprite
                    self.squadtoarmy() # update squad image individually
                    self.rotate() # rotate after update
                    self.squadimgchange = [] # reset squad image to update list
                    self.zoomchange = False # reset camera zoom change
        #^ End redraw

        if self.state != 100:
            if self.team == 1:
                self.maingame.team1poslist[self.gameid] = self.basepos # update current position to team list
                thisposlist = self.maingame.team2poslist # update position list
            else:
                self.maingame.team2poslist[self.gameid] = self.basepos # update current position to team list
                thisposlist = self.maingame.team1poslist # update position list
            #v Mouse collision detect
            if self.rect.collidepoint(mousepos):
                posmask = int(mousepos[0] - self.rect.x), int(mousepos[1] - self.rect.y) # for checking whether mouse position is inside mask or not
                try:
                    if self.mask.get_at(posmask) == 1: # mouse inside mask
                        self.maingame.lastmouseover = self # last mouse over on this battalion
                        if mouseup and self.maingame.uiclick == False:
                            self.maingame.lastselected = self # become last selected battalion
                            for hitbox in self.hitbox:
                                hitbox.clicked() # change hitbox colour to selected
                            if self.maingame.beforeselected is not None and self.maingame.beforeselected != self: # battalion was selected before but not anymore
                                for hitbox in self.maingame.beforeselected.hitbox:
                                    hitbox.release() # change hitbox colour to non-selected
                            self.maingame.clickany = True
                except: pass # not inside, skip
            #^ End mouse detect

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
                    self.timer -= 1 # reset timer, not reset to 0 because higher speed can cause inconsistency in update timing
            if self.authrecalnow:
                self.authrecal()
                self.authrecalnow = False

            #v Setup frontline again when any squad die
            if self.deadchange == True:
                self.setupfrontline()
                for squad in self.squadsprite:
                    squad.basemorale -= 30
                self.deadchange = False
            # ^End setup frontline when squad die

            #v Combat and unit update
            for hitbox in self.hitbox:
                collidelist = pygame.sprite.spritecollide(hitbox, self.maingame.hitboxes, dokill=False, collided=pygame.sprite.collide_mask)
                for hitbox2 in collidelist:
                    if self.gameid != hitbox2.who.gameid:  ##colide battalion in same faction
                        hitbox.collide, hitbox2.collide = hitbox2.who.gameid, self.gameid
                        if self.team != hitbox2.who.team:
                            if (self.combatpreparestate and hitbox2.who.gameid == self.attacktarget.gameid) \
                                    or (self.battlesideid[hitbox.side] == 0 and hitbox2.who.battlesideid[hitbox2.side] == 0):
                                self.battleside[hitbox.side] = hitbox2.who
                                self.battlesideid[hitbox.side] = hitbox2.who.gameid
                                hitbox2.who.battleside[hitbox2.side] = self
                                hitbox2.who.battlesideid[hitbox2.side] = self.gameid
                            """set up army position to the enemyside"""
                            if self.combatpreparestate == False and hitbox.side == 0 and self.state in (1, 2, 3, 4, 5, 6) and self.battleside[hitbox.side] == hitbox2.who and \
                                    (hitbox2.who.combatpreparestate == False or (hitbox2.who.combatpreparestate and hitbox2.who.attacktarget.gameid != self.gameid)):
                                self.combatprepare(hitbox2)    # run combatprepare when combat start if army is the attacker
            for index, battle in enumerate(self.battleside):
                if battle is not None and self.gameid in battle.battlesideid:
                    self.squadcombatcal(self.maingame.squad, self.maingame.squadindexlist, battle, index,
                                        battle.battlesideid.index(self.gameid))
            #^ End combat update

            # if self.attacktarget != 0: self.baseattackpos = self.attacktarget.basepos

            #v Recal stat involve leader if one die
            if self.leaderchange:
                self.authrecal()
                for leader in self.leader:
                    if leader.gameid != 0:
                        self.squadsprite[leader.squadpos].leader = leader
                self.commandbuff = [(self.leader[0].meleecommand - 5) * 0.1, (self.leader[0].rangecommand - 5) * 0.1,
                                    (self.leader[0].cavcommand - 5) * 0.1]
                self.leaderchange = False
            #^ End recal stat when leader die

            if self.battlesideid != [0,0,0,0]:
                self.rangecombatcheck = False # can not use range attack in melee combat
                """enter melee combat state when check"""
                if self.state not in (96, 98, 99):
                    self.state = 10
                    self.newangle = self.angle # stop rotating when get attacked
            if self.rangecombatcheck: self.state = 11 # can only shoot if rangecombatcheck is true

            #v Retreat function
            if round(self.morale) <= 20 and self.state != 97:  ## Retreat state when morale lower than 20
                self.state = 98
                if self.retreatstart == False:
                    self.retreatstart = True
                    self.retreattimer = 0.1
                if self.morale <= 10:  ## Broken state
                    self.morale, self.state = 0, 99
            elif self.state == 98 and self.morale >= self.brokenlimit/2:  # quit retreat when morale reach increasing limit
                self.state = 0 # become idle, not resume previous command
                self.retreattimer = 0
                self.retreatstart = False
                self.retreatway = None
                self.set_target(self.basepos)
                self.brokenlimit += random.randint(1,10)
            elif self.state == 99 and self.morale >= self.brokenlimit: # quit broken when morale reach increasing limit
                self.state = 0 # become idle, not resume previous command
                self.retreattimer = 0 # no longer retreat
                self.retreatstart = False
                self.retreatway = None
                self.set_target(self.basepos)
                self.brokenlimit += random.randint(5,15)
            if self.retreattimer > 0: # update retreat timer
                self.retreattimer += dt
            if self.retreatstart:
                retreatside = [hitbox.side for hitbox in self.hitbox if hitbox.collide == 0]
                if len(retreatside) > 0: # has no collided side to flee
                    self.retreatmax = (4 - len(retreatside)) * 2 # retreat time +2 second for every side that collided
                    if self.retreattimer >= self.retreatmax: # can only retreat when timer reach max
                        if self.state in (98, 99): # retreat/broken state
                            if self.retreatway is None or self.retreatway[1] not in retreatside: # not yet start retreat or previous retreat way got blocked
                                if 3 in retreatside: # prioritise rear retreat
                                    self.retreatway = [self.allsidepos[3], 3] # [position of side to retreat with, side]
                                else: # retreat on other side
                                    getrandom = random.randint(0, len(retreatside) - 1) # randomly select side
                                    self.retreatway = [self.allsidepos[retreatside[getrandom]], retreatside[getrandom]] # [position of side to retreat with, side]
                                basetarget = self.basepos + ((self.retreatway[0] - self.basepos)*100)
                                self.set_target(basetarget)
                            self.combatpreparestate = False
                        self.retreattimer = self.retreatmax
                else:  # no way to retreat, Fight to the death
                    self.state = 10
                    for squad in self.squadsprite:
                        if 9 not in squad.statuseffect:
                            squad.statuseffect[9] = self.statuslist[9].copy() # fight to the death status
                    # if random.randint(0, 100) > 99:  ## change side via surrender or betrayal
                    #     if self.team == 1:
                    #         self.maingame.allunitindex = self.switchfaction(self.maingame.team1army, self.maingame.team2army,
                    #                                                         self.maingame.team1poslist, self.maingame.allunitindex,
                    #                                                         self.maingame.enactment)
                    #     else:
                    #         self.maingame.allunitindex = self.switchfaction(self.maingame.team2army, self.maingame.team1army,
                    #                                                         self.maingame.team2poslist, self.maingame.allunitindex,
                    #                                                         self.maingame.enactment)
                    #     self.maingame.eventlog.addlog([0, str(self.leader[0].name) + "'s battalion surrender"], [0, 1])
                    #     self.maingame.setuparmyicon()
            #^ End retreat function

            #v skirmishing
            if self.hold == 1 and self.state not in (97,98,99):
                minrange = self.minrange # run away from enemy that reach minimum range
                if minrange < 50: minrange = 50 # for in case minrange is 0 (melee troop only)
                if list(self.neartarget.values())[0].distance_to(self.basepos) <= minrange: # if there is any enemy in minimum range
                    self.state = 96 # retreating
                    basetarget = self.basepos - (list(self.neartarget.values())[0] - self.basepos) # generate target to run away, opposite direction at same distance
                    if basetarget[0] < 1: # can't run away when reach corner of map same for below if elif
                        basetarget[0] = 1
                    elif basetarget[0] > 998:
                        basetarget[0] = 998
                    if basetarget[1] < 1:
                        basetarget[1] = 1
                    elif basetarget[1] > 998:
                        basetarget[1] = 998
                    self.set_target(basetarget) # set target position to run away
            #^ End skirmishing

            #v Fight state but no collided enemy now
            if self.state == 10 and self.battlesideid == [0,0,0,0]:
                if self.nocombat > 0:  # For avoiding battalion bobble between two collided enemy
                    self.nocombat += dt
                    if self.nocombat > 5 or (self.attacktarget != 0 and self.attacktarget.state != 10): # no combat or enemy retreat
                        self.nocombat = 0 # reset timer
                        self.combatpreparestate = False # reset combat prepare
                        self.gotcombatprepare = False # reset combat prepare
                        self.enemyprepareside = None # reset combat prepare
                        self.state = self.commandstate
                        if self.commandstate in (3,4,5,6): # previous command is to attack enemy
                            if self.attacktarget.state == 100: # if enemy already dead then stop
                                self.attacktarget = 0
                                self.set_target(self.frontpos)
                        else:
                            self.attacktarget = 0
                            self.baseattackpos = 0
                            self.set_target(self.commandtarget)
                            self.setrotate()
                else:
                    self.nocombat = 0.1
            else:
                self.nocombat = 0
            #^ End end of fight code

            #v Rotate Function
            if self.combatpreparestate and self.stopcombatmove == False: # Rotate army side to the enemyside during auto placement
                self.baseattackpos = self.attacktarget.allsidepos[self.enemyprepareside] # set attack position to enemy side
                self.setrotate(self.attacktarget.basepos) # rotate to enemy center position
            if self.angle != round(self.newangle) and self.stamina > 0 and (
                    self.hitbox[0].collide == 0 or self.combatpreparestate):
                self.rotatecal = abs(round(self.newangle) - self.angle) # amount of angle left to rotate
                self.rotatecheck = 360 - self.rotatecal # rotate distance used for preventing angle calculation bug (pygame rotate related)
                self.moverotate = True
                self.radians_angle = math.radians(360 - self.angle) # for allside rotate
                if self.angle < 0: # negative angle (rotate to left side)
                    self.radians_angle = math.radians(-self.angle)
                ## Rotate logic to continuously rotate based on angle and shortest length
                if self.state in (1, 3, 5):
                    self.rotatespeed = round(self.walkspeed * 50 / (self.armysquad.size / 2)) # rotate speed is based on move speed and battalion block size (not squad total number)
                    self.walk = True
                else:
                    self.rotatespeed = round(self.runspeed * 50 / (self.armysquad.size / 2))
                    self.run = True
                if self.rotatespeed > 20 or self.state == 10: self.rotatespeed = 20 # state 10 melee combat rotate is auto placement
                if self.rotatespeed < 1: # no less than speed 1, it will be too slow or can't rotate with speed 0
                    self.rotatespeed = 1
                rotatetiny = self.rotatespeed * dt # rotate little by little according to time
                if round(self.newangle) > self.angle: # rotate to angle more than the current one
                    if self.rotatecal > 180: # rotate with the smallest angle direction
                        self.angle -= rotatetiny
                        self.rotatecheck -= rotatetiny
                        if self.rotatecheck <= 0: self.angle = round(self.newangle) # if rotate pass target angle, rotate to target angle
                    else:
                        self.angle += rotatetiny
                        if self.angle > self.newangle: self.angle = round(self.newangle) # if rotate pass target angle, rotate to target angle
                elif round(self.newangle) < self.angle:  # rotate to angle less than the current one
                    if self.rotatecal > 180: # rotate with the smallest angle direction
                        self.angle += rotatetiny
                        self.rotatecheck -= rotatetiny
                        if self.rotatecheck <= 0: self.angle = round(self.newangle) # if rotate pass target angle, rotate to target angle
                    else:
                        self.angle -= rotatetiny
                        if self.angle < self.newangle: self.angle = round(self.newangle) # if rotate pass target angle, rotate to target angle
                self.rotate() # rotate sprite to new angle
                self.makeallsidepos() # generate new pos related to side
                self.frontpos = self.allsidepos[0]
                self.mask = pygame.mask.from_surface(self.image) # make new mask
            elif self.moverotate and self.angle == round(self.newangle):  # Finish rotate
                self.moverotate = False

                #v Perform range attack, can only enter range attack state after finishing rotate
                shootrange = self.maxrange
                if self.useminrange == 0: # use minimum range to shoot
                    shootrange = self.minrange
                if self.state in (5, 6) and ((self.attacktarget != 0 and self.basepos.distance_to(self.attacktarget.basepos) <= shootrange)
                                             or self.basepos.distance_to(self.baseattackpos) <= shootrange): # in shoot range
                    self.set_target(self.frontpos) # stop moving
                    self.rangecombatcheck = True # set range combat check to start shooting
                elif self.state == 11 and self.attacktarget != 0 and self.basepos.distance_to(
                        self.attacktarget.basepos) > shootrange and self.hold == 0:  # chase target if it go out of range and hold condition not hold
                    self.state = self.commandstate # set state to attack command state
                    self.rangecombatcheck = False # stop range combat check
                    self.set_target(self.attacktarget.basepos) # move to target
                    self.setrotate(self.basetarget) # also keep rotate to target
                #^ End range attack state
            #^ End rotate function

            #v Move function to given target position
            if self.frontpos != self.basetarget and self.rangecombatcheck == False:
                self.charging = False

                #v Chase target and rotate accordingly
                if self.state in (3, 4, 5, 6, 10) and self.commandstate in (3,4,5,6) and self.attacktarget != 0 \
                        and self.combatpreparestate == False and self.hold == 0:
                    cantchase = False
                    for side in self.battlesideid:
                        if (side != 0 and side != self.attacktarget.gameid) or (side == self.attacktarget.gameid and (self.combatpreparestate or self.gotcombatprepare)):
                            cantchase = True # hitbox got collided can no longer chase target
                            break
                    if cantchase == False and self.forcedmelee:
                        self.state = self.commandstate # resume attack command
                        side, side2 = self.attacktarget.allsidepos.copy(), {}
                        for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.frontpos)
                        side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])} # find which side of enemy is closest to this unit front side
                        self.set_target(self.attacktarget.allsidepos[list(side2.keys())[0]]) # set target to cloest enemy's side
                        self.baseattackpos = self.basetarget
                        self.setrotate(self.basetarget) # keep rotating while chasing
                ## ^End chase

                if self.state in (3, 4) and type(self.baseattackpos) != int and self.moverotate == False:
                    if self.baseattackpos.distance_to(self.frontpos) < 15:
                        self.charging = True
                if self.state not in (0, 97) and self.stamina > 0 and (self.retreattimer == 0 or self.retreattimer >= self.retreatmax):
                    side, side2 = self.allsidepos.copy(), {} # check for self hitbox collide according to which ever closest to the target position
                    for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.basetarget) # generate side 2 dict with side as key and distance as item
                    side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])} # sort side that is closest to target
                    if (self.hitbox[list(side2.keys())[0]].collide == 0 or self.combatpreparestate or (self.state in (3,4) and self.baseattackpos.distance_to(self.frontpos) < 8)) \
                            and self.moverotate == False and self.rotateonly == False: # can move if hitbox closest to target is not collided, only auto placement can bypass collide
                        move = self.basetarget - self.frontpos # distance between target and front side
                        move_length = move.length() # convert length
                        if move_length > 0.1: # not reach target yet
                            heightdiff = (self.height / self.sideheight[0]) ** 2 # walking down hill increase speed while walking up hill reduce speed
                            if self.state in (96, 98, 99) or self.revert: # retreat or revert use the side closest to target for checking height
                                heightdiff = (self.height / self.sideheight[list(side2.keys())[0]]) ** 2
                            move.normalize_ip()
                            if self.state in (1, 3, 5): # walking
                                move = move * self.walkspeed * heightdiff * dt # use walk speed
                                self.walk = True
                            else: #  self.state in (2, 4, 6, 10, 96, 98, 99), running
                                move = move * self.runspeed * heightdiff * dt # use run speed
                                self.run = True
                            # elif self.state == 10:
                            #     move = move * 3 * heightdiff * dt
                            if move.length() <= move_length: # move normally according to move speed
                                self.basepos += move
                                self.pos = self.basepos * (11 - self.viewmode)
                                self.rect.center = list(int(v) for v in self.pos) # list rect so the sprite gradually move to position
                            else:  # move length pass the target destination
                                move = self.basetarget - self.frontpos # simply change move to whatever remaining distance
                                self.basepos += move # adjust base position according to movement
                                self.pos = self.basepos * (11 - self.viewmode)
                                self.rect.center = self.pos # no need to do list movement
                                if self.combatpreparestate == False: # stop normally
                                    self.retreattimer = 0 # reset retreat
                                    self.retreatstart = False
                                    if self.battlesideid == [0,0,0,0]: # not getting hit by anything
                                        if self.attacktarget == 0 and self.rangecombatcheck == False: # no enemy target, this will be ignored and chasing code above will be used
                                            self.frontpos = self.commandtarget
                                            self.state = 0 # go idle
                                            self.revert = False # reset revert order
                                            self.commandstate = self.state # reset command state
                                            self.commandtarget = self.basetarget # reset command target
                                    else:
                                        self.state = 10 # enter fight state since it get hit
                                else:  # Rotate army to the enemy sharply to stop in combat prepare auto placement
                                    self.stopcombatmove = True # stop auto placement move
                                    self.setrotate(self.attacktarget.basepos) # set rotate angle to enemy center
                                    self.angle = self.newangle # no need to gradually rotate, do it only once
                                    self.rotate() # final rotate

                            #v move to shoot, stop moving if reach shoot range instead of target
                            if self.state in (5, 6):
                                shootrange = self.maxrange
                                if self.useminrange == 0: # user set to use min shoot range
                                    shootrange = self.minrange
                                if (self.attacktarget != 0 and self.basepos.distance_to(self.attacktarget.basepos) <= shootrange) or \
                                        self.basepos.distance_to(self.baseattackpos) <= shootrange:
                                    self.set_target(self.frontpos) # stop moving when reach shoot range
                                    self.rangecombatcheck = True # start range combat
                            #^ End move to shoot
                        else: # either reach target or move distance left is too small
                            if self.combatpreparestate == False: # not in melee auto placement
                                self.retreattimer = 0 # reset all retreat
                                self.retreatstart = False
                                if self.battlesideid == [0, 0, 0, 0]: # not in melee combat
                                    if self.attacktarget == 0 and self.rangecombatcheck == False: # reset all target
                                        self.frontpos = self.commandtarget
                                        self.state = 0 # idle
                                        self.revert = False
                                        if self.commandtarget == self.basetarget:
                                            self.commandstate = self.state # command done
                                else:
                                    self.state = 10
                            else:  # Rotate army to the enemy sharply to stop in melee auto placement
                                self.stopcombatmove = True
                                self.setrotate(self.attacktarget.basepos)
                                self.angle = self.newangle
                                self.rotate()
                        self.makeallsidepos() # make new all side position after moving
                        self.frontpos = self.allsidepos[0] # get new front side position
                        self.height = self.gamemapheight.getheight(self.basepos) # get new height at new position
                        self.sideheight = [self.gamemapheight.getheight(self.allsidepos[0]), self.gamemapheight.getheight(self.allsidepos[1]),
                                           self.gamemapheight.getheight(self.allsidepos[2]), self.gamemapheight.getheight(self.allsidepos[3])]  # get new height for other sides
                        self.mask = pygame.mask.from_surface(self.image) # make new mask
                    elif self.rotateonly and self.moverotate == False: # if rotate only order
                        self.state = 0 # idle state
                        self.commandstate = self.state
                        self.set_target(self.frontpos) # rotate only so reset target to front side
                        self.commandtarget = self.basetarget
                        self.rotateonly = False # reset rotate only condition
                        self.makeallsidepos() # make new all side position after finish rotate
                        self.frontpos = self.allsidepos[0]
                        self.height = self.gamemapheight.getheight(self.basepos)
                        self.sideheight = [self.gamemapheight.getheight(self.allsidepos[0]), self.gamemapheight.getheight(self.allsidepos[1]),
                                           self.gamemapheight.getheight(self.allsidepos[2]), self.gamemapheight.getheight(self.allsidepos[3])]
                        self.mask = pygame.mask.from_surface(self.image) # make new mask
            #^ End move function

            #v Collapse related
            if self.stamina <= 0: # battalion only enter collpase state when all squad stamina is 0
                self.state = 97 # Enter collaspse state
            if self.state == 97: # Awake from collapse when there is no squad in collaspe state
                awake = True
                for squad in self.squadsprite: # check if any squad in collapse state
                    if squad.state == 97: # can't stop collapse state yet if any squad still in collaspe state
                        awake = False
                        break # no need to find any squad still in collapse state
                if awake == True:
                    self.state = self.commandstate # resume previous order
            #^ End colapse related

            #v no longer in combat, reset combat state
            if self.battlesideid == [0,0,0,0] and self.state != 10:
                self.gotcombatprepare = False
                if self.combatpreparestate:
                    self.combatpreparestate = False # reset combatprepare
                    self.enemyprepareside = None  # reset combat prepare
                    self.stopcombatmove = False
            #^ End reset combat state

            #v Destroy when troop number reach 0
            if self.troopnumber <= 0:
                self.stamina, self.morale, self.speed = 0, 0, 0
                for leader in self.leader:
                    if leader.state not in (96, 97, 98, 100):  ## Leaders may get flee/captured/die when battalion destroyed
                        leader.state = 96
                        for hitbox in self.hitbox:
                            if hitbox.collide != 0 and random.randint(0, 1) == 0: # If there is hitbox collide, random change to get capture
                                leader.state = 97
                                if random.randint(0, 1) == 0: # Also random chance to die
                                    leader.state = 100
                self.state = 100
            #^ End destroy

            #v remove when go pass the map border for any reason
            if self.basepos[0] < 0 or self.basepos[0] > 999 or self.basepos[1] < 0 or self.basepos[
                1] > 999:  # Remove unit when it go out of battlemap
                self.maingame.allunitindex.remove(self.gameid)
                self.leader[0].state = 98 # leader gone missing
                self.leader[0].health = 0
                self.leader[0].gone()
                self.kill()
                for hitbox in self.hitbox:
                    hitbox.kill()
            #^ End pass map border remove

        else: # dead battalion
            #v battalion just got killed
            if self.gotkilled == False:
                if self.team == 1:
                    self.die(self.maingame, self.maingame.team1army, self.maingame.team2army)
                else:
                    self.die(self.maingame, self.maingame.team2army, self.maingame.team1army)
                self.maingame.setuparmyicon() # reset army icon (remove dead one)
                self.maingame.eventlog.addlog([0, str(self.leader[0].name) + "'s battalion is destroyed"], [0, 1]) # put destroyed event in war and army log
            #^ End got killed

    def set_target(self, pos):
        """set new target, scale target from basetarget according to zoom scale"""
        self.basetarget = pygame.Vector2(pos) # Set new base target
        self.target = self.basetarget * (11 - self.viewmode) # Re-calculate target with current viewmode

    def rotate(self):
        """rotate sprite"""
        self.image = pygame.transform.rotate(self.image_original, self.angle) # Rotate the image
        self.rect = self.image.get_rect(center=self.pos)  # Create a new rect with the center of the sprite

    def setrotate(self, settarget=0):
        """set target and new angle for sprite rotation"""
        self.basepreviousposition = self.basepos
        self.previousposition = self.basepreviousposition * (11 - self.viewmode)
        if settarget == 0: # For auto chase rotate
            myradians = math.atan2(self.basetarget[1] - self.basepreviousposition[1], self.basetarget[0] - self.basepreviousposition[0])
        else: # Command move or rotate
            myradians = math.atan2(settarget[1] - self.basepreviousposition[1], settarget[0] - self.basepreviousposition[0])
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
        """Process input order into state and unit target action"""
        self.state = 1
        self.rotateonly = False
        self.forcedmelee = False
        self.revert = False
        self.attacktarget = 0
        self.baseattackpos = 0
        if keystate[pygame.K_LALT] or (whomouseover != 0 and (self.team != whomouseover.team)): # attack
            if self.ammo <= 0 or keystate[pygame.K_LCTRL]: # no ammo to shoot or forced attack command
                self.forcedmelee = True
                self.state = 3 # move to melee
            elif self.ammo > 0:  # have ammo to shoot
                self.state = 5 # Move to range attack
            if keystate[pygame.K_LALT]: # attack specific location
                self.set_target(mouse_pos[1])
                if self.ammo > 0:
                    self.baseattackpos = mouse_pos[1]
            else:
                self.attacktarget = whomouseover
                self.baseattackpos = whomouseover.basepos
        if double_mouse_right or self.runtoggle == 1:
            self.state += 1 # run state
        self.commandstate = self.state
        self.rangecombatcheck = False
        if keystate[pygame.K_LSHIFT]: self.rotateonly = True
        self.set_target(mouse_pos[1])
        self.commandtarget = self.basetarget
        self.setrotate()
        if keystate[pygame.K_z] == True: ## Revert unit without rotate, cannot run in this state
            self.newangle = self.angle
            self.moverotate = False
            self.revert = True
            # if double_mouse_right or self.runtoggle:
            #     self.state -= 1
        if self.charging: # change order when charging will cause authority penalty
            self.leader[0].authority -= self.authpenalty
            self.authrecal()

    def processretreat(self, mouse_pos, whomouseover):
        if whomouseover == 0: # click at empty map
            self.state = 96 # retreat state (not same as 98)
            self.commandstate = self.state # command retreat
            self.rotateonly = False
            self.forcedmelee = False
            self.attacktarget = 0
            self.baseattackpos = 0
            self.moverotate = False # will not rotate to move
            self.leader[0].authority -= self.authpenalty # retreat reduce main leader authority
            self.authrecal()
            self.retreattimer = 0.1 # start retreat timer
            self.retreatstart = True # start retreat process
            self.set_target(mouse_pos[1])
            self.commandtarget = self.basetarget
            self.combatpreparestate = False # remove auto placement

    def command(self, mouse_pos, mouse_right, double_mouse_right, whomouseover, keystate, othercommand=0):
        """othercommand is special type of command such as stop all action, raise flag, decimation, duel and so on"""
        if self.control and self.state != 100:
            posmask = mouse_pos[0][0] - self.rect.x, mouse_pos[0][1] - self.rect.y # for checking if right click in mask or not. if not, move unit
            if mouse_right and mouse_pos[1][0] >= 1 and mouse_pos[1][0] < 998 and mouse_pos[1][1] >= 1 and mouse_pos[1][1] < 998:
                if self.state not in (10, 97, 98, 99, 100): # can move normally
                    try:  # if click within rect
                        if self.mask.get_at(posmask) == 0: # not in mask
                            self.processcommand(mouse_pos, double_mouse_right, whomouseover, keystate)
                    except:  # if click outside of rect and mask
                        self.processcommand(mouse_pos, double_mouse_right, whomouseover, keystate)
                elif self.state == 10:  # Enter retreat state if in combat and move command issue
                    try: # if click within rect
                        if self.mask.get_at(posmask) == 0: # not in mask
                            self.processretreat(mouse_pos, whomouseover) # retreat
                    except: # if click outside of rect and mask
                        self.processretreat(mouse_pos, whomouseover) # retreat
            elif othercommand == 1 and self.state not in (10, 97, 98, 99, 100):  # Pause all action except combat or broken
                if self.charging: # TODO change pause option to come into effect much slower when charging
                    self.leader[0].authority -= self.authpenalty # decrease authority of the first leader for stop charge
                    self.authrecal() # recal authority
                self.state = 0 # go into idle state
                self.commandstate = self.state # reset command state
                self.set_target(self.frontpos) # set target at self
                self.commandtarget = self.basetarget # reset command target
                self.rangecombatcheck = False # reset range combat check
                self.setrotate() # set rotation target

    def switchfaction(self, oldgroup, newgroup, oldposlist, allunitindex, enactment):
        """Change army group and gameid when change side"""
        self.colour = (144, 167, 255) # team1 colour
        self.control = True #TODO need to change later when player can choose team
        self.team = 1 # change to team 1
        if self.gameid < 2000: # originally team 1, new team would be 2
            self.team = 2 # change to team 2
            self.colour = (255, 114, 114) # team2 colour
            if enactment == False:
                self.control = False
        newgameid = newgroup[-1].gameid + 1
        oldgroup.remove(self) # remove from old team group
        newgroup.append(self) # add to new team group
        oldposlist.pop(self.gameid) # remove from old pos list
        allunitindex = [newgameid if index == self.gameid else index for index in allunitindex] # replace index in allunitindex
        self.gameid = newgameid # change game id
        self.recreatesprite()
        self.changescale() # reset scale to the current zoom
        self.icon.changeimage(changeside=True) # change army icon to new team
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
