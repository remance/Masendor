import random
import numpy as np
import pygame
import pygame.freetype
import math
from pygame.transform import scale
from gamescript import rangeattack, gamelongscript

class Subunit(pygame.sprite.Sprite):
    images = []
    maingame = None
    gamemap = None # base map
    gamemapfeature = None # feature map
    gamemapheight = None # height map
    dmgcal = gamelongscript.dmgcal
    weaponlist = None
    armourlist = None
    statlist = None
    createtroopstat = gamelongscript.createtroopstat
    rotationxy = gamelongscript.rotationxy
    setrotate = gamelongscript.setrotate
    maxzoom = 10 # max zoom allow
    # use same position as subunit front index 0 = front, 1 = left, 2 = rear, 3 = right

    def __init__(self, unitid, gameid, parentunit, position, starthp, startstamina, unitscale):
        """Although subunit in code, this is referred as sub-subunit ingame"""
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.wholastselect = None
        self.mouse_over = False
        self.leader = None # Leader in the sub-subunit if there is one, got add in leader gamestart
        self.boardpos = None  # Used for event log position of subunit (Assigned in maingame subunit setup)
        self.walk = False # currently walking
        self.run = False # currently running
        self.frontline = False # on front line of unit or not
        self.unitleader = False # contain the general or not, making it leader subunit
        self.attacktarget = None
        self.meleetarget = None
        self.closetarget = None
        self.parentunit = parentunit # reference to the parent battlion of this subunit

        self.enemyfront = [] # list of front collide sprite
        self.enemyside = [] # list of side collide sprite
        self.friendfront = [] # list of friendly front collide sprite
        self.team = self.parentunit.team
        if self.team == 1: # add sprite to team subunit group for collision
            groupcollide = self.maingame.team1subunit
        elif self.team == 2:
            groupcollide = self.maingame.team2subunit
        groupcollide.add(self)

        self.statuslist = self.parentunit.statuslist

        self.gameid = gameid # ID of this subunit
        self.unitid = int(unitid) # ID of preset used for this subunit

        self.angle = self.parentunit.angle
        self.newangle = self.parentunit.angle
        self.radians_angle = math.radians(360 - self.angle)  # radians for apply angle to position (allsidepos and subunit)
        self.parentangle = self.parentunit.angle # angle subunit will face when not moving or

        self.haveredcorner = False
        self.state = 0 # Current subunit state, similar to parentunit state
        self.timer = 0 # may need to use random.random()
        self.movetimer = 0 # timer for moving to front position before attacking nearest enemy
        self.chargemomentum = 1 # charging momentum to reach target before choosing nearest enemy
        self.magazinenow = 0
        self.zoom = 1
        self.lastzoom = 10

        self.getfeature = self.gamemapfeature.getfeature
        self.getheight = self.gamemapheight.getheight

        #v Setup troop stat
        self.createtroopstat(self.team, self.statlist.unitlist[self.unitid].copy(), unitscale, starthp, startstamina)

        self.criteffect = 1 # default critical effect
        self.frontdmgeffect = 1 # default frontal damage
        self.sidedmgeffect = 1 # default side damage

        self.corneratk = False # cannot attack corner enemy by default
        self.tempunbraekable = False
        self.tempfulldef = False

        self.authpenalty = self.baseauthpenalty
        self.hpregen = self.basehpregen
        self.staminaregen = self.basestaminaregen
        self.inflictstatus = self.baseinflictstatus
        self.elemmelee = self.baseelemmelee
        self.elemrange = self.baseelemrange
        #^ End setup stat

        #v Subunit block team colour
        image = self.images[0].copy()  # Subunit block blue colour for team1 for shown in inspect ui
        if self.team == 2:
            image = self.images[13].copy()

        self.image = pygame.Surface((image.get_width()+1, image.get_height()+1), pygame.SRCALPHA) # subunit sprite image
        pygame.draw.circle(self.image, self.parentunit.colour, (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2)

        if self.unittype == 2: # cavalry draw line on block
            pygame.draw.line(image, (0, 0, 0), (0, 0), (image.get_width(), image.get_height()), 2)
            radian = 45 * 0.0174532925 # top left
            start = (self.image.get_width()/4 * math.cos(radian), self.image.get_width()/4 * math.sin(radian)) # draw line from 45 degree in circle
            radian = 225 * 0.0174532925 # bottom right
            end = (self.image.get_width() * -math.cos(radian), self.image.get_width() * -math.sin(radian)) # drow line to 225 degree in circle
            pygame.draw.line(self.image, (0, 0, 0), start, end, 2)

        self.imageblock = image.copy() # image shown in inspect ui as square instead of circle

        self.selectedimage = pygame.Surface((image.get_width(), image.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(self.selectedimage, (255, 255, 255, 150), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2)
        pygame.draw.circle(self.selectedimage, (0, 0, 0, 255), (image.get_width() / 2, image.get_height() / 2), image.get_width() / 2, 1)
        self.selectedimage_original, self.selectedimage_original2 = self.selectedimage.copy(), self.selectedimage.copy()
        self.selectedimagerect = self.selectedimage.get_rect(topleft=(0,0))
        #^ End subunit block team colour

        #v health circle image setup
        self.healthimage = self.images[1]
        self.healthimagerect = self.healthimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.healthimage, self.healthimagerect)
        self.imageblock.blit(self.healthimage, self.healthimagerect)
        #^ End health circle

        #v stamina circle image setup
        self.staminaimage = self.images[6]
        self.staminaimagerect = self.staminaimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.staminaimage, self.staminaimagerect)
        self.imageblock.blit(self.staminaimage, self.staminaimagerect)
        #^ End stamina circle

        #v weapon class icon in middle circle
        if self.unitclass == 0: # melee weapon image as main
            image1 = self.weaponlist.imgs[self.weaponlist.weaponlist[self.meleeweapon[0]][-3]] # image on subunit sprite
        else: # range weapon image
            image1 = self.weaponlist.imgs[self.weaponlist.weaponlist[self.rangeweapon[0]][-3]]
        image1rect = image1.get_rect(center=self.image.get_rect().center)
        self.image.blit(image1, image1rect)
        self.imageblock.blit(image1, image1rect)
        self.imageblock_original = self.imageblock.copy()

        self.cornerimagerect = self.images[11].get_rect(center=self.imageblock.get_rect().center) # red corner when take dmg shown in image block
        #^ End weapon icon

        self.image_original =  self.image.copy()  # original for rotate #TODO enlarge image a bit so no empty space between two sprite when click
        self.image_original2 =  self.image.copy() # original2 for saving original notclicked
        self.image_original3 = self.image.copy() # original3 for saving original zoom level

        #v position related
        self.armypos = (position[0]/10, position[1]/10) # position in parentunit sprite
        battaliontopleft = pygame.Vector2(self.parentunit.basepos[0] - self.parentunit.basewidthbox / 2,
                                          self.parentunit.basepos[1] - self.parentunit.baseheightbox / 2) # get topleft corner position of parentunit to calculate true pos
        self.basepos = pygame.Vector2(battaliontopleft[0] + self.armypos[0], battaliontopleft[1] + self.armypos[1]) # true position of subunit in map
        self.lastpos = self.basepos

        self.movementqueue = []
        self.combatmovequeue = []
        self.basetarget = self.basepos # basetarget to move
        self.commandtarget = self.basepos # actual basetarget outside of combat
        self.pos = self.basepos * self.zoom  # pos is for showing on screen

        #v Generate front side position
        self.imageheight = (self.image_original.get_height() - 1) / 20 # get real half height of circle sprite

        #v rotate the new front side according to sprite rotation
        self.frontsidepos = (self.basepos[0], (self.basepos[1] - self.imageheight))
        self.frontsidepos = self.rotationxy(self.basepos, self.frontsidepos, self.radians_angle)

        self.attackpos = self.parentunit.baseattackpos
        self.terrain, self.feature = self.getfeature(self.basepos, self.gamemap)  # get new terrain and feature at each subunit position
        self.height = self.gamemapheight.getheight(self.basepos)  # Current terrain height
        self.frontheight = self.gamemapheight.getheight(self.frontsidepos) # terrain height at front position
        #^ End position related

        self.rect = self.image.get_rect(center=self.pos)

    def zoomscale(self):
        """camera zoom change and rescale the sprite and position scale"""
        self.image_original = self.image_original3.copy() # reset image for new scale
        scalewidth = self.image_original.get_width() * self.zoom / self.maxzoom
        scaleheight = self.image_original.get_height() * self.zoom / self.maxzoom
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.image_original2 = self.image.copy()

        if self.parentunit.selected and self.state != 100:
            self.selectedimage_original = pygame.transform.scale(self.selectedimage_original2, (int(self.dim[0]), int(self.dim[1])))

        self.changeposscale()
        self.rotate()
        self.mask = pygame.mask.from_surface(self.image)  # make new mask for collision

    def changeposscale(self):
        """Change position variable to new camera scale"""
        self.pos = self.basepos * self.zoom
        self.rect = self.image.get_rect(center=self.pos)

    def useskill(self, whichskill):
        if whichskill == 0:  # charge skill need to seperate since charge power will be used only for charge skill
            skillstat = self.skill[list(self.skill)[0]].copy() # get skill stat
            self.skilleffect[self.chargeskill] = skillstat # add stat to skill effect
            self.skillcooldown[self.chargeskill] = skillstat[4] # add skill cooldown
        else:  # other skill
            skillstat = self.skill[whichskill].copy() # get skill stat
            self.skilleffect[whichskill] = skillstat # add stat to skill effect
            self.skillcooldown[whichskill] = skillstat[4] # add skill cooldown
        self.stamina -= skillstat[9]
        # self.skillcooldown[whichskill] =

    # def receiveskill(self,whichskill):

    def checkskillcondition(self):
        """Check which skill can be used, cooldown, condition state, discipline, stamina are checked. charge skill is excepted from this check"""
        if self.useskillcond == 1 and self.staminastate < 50: # reserve 50% stamina, don't use any skill
            self.availableskill = []
        elif self.useskillcond == 2 and self.staminastate < 25: # reserve 25% stamina, don't use any skill
            self.availableskill = []
        else: # check all skill
            self.availableskill = [skill for skill in self.skill if skill not in self.skillcooldown.keys()
                                   and self.state in self.skill[skill][6] and self.discipline >= self.skill[skill][8]
                                   and self.stamina > self.skill[skill][9] and skill != self.chargeskill]

    def findnearbysquad(self):
        """Find nearby friendly squads in the same parentunit for applying buff"""
        self.nearbysquadlist = []
        cornersquad = []
        for rowindex, rowlist in enumerate(self.parentunit.armysubunit.tolist()):
            if self.gameid in rowlist:
                if rowlist.index(self.gameid) - 1 != -1:  #get subunit from left if not at first column
                    self.nearbysquadlist.append(self.parentunit.spritearray[rowindex][rowlist.index(self.gameid) - 1]) # index 0
                else: # not exist
                    self.nearbysquadlist.append(0) # add number 0 instead

                if rowlist.index(self.gameid) + 1 != len(rowlist):  #get subunit from right if not at last column
                    self.nearbysquadlist.append(self.parentunit.spritearray[rowindex][rowlist.index(self.gameid) + 1]) # index 1
                else: # not exist
                    self.nearbysquadlist.append(0) # add number 0 instead

                if rowindex != 0:  #get top subunit
                    self.nearbysquadlist.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid)]) # index 2
                    if rowlist.index(self.gameid) - 1 != -1:  # get top left subunit
                        cornersquad.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid) - 1]) # index 3
                    else: # not exist
                        cornersquad.append(0) # add number 0 instead
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get top right
                        cornersquad.append(self.parentunit.spritearray[rowindex - 1][rowlist.index(self.gameid) + 1]) # index 4
                    else: # not exist
                        cornersquad.append(0) # add number 0 instead
                else: # not exist
                    self.nearbysquadlist.append(0) # add number 0 instead

                if rowindex != len(self.parentunit.spritearray) - 1:  # get bottom subunit
                    self.nearbysquadlist.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid)]) # index 5
                    if rowlist.index(self.gameid) - 1 != -1:  # get bottom left subunit
                        cornersquad.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid) - 1]) # index 6
                    else: # not exist
                        cornersquad.append(0) # add number 0 instead
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get bottom  right subunit
                        cornersquad.append(self.parentunit.spritearray[rowindex + 1][rowlist.index(self.gameid) + 1]) # index 7
                    else: # not exist
                        cornersquad.append(0) # add number 0 instead
                else: # not exist
                    self.nearbysquadlist.append(0) # add number 0 instead
        self.nearbysquadlist = self.nearbysquadlist + cornersquad

    def statustonearby(self, aoe, id, statuslist):
        """apply status effect to nearby subunit depending on aoe stat"""
        if aoe in (2, 3):
            if aoe > 1: # only direct nearby friendly subunit
                for squad in self.nearbysquadlist[0:4]:
                    if squad != 0 and squad.state != 100: # only apply to exist and alive squads
                        squad.statuseffect[id] = statuslist # apply status effect
            if aoe > 2: # all nearby including corner friendly subunit
                for squad in self.nearbysquadlist[4:]:
                    if squad != 0 and squad.state != 100: # only apply to exist and alive squads
                        squad.statuseffect[id] = statuslist # apply status effect
        elif aoe == 4: # apply to whole parentunit
            for squad in self.parentunit.spritearray.flat:
                if squad.state != 100: # only apply to alive squads
                    squad.statuseffect[id] = statuslist # apply status effect

    def thresholdcount(self, elem, t1status, t2status):
        """apply elemental status effect when reach elemental threshold"""
        if elem > 50:
            self.statuseffect[t1status] = self.statuslist[t1status].copy() # apply tier 1 status
            if elem > 100:
                self.statuseffect[t2status] = self.statuslist[t2status].copy() # apply tier 2 status
                del self.statuseffect[t1status] # remove tier 1 status
                elem = 0 # reset elemental count
        return elem

    def findeclosetarget(self):
        """Find close enemy sub-unit to move to fight"""
        closelist = {subunit: subunit.basepos.distance_to(self.basepos) for subunit in
                     self.meleetarget.parentunit.subunitsprite}
        closelist = dict(sorted(closelist.items(), key=lambda item: item[1]))
        maxrandom = 3
        if len(closelist) < 4:
            maxrandom = len(closelist) - 1
            if maxrandom < 0:
                maxrandom = 0
        if len(closelist) > 0:
            closetarget = list(closelist.keys())[random.randint(0, maxrandom)]
            # if closetarget.basepos.distance_to(self.basepos) < 20: # in case can't find close target
            self.closetarget = closetarget

    def statusupdate(self, thisweather=None):
        """calculate stat from stamina, morale state, skill, status, terrain"""

        if self.haveredcorner:  # have red corner reset image
            self.imageblock.blit(self.imageblock_original, self.cornerimagerect)
            self.haveredcorner = False

        #v reset stat to default and apply morale, stamina, command buff to stat
        if self.maxstamina > 100: # Max stamina gradually decrease over time - (self.timer * 0.05)
            self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.maxstamina-(self.timer*0.05), round(self.maxstamina * 0.75), round(
                self.maxstamina * 0.5), round(self.maxstamina * 0.25)
        self.morale = self.basemorale
        self.authority = self.parentunit.authority # parentunit total authoirty
        self.commandbuff = self.parentunit.commandbuff[self.unittype] * 100 # command buff from main leader according to this subunit subunit type
        self.discipline = self.basediscipline
        self.attack = self.baseattack
        self.meleedef = self.basemeleedef
        self.rangedef = self.baserangedef
        self.accuracy = self.baseaccuracy
        self.reload = self.basereload
        self.chargedef = self.basechargedef
        self.speed = self.basespeed
        self.charge = self.basecharge
        self.shootrange = self.baserange

        self.criteffect = 1 # default critical effect
        self.frontdmgeffect = 1 # default frontal damage
        self.sidedmgeffect = 1 # default side damage

        self.corneratk = False # cannot attack corner enemy by default
        self.tempunbraekable = False
        self.tempfulldef = False

        self.authpenalty = self.baseauthpenalty
        self.hpregen = self.basehpregen
        self.staminaregen = self.basestaminaregen
        self.inflictstatus = self.baseinflictstatus
        self.elemmelee = self.baseelemmelee
        self.elemrange = self.baseelemrange
        #^ End default stat

        if self.height > 100: #  apply height to range for height that is higher than 100 #TODO redo height range cal to use enemy basetarget height as well
            self.shootrange = self.shootrange + (self.height / 10)

        #v Apply status effect from trait
        if len(self.trait) > 1:
            for trait in self.trait.values():
                if trait[18] != [0]:
                    for effect in trait[18]: #aplly status effect from trait
                        self.statuseffect[effect] = self.statuslist[effect].copy()
                        if trait[1] > 1:  # status buff range to nearby friend
                            self.statustonearby(trait[1], effect, self.statuslist[effect].copy())
        #^ End trait

        #v apply effect from weather"""
        weathertemperature = 0
        if thisweather is not None:
            weather = thisweather
            self.attack += weather.meleeatk_buff
            self.meleedef += weather.meleedef_buff
            self.rangedef += weather.rangedef_buff
            self.armour += weather.armour_buff
            self.speed += weather.speed_buff
            self.accuracy += weather.accuracy_buff
            self.reload += weather.reload_buff
            self.charge += weather.charge_buff
            self.chargedef += weather.chargedef_buff
            self.hpregen += weather.hpregen_buff
            self.staminaregen += weather.staminaregen_buff
            self.morale += (weather.morale_buff * self.mental)
            self.discipline += weather.discipline_buff
            if weather.elem[0] != 0: # Weather can cause elemental effect such as wet
                self.elemcount[weather.elem[0]] += ((weather.elem[1] * (100 - self.elemresist[weather.elem[0]]) / 100))
            weathertemperature = weather.temperature
        #^ End weather

        #v Map feature modifier to stat
        mapfeaturemod = self.gamemapfeature.featuremod[self.feature]
        if mapfeaturemod[self.featuremod] != 1: # speed/charge
            speedmod = mapfeaturemod[self.featuremod] # get the speed mod appropiate to subunit type
            self.speed *= speedmod
            self.charge *= speedmod

        if mapfeaturemod[self.featuremod + 1] != 1: # melee attack
            # combatmod = self.parentunit.gamemapfeature.featuremod[self.parentunit.feature][self.featuremod + 1]
            self.attack *= mapfeaturemod[self.featuremod + 1] # get the attack mod appropiate to subunit type

        if mapfeaturemod[self.featuremod + 2] != 1: # melee/charge defense
            combatmod = mapfeaturemod[self.featuremod + 2] # get the defence mod appropiate to subunit type
            self.meleedef *= combatmod
            self.chargedef *= combatmod

        self.rangedef += mapfeaturemod[7] # range defense bonus from terrain bonus
        self.accuracy -= (mapfeaturemod[7]/2) # range def bonus block subunit sight as well so less accuracy
        self.discipline += mapfeaturemod[9]  # discipline defense bonus from terrain bonus

        if mapfeaturemod[11] != [0]: # Some terrain feature can also cause status effect such as swimming in water
            if 1 in mapfeaturemod[11]: # Shallow water type terrain
                self.statuseffect[31] = self.statuslist[31].copy()  # wet
            if 5 in mapfeaturemod[11]: # Deep water type terrain
                self.statuseffect[93] = self.statuslist[93].copy()  # drench

                if self.weight > 60 or self.stamina <= 0: # weight too much or tired will cause drowning
                    self.statuseffect[102] = self.statuslist[102].copy() # Drowning

                elif self.weight > 30:  # Medium weight subunit has trouble travel through water and will sink and progressively lose troops
                    self.statuseffect[101] = self.statuslist[101].copy() # Sinking

                elif self.weight < 30:  # Light weight subunit has no trouble travel through water
                    self.statuseffect[104] = self.statuslist[104].copy() # Swiming

            if 2 in mapfeaturemod[11]:  # Rot type terrain
                self.statuseffect[54] = self.statuslist[54].copy()

            if 3 in mapfeaturemod[11]:  # Poison type terrain
                self.elemcount[4] += ((100 - self.elemresist[5]) / 100)
        # self.hidden += self.parentunit.gamemapfeature[self.parentunit.feature][6]
        #^ End map feature

        #v Temperature mod function from terrain and weather
        tempreach = mapfeaturemod[10] + weathertemperature # temperature the subunit will change to based on current terrain feature and weather
        for status in self.statuseffect.values():
            tempreach += status[19] # add more from status effect
        if tempreach < 0: # cold temperature
            tempreach = tempreach * (100 - self.coldres) / 100 # lowest temperature the subunit will change based on cold resist
        else: # hot temperature
            tempreach = tempreach * (100 - self.heatres) / 100 # highest temperature the subunit will change based on heat resist

        if self.tempcount != tempreach: # move tempcount toward tempreach
            if tempreach > 0:
                if self.tempcount < tempreach:
                    self.tempcount += (100 - self.heatres) / 100 * self.timer # increase subunit temperature, rate depends on heat resistance (negative make rate faster)
            elif tempreach < 0:
                if self.tempcount > tempreach:
                    self.tempcount -= (100 - self.coldres) / 100 * self.timer # reduce subunit temperature, rate depends on cold resistance
            else: # tempreach is 0, subunit temp revert back to 0
                if self.tempcount > 0:
                    self.tempcount -= (1 + self.heatres) / 100 * self.timer # revert faster with higher resist
                else:
                    self.tempcount += (1 + self.coldres) / 100 * self.timer
        #^ End temperature

        #v Apply effect from skill
        if len(self.skilleffect) > 0:
            for status in self.skilleffect:  # apply elemental effect to dmg if skill has element
                calstatus = self.skilleffect[status]
                if calstatus[1] == 0 and calstatus[31] != 0: # melee elemental effect
                    self.elemmelee = int(calstatus[31])
                elif calstatus[1] == 1 and calstatus[31] != 0: # range elemental effect
                    self.elemrange = int(calstatus[31])
                self.attack = self.attack * calstatus[10]
                self.meleedef = self.meleedef * calstatus[11]
                self.rangedef = self.rangedef * calstatus[12]
                self.speed = self.speed * calstatus[13]
                self.accuracy = self.accuracy * calstatus[14]
                self.shootrange = self.shootrange * calstatus[15]
                self.reload = self.reload / calstatus[16] # different than other modifier the higher mod reduce reload time (decrease stat)
                self.charge = self.charge * calstatus[17]
                self.chargedef = self.chargedef + calstatus[18]
                self.hpregen += calstatus[19]
                self.staminaregen += calstatus[20]
                self.morale = self.morale + (calstatus[21] * self.mental)
                self.discipline = self.discipline + calstatus[22]
                # self.sight += calstatus[18]
                # self.hidden += calstatus[19]
                self.criteffect = round(self.criteffect * calstatus[23], 0)
                self.frontdmgeffect = round(self.frontdmgeffect * calstatus[24], 0)
                if calstatus[2] in (2, 3) and calstatus[24] != 100:
                    self.sidedmgeffect = round(self.sidedmgeffect * calstatus[24], 0)
                    if calstatus[2] == 3: self.corneratk = True # if aoe 3 mean it can attack nearby enemy squads in corner

                #v Apply status to friendly if there is one in skill effect
                if calstatus[27] != [0]:
                    for effect in calstatus[27]:
                        self.statuseffect[effect] = self.statuslist[effect].copy()
                        if self.statuseffect[effect][2] > 1:
                            self.statustonearby(self.statuseffect[effect][2], effect, self.statuslist)
                        # if status[2] > 1:
                        #     self.parentunit.armysubunit
                        # if status[2] > 2:
                #^ End apply status to

                self.bonusmoraledmg += calstatus[28]
                self.bonusstaminadmg += calstatus[29]
                if calstatus[30] != [0]: # Apply inflict status effect to enemy from skill to inflict list
                    for effect in calstatus[30]:
                        if effect != [0]: self.inflictstatus[effect] = calstatus[2]
            if self.chargeskill in self.skilleffect:
                self.authpenalty += 0.5 # higher authority penalty when attacking (retreat while attacking)
        #^ End skill effect

        #v Elemental effect
        if self.elemcount != [0, 0, 0, 0, 0]: # Apply effect if elem threshold reach 50 or 100
            self.elemcount[0] = self.thresholdcount(self.elemcount[0], 28, 92)
            self.elemcount[1] = self.thresholdcount(self.elemcount[1], 31, 93)
            self.elemcount[2] = self.thresholdcount(self.elemcount[2], 30, 94)
            self.elemcount[3] = self.thresholdcount(self.elemcount[3], 23, 35)
            self.elemcount[4] = self.thresholdcount(self.elemcount[4], 26, 27)
            self.elemcount = [elem - self.timer if elem > 0 else elem for elem in self.elemcount]
        #^ End elemental effect

        #v Temperature effect
        if self.tempcount > 50: # Hot
            self.statuseffect[96] = self.statuslist[96].copy()
            if self.tempcount > 100: # Extremely hot
                self.statuseffect[97] = self.statuslist[97].copy()
                del self.statuseffect[96]
        if self.tempcount < -50: # Cold
            self.statuseffect[95] = self.statuslist[95].copy()
            if self.tempcount < -100: # Extremely cold
                self.statuseffect[29] = self.statuslist[29].copy()
                del self.statuseffect[95]
        #^ End temperature effect related function

        #v Apply effect and modifer from status effect
        # """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no attack, 5 no skill, 6 no spell, 7 no exp gain,
        # 7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal""" Not implemented yet
        if len(self.statuseffect) > 0:
            for status in self.statuseffect:
                calstatus = self.statuslist[status]
                self.attack = self.attack * calstatus[4]
                self.meleedef = self.meleedef * calstatus[5]
                self.rangedef = self.rangedef * calstatus[6]
                self.armour = self.armour * calstatus[7]
                self.speed = self.speed * calstatus[8]
                self.accuracy = self.accuracy * calstatus[9]
                self.reload = self.reload / calstatus[10]
                self.charge = self.charge * calstatus[11]
                self.chargedef += calstatus[12]
                self.hpregen += calstatus[13]
                self.staminaregen += calstatus[14]
                self.morale = self.morale + (calstatus[15] * self.mental)
                self.discipline += calstatus[16]
                # self.sight += status[18]
                # self.hidden += status[19]
                if status == 1: # Fearless status
                    self.tempunbraekable = True
                elif status == 91: # All round defense status
                    self.tempfulldef = True
        #^ End status effect

        moralestate = self.morale
        if moralestate > 300: # morale more than 300 give no more benefit
            moralestate = 300
        self.moralestate = round((moralestate / self.maxmorale) * (self.authority / 100), 0)  # for using as modifer to stat
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.staminastatecal = self.staminastate / 100  # for using as modifer to stat
        self.discipline = (self.discipline * self.moralestate * self.staminastatecal) + self.parentunit.leadersocial[
            self.grade + 1] + (self.authority / 10)  # use morale, stamina, leader social vs grade and authority
        self.attack = (self.attack * (self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        self.meleedef = (self.meleedef * (
                    self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        self.rangedef = (self.rangedef * (self.moralestate + 0.1)) * self.staminastatecal + (
                    self.commandbuff / 2)  # use morale, stamina and half command buff
        self.accuracy = self.accuracy * self.staminastatecal + self.commandbuff  # use stamina and command buff
        self.reload = self.reload * (2 - self.staminastatecal)  # the less stamina, the higher reload time
        self.chargedef = (self.chargedef * (
                    self.moralestate + 0.1)) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff
        heightdiff = (self.height / self.frontheight) ** 2  # walking down hill increase speed while walking up hill reduce speed
        self.speed = self.speed * self.staminastatecal * heightdiff  # use stamina
        self.charge = (self.charge + self.speed) * (
                    self.moralestate + 0.1) * self.staminastatecal + self.commandbuff  # use morale, stamina and command buff

        #v Rounding up, add discipline to stat and forbid negative int stat
        self.discipline = round(self.discipline, 0)
        disciplinecal = self.discipline / 10
        self.attack = round((self.attack + disciplinecal), 0)
        self.meleedef = round((self.meleedef + disciplinecal), 0)
        self.rangedef = round((self.rangedef + disciplinecal), 0)
        self.armour = round(self.armour, 0)
        self.speed = round(self.speed + disciplinecal, 0)
        self.accuracy = round(self.accuracy, 0)
        self.reload = round(self.reload, 0)
        self.chargedef = round((self.chargedef + disciplinecal), 0)
        self.charge = round((self.charge + disciplinecal), 0)

        if self.ammo == 0 and self.magazinenow == 0:
            self.shootrange = 0
        if self.attack < 0: self.attack = 0
        if self.meleedef < 0: self.meleedef = 0
        if self.rangedef < 0: self.rangedef = 0
        if self.armour < 0: self.armour = 0
        elif self.armour > 100: self.armour = 100 # Armour cannot be higher than 100 since it is percentage reduction
        if self.speed < 1: self.speed = 1 # speed cannot be lower than 1 or it won't be able to move
        if self.accuracy < 0: self.accuracy = 0
        if self.reload < 0: self.reload = 0
        if self.charge < 0: self.charge = 0
        if self.chargedef < 0: self.chargedef = 0
        if self.discipline < 0: self.discipline = 0
        #^ End rounding up

        self.rotatespeed = 20 # rotate speed for subunit only use for self rotate not subunit rotate related
        # if self.parentunit.state in (10,96,97,98,99): self.rotatespeed = 10

        #v cooldown, active and effect timer function
        self.skillcooldown = {key: val - self.timer for key, val in self.skillcooldown.items()} # cooldown decrease overtime
        self.skillcooldown = {key: val for key, val in self.skillcooldown.items() if val > 0} # remove cooldown if time reach 0
        for a, b in self.skilleffect.items(): # Can't use dict comprehension here since value include all other skill stat
            b[3] -= self.timer
        self.skilleffect = {key: val for key, val in self.skilleffect.items() if val[3] > 0 and self.state in val[5]} # remove effect if time reach 0 or restriction state is not met
        for a, b in self.statuseffect.items():
            b[3] -= self.timer
        self.statuseffect = {key: val for key, val in self.statuseffect.items() if val[3] > 0}
        #^ End timer effect

    def findshootingtarget(self, parentstate):
        # get nearby enemy basetarget from list if not targeting anything yet
        self.attackpos = list(self.parentunit.neartarget.values())[0]  # replace attacktarget with enemy pos
        self.attacktarget = list(self.parentunit.neartarget.keys())[0]  # replace attacktarget with enemy id
        if self.shootrange >= self.attackpos.distance_to(self.basepos):
            self.state = 11
            if parentstate in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif parentstate in (2, 4, 6):  # Run and shoot
                self.state = 13

    def makefrontsidepos(self):
        # create new pos for front side of sprite
        self.frontsidepos = (self.basepos[0], (self.basepos[1] - self.imageheight))

        self.frontsidepos = self.rotationxy(self.basepos, self.frontsidepos, self.radians_angle)

    def makeposrange(self):
        # (range(int(max(0, round(self.basepos[0] - (self.imageheight - 1), 0))), int(min(1000, round(self.basepos[0] + self.imageheight, 0)))),
        #  range(int(max(0, round(self.basepos[1] - (self.imageheight - 1), 0))), int(min(1000, round(self.basepos[1] + self.imageheight, 0)))))

        self.posrange = (range(int(max(0, self.basepos[0] - (self.imageheight - 1))), int(min(1000, self.basepos[0] + self.imageheight))),
                         range(int(max(0, self.basepos[1] - (self.imageheight - 1))), int(min(1000, self.basepos[1] + self.imageheight))))
        # self.posrange = (range(int(max(0, self.basepos[0] - (self.imageheight))), int(min(1000, self.basepos[0] + self.imageheight+1))),
        #                  range(int(max(0, self.basepos[1] - (self.imageheight))), int(min(1000, self.basepos[1] + self.imageheight+1))))

    def gamestart(self, zoom):
        # run once when game start or subunit just get created
        self.zoom = zoom
        self.makefrontsidepos()
        self.makeposrange()
        self.zoomscale()
        self.findnearbysquad()

        #v reset stat to default and apply morale, stamina, command buff to stat
        if self.maxstamina > 100: # Max stamina gradually decrease over time - (self.timer * 0.05)
            self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.maxstamina-(self.timer*0.05), round(self.maxstamina * 0.75), round(
                self.maxstamina * 0.5), round(self.maxstamina * 0.25)
        self.statusupdate()

    def update(self, weather, newdt, zoom, combattimer, mousepos, mouseup):
        if self.lastzoom != zoom: # camera zoom is changed
            self.lastzoom = zoom
            self.zoomchange = True
            self.zoom = zoom # save scale
            self.zoomscale() # update parentunit sprite according to new scale

        if self.state != 100:

            # v Mouse collision detection
            if self.rect.collidepoint(mousepos):
                self.maingame.lastmouseover = self.parentunit  # last mouse over on this parentunit
                if mouseup and self.maingame.uiclick is False:
                    self.maingame.lastselected = self.parentunit  # become last selected parentunit
                    if self.parentunit.selected is False:
                        self.parentunit.justselected = True
                        self.parentunit.selected = True
                    self.wholastselect = self.gameid
                    self.maingame.clickany = True
            # ^ End mouse detect

            #v Stamina and Health bar and melee combat indicator function
            if self.oldlasthealth != self.unithealth:
                healthlist = (self.health75, self.health50, self.health25, 0)
                for index, health in enumerate(healthlist):
                    if self.unithealth > health:
                        if self.lasthealthstate != abs(4-index):
                            self.image_original3.blit(self.images[index+1], self.healthimagerect)
                            self.imageblock_original.blit(self.images[index+1], self.healthimagerect)
                            self.lasthealthstate = abs(4-index)
                            self.zoomscale()
                        break
                #^ End hp bar

                #v Stamina bar
                if self.oldlaststamina != self.stamina:
                    staminalist = (self.stamina75, self.stamina50, self.stamina25, 0, -1)
                    for index, stamina in enumerate(staminalist):
                        if self.stamina > stamina:
                            if self.laststaminastate != abs(4 - index):
                                if index != 3:
                                    self.image_original3.blit(self.images[index + 6], self.staminaimagerect)
                                    self.zoomscale()
                                    self.imageblock_original.blit(self.images[index + 6], self.staminaimagerect)
                                    self.laststaminastate = abs(4 - index)
                                else: # the last level is for collaspe state, condition is slightly different
                                    if self.state != 97: # not in collaspe state
                                        self.image_original3.blit(self.images[10], self.staminaimagerect)
                                        self.zoomscale()
                                        self.laststaminastate = 0
                                        self.oldlaststamina = self.stamina
                            break

                    self.oldlaststamina = self.stamina
                #^ End stamina bar
            #^ End hp/stamina

            dt = newdt
            if dt > 0: # only run these when game not pause
                self.timer += dt

                parentstate = self.parentunit.state
                if parentstate in (0, 1, 2, 3, 4, 5, 6, 96, 97, 98, 99) and self.state not in (97, 98, 99):
                    self.state = parentstate # Enforce parentunit state to subunit when moving and breaking
                    if 9 in self.statuseffect: # fight to the death
                        self.state = 10

                self.walk = False  # reset walk
                self.run = False  # reset run
                self.attacktarget = self.parentunit.attacktarget
                self.attackpos = self.parentunit.baseattackpos
                # if self.attacktarget is not None:
                #     self.attackpos = self.attacktarget.leadersubunit.basepos

                if self.timer > 1: # Update status and skill use around every 1 second
                    self.statusupdate(weather)
                    self.availableskill = []

                    if self.useskillcond != 3: # any skill condition behaviour beside 3 (forbid skill) will check available skill to use
                        self.checkskillcondition()

                    if self.state == 4 and self.attacking and self.parentunit.moverotate is False and self.chargeskill not in self.skillcooldown \
                            and self.basepos.distance_to(self.basetarget) < 100: # charge skill only when running to melee
                        self.useskill(0) # Use charge skill
                        self.chargemomentum = self.parentunit.runspeed / 2
                        self.parentunit.charging = True

                    if self.chargemomentum > 1 and self.chargeskill not in self.skilleffect:  # reset charge momentum if charge skill not active
                        self.chargemomentum -= self.timer
                        if self.chargemomentum < 1:
                            self.parentunit.charging = False
                            self.chargemomentum = 1

                    skillchance = random.randint(0, 10) # random chance to use random available skill
                    if len(self.availableskill) > 0 and skillchance >= 6:
                        self.useskill(self.availableskill[random.randint(0, len(self.availableskill) - 1)])
                    self.timer -= 1

                if self.state not in (96,97,98,99):
                    #v Check if in combat or not with collision
                    if self.enemyfront != [] or self.enemyside != []:
                        collidelist = self.enemyfront + self.enemyside
                        for subunit in collidelist:
                            if subunit.team != self.team:
                                self.state = 10
                                self.meleetarget = subunit
                                if parentstate not in (96,97,98,99):
                                    parentstate = 10
                                    self.parentunit.state = 10
                                    self.parentunit.attacktarget = self.meleetarget.parentunit

                                if self.enemyfront == []: # no enemy in front try rotate to enemy at side
                                    self.basetarget = self.meleetarget.basepos
                                    self.newangle = self.setrotate()

                                break
                    elif parentstate == 10:
                        if self.attacking and self.parentunit.collide:
                            if self.chargemomentum == 1 and (self.frontline or self.parentunit.attackmode == 2) and self.parentunit.attackmode != 1: # attack to nearest target instead
                                if self.meleetarget is None and self.parentunit.attacktarget is not None:
                                    self.meleetarget = self.parentunit.attacktarget.subunitsprite[0]
                                if self.closetarget is None: # movement queue is empty regenerate new one
                                    self.findeclosetarget() # find new close target

                                    if self.closetarget is not None: # found target to fight

                                        if self not in self.maingame.combatpathqueue:
                                            self.maingame.combatpathqueue.append(self)

                                        # if self.gameid == 10087:
                                        #     print('run', self.basepos != self.basetarget)

                                    else: # no target to fight move back to command pos first)
                                        self.basetarget = self.attacktarget.basepos
                                        self.newangle = self.setrotate()

                                if self.meleetarget.parentunit.state != 100:
                                    if self.movetimer == 0:
                                        self.movetimer = 0.1 # recalculate again in 10 seconds if not in fight
                                        # if len(self.friendfront) != 0 and len(self.enemyfront) == 0: # collide with friend try move to basetarget first before enemy
                                            # self.combatmovequeue = [] # clean queue since the old one no longer without collide
                                    else:
                                        self.movetimer += dt
                                        if len(self.enemyfront) != 0 or len(self.enemyside) != 0: # in fight, stop timer
                                            self.movetimer = 0

                                        elif self.movetimer > 10 or len(self.combatmovequeue) == 0: # # time up, or no path. reset
                                            self.movetimer = 0
                                            self.closetarget = None
                                            if self in self.maingame.combatpathqueue:
                                                self.maingame.combatpathqueue.remove(self)

                                        elif len(self.combatmovequeue) > 0: # no collide move to enemy
                                            self.basetarget = pygame.Vector2(self.combatmovequeue[0])
                                            self.newangle = self.setrotate()

                                else: # whole targeted enemy unit destroyed, reset target and state
                                    self.meleetarget = None
                                    self.closetarget = None
                                    if self in self.maingame.combatpathqueue:
                                        self.maingame.combatpathqueue.remove(self)

                                    self.attacktarget = None
                                    self.basetarget = self.commandtarget
                                    self.newangle = self.setrotate()
                                    self.newangle = self.parentunit.angle
                                    self.state = 0

                            elif self.chargemomentum > 1: # gradually reduce charge momentum during combat
                                self.chargemomentum -= dt
                                if self.chargemomentum < 1:
                                    self.chargemomentum = 1

                        elif self.attacking is False:  # not in fight anymore, rotate and move back to original position
                            self.meleetarget = None
                            self.closetarget = None
                            if self in self.maingame.combatpathqueue:
                                self.maingame.combatpathqueue.remove(self)

                            self.attacktarget = None
                            self.basetarget = self.commandtarget
                            self.newangle = self.parentunit.angle
                            self.state = 0

                    #^ End melee check

                    #v Unit in melee combat, set subunit state to be in idle, melee combat or range attack state
                    if parentstate == 10:
                        if self.state != 10 and self.ammo > 0 and self.parentunit.fireatwill == 0 and (self.arcshot or self.frontline) and self.chargemomentum == 1:  # Help range attack when parentunit in melee combat if has arcshot or frontline
                            self.state = 11
                            if self.parentunit.neartarget != {} and (self.attacktarget is None or self.attackpos == 0):
                                self.findshootingtarget(parentstate)
                    #^End parentunit in melee combat

                    #v Range attack function
                    elif parentstate == 11: # Unit in range attack state and self is not collapse or broken
                        self.state = 0 # Default state at idle
                        if (self.ammo > 0 or self.magazinenow > 0) and self.attackpos != 0 \
                                and self.shootrange >= self.attackpos.distance_to(self.parentunit.basepos): # can shoot if have ammo and in shoot range
                            self.state = 11 # range combat state

                    elif self.ammo > 0 and self.parentunit.fireatwill == 0 and (self.state == 0 or (parentstate in (1, 2, 3, 4, 5, 6)
                                                                                                    and self.shootmove)):  # Fire at will, auto pick closest enemy
                        if self.parentunit.neartarget != {} and self.attacktarget is None:
                            self.findshootingtarget(parentstate)

                    if self.state in (11, 12, 13) and self.ammo > 0 and self.magazinenow == 0: # reloading ammo
                        self.reloadtime += dt
                        if self.reloadtime >= self.reload:
                            self.magazinenow = self.magazinesize
                            self.ammo -= 1
                            self.reloadtime = 0
                        self.stamina = self.stamina - (dt * 2) # use stamina while reloading
                    #^ End range attack function

                    #v Combat action related
                    if combattimer >= 0.5: # combat is calculated every 0.5 second in game time
                        if self.state == 10: # if melee combat (engaging anyone on any side)
                            collidelist = [subunit for subunit in self.enemyfront if subunit.team != self.team]
                            for subunit in collidelist:
                                anglecheck = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
                                if anglecheck >= 135:  # front
                                    hitside = 0
                                elif anglecheck >= 45:  # side
                                    hitside = 1
                                else: # rear
                                    hitside = 2
                                self.dmgcal(subunit, 0, hitside, self.maingame.gameunitstat.statuslist, combattimer)
                                self.stamina = self.stamina - (combattimer * 2)

                        elif self.state in (11, 12, 13): # range combat
                            if type(self.attacktarget) == int: # For fire at will, which attacktarge is int
                                allunitindex = self.maingame.allunitindex
                                if self.attacktarget in allunitindex: # if the attack basetarget still alive (if dead it would not be in index list)
                                    self.attacktarget = self.maingame.allunitlist[allunitindex.index(self.attacktarget)] # change attacktarget index into sprite
                                else: # enemy dead
                                    self.attackpos = 0 # reset attackpos to 0
                                    self.attacktarget = None # reset attacktarget to 0

                                    for target in list(self.parentunit.neartarget.values()): # find other nearby basetarget to shoot
                                        if target in allunitindex: # check if basetarget alive
                                            self.attackpos = target[1]
                                            self.attacktarget = target[1]
                                            self.attacktarget = self.maingame.allunitlist[allunitindex.index(self.attacktarget)]
                                            break # found new basetarget break loop

                            if self.magazinenow > 0 and self.shootrange > 0 and ((self.attacktarget is not None and self.attacktarget.state != 100) or
                                                (self.attacktarget is None and self.attackpos != 0)) \
                                                and (self.arcshot or (self.arcshot is False and self.parentunit.shoothow != 1)):
                                # can shoot if reload finish and basetarget existed and not dead. Non arcshot cannot shoot if forbidded
                                rangeattack.Rangearrow(self, self.basepos.distance_to(self.attackpos), self.shootrange, self.zoom) # Shoot at enemy
                                self.magazinenow -= 1 # use 1 ammo in magazine
                            elif self.attacktarget is not None and self.attacktarget.state == 100: # if basetarget die when it about to shoot
                                self.parentunit.rangecombatcheck, self.parentunit.attacktarget = False, 0 # reset range combat check and basetarget

                    #^ End combat related

                if parentstate != 10: # reset basetarget every update to command basetarget outside of combat
                    self.basetarget = self.commandtarget
                    # self.newangle = self.setrotate()
                # elif self.state != 10 and self.frontline: # set basetarget to enemy basepos
                #     if self.attacktarget is not None:
                #         pass
                    # self.basetarget = self.attacktarget.basepos
                    # self.newangle = self.setrotate()

                # v Rotate Function
                if self.angle != self.newangle:
                    self.rotatecal = abs(self.newangle - self.angle)  # amount of angle left to rotate
                    self.rotatecheck = 360 - self.rotatecal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
                    self.radians_angle = math.radians(360 - self.angle)  # for allside rotate
                    if self.angle < 0:  # negative angle (rotate to left side)
                        self.radians_angle = math.radians(-self.angle)

                    rotatetiny = self.rotatespeed * dt  # rotate little by little according to time
                    if self.newangle > self.angle:  # rotate to angle more than the current one
                        if self.rotatecal > 180:  # rotate with the smallest angle direction
                            self.angle -= rotatetiny
                            self.rotatecheck -= rotatetiny
                            if self.rotatecheck <= 0: self.angle = self.newangle  # if rotate pass basetarget angle, rotate to basetarget angle
                        else:
                            self.angle += rotatetiny
                            if self.angle > self.newangle: self.angle = self.newangle  # if rotate pass basetarget angle, rotate to basetarget angle
                    elif self.newangle < self.angle:  # rotate to angle less than the current one
                        if self.rotatecal > 180:  # rotate with the smallest angle direction
                            self.angle += rotatetiny
                            self.rotatecheck -= rotatetiny
                            if self.rotatecheck <= 0: self.angle = self.newangle  # if rotate pass basetarget angle, rotate to basetarget angle
                        else:
                            self.angle -= rotatetiny
                            if self.angle < self.newangle: self.angle = self.newangle  # if rotate pass basetarget angle, rotate to basetarget angle
                    self.rotate()  # rotate sprite to new angle
                    self.makefrontsidepos()  # generate new pos related to side
                    self.mask = pygame.mask.from_surface(self.image) # make new mask
                # ^ End rotate

                revertmove = False
                if self.state != 10 and self.parentunit.revert or \
                        (self.angle != self.parentunit.angle and self.parentunit.moverotate is False) or parentstate == 10:
                    revertmove = True # revert move check for in case subunit still need to rotate more before moving

                #v Move function to given basetarget position
                if ((self.angle != self.newangle and revertmove is False) or (self.angle == self.newangle \
                    and (self.basepos != self.basetarget or self.chargemomentum > 1))): # cannot move if still need to rotate
                    if parentstate in (1, 2, 3, 4):
                        self.attacking = True
                    elif self.attacking and parentstate not in (1, 2, 3, 4, 10): # cancel charge when no longer move to melee or in combat
                        self.attacking = False

                    #v Can move if front not collided
                    if self.stamina > 0 and (self.parentunit.collide is False or ((self.frontline or self.parentunit.attackmode == 2) and self.attacking) or self.chargemomentum > 1) \
                            and len(self.enemyfront) == 0 and ((len(self.friendfront) == 0 and parentstate == 10) or parentstate != 10): #  or self.parentunit.retreatstart
                        if self.chargemomentum > 1 and self.basepos == self.basetarget:
                            newtarget = self.frontsidepos - self.basepos
                            self.basetarget = self.basetarget + newtarget
                            self.commandtarget = self.basetarget
                        move = self.basetarget - self.basepos
                        move_length = move.length()  # convert length

                        if move_length > 0:  # movement length longer than 0.1, not reach basetarget yet
                            move.normalize_ip()

                            if self.state in (1, 3, 5, 12):  # walking
                                move = move * self.parentunit.walkspeed * dt # use walk speed
                                self.walk = True
                            else:  # self.state in (2, 4, 6, 10, 96, 98, 99), running
                                move = move * self.parentunit.runspeed * dt # use run speed
                                self.run = True
                            newpos = self.basepos + move

                            if (self.state not in (98, 99) and (newpos[0] > 0 and newpos[0] < 999 and newpos[1] > 0 and newpos[1] < 999)) \
                                    or self.state in (98, 99):  # cannot go pass map unless in retreat
                                if move.length() <= move_length:  # move normally according to move speed
                                    self.basepos = newpos
                                    self.pos = self.basepos * self.zoom
                                    self.rect.center = list(int(v) for v in self.pos)  # list rect so the sprite gradually move to position

                                else:  # move length pass the basetarget destination, set movement to stop exactly at basetarget
                                    move = self.basetarget - self.basepos  # simply change move to whatever remaining distance
                                    self.basepos += move  # adjust base position according to movement
                                    self.pos = self.basepos * self.zoom
                                    self.rect.center = self.pos  # no need to do list
                                if len(self.combatmovequeue) > 0 and self.basepos.distance_to(pygame.Vector2(self.combatmovequeue[0])) < 0.1: #:  # reach the current queue point, remove from queue
                                    self.combatmovequeue = self.combatmovequeue[1:]

                                self.makefrontsidepos()
                                self.makeposrange()

                                if self.unitleader: #parentstate != 10 and self.parentunit.moving is False and self.parentunit.moverotate is False:
                                    if self.parentunit.moverotate is False:
                                        self.parentunit.basepos += move
                                    frontpos = (self.parentunit.basepos[0], (self.parentunit.basepos[1] - self.parentunit.baseheightbox))  # find front position
                                    self.parentunit.frontpos = self.rotationxy(self.parentunit.basepos, frontpos, self.parentunit.radians_angle)

                                    numberpos = (self.parentunit.basepos[0] - self.parentunit.basewidthbox, (self.parentunit.basepos[1] + self.parentunit.baseheightbox))
                                    self.parentunit.numberpos = self.rotationxy(self.parentunit.basepos, numberpos, self.parentunit.radians_angle)
                                    self.parentunit.truenumberpos = self.parentunit.numberpos * (11 - self.parentunit.zoom) # find new position for troop number text

                        else:  # Stopping subunit when reach basetarget
                            self.state = 0  # idle

                        # if self.lastpos != self.basepos:
                        self.terrain, self.feature = self.getfeature(self.basepos, self.gamemap)  # get new terrain and feature at each subunit position
                        self.height = self.gamemapheight.getheight(self.basepos)  # get new height
                        self.frontheight = self.gamemapheight.getheight(self.frontsidepos)
                        self.mask = pygame.mask.from_surface(self.image) # make new mask
                        self.lastpos = self.basepos
                    # ^ End move function

                self.stamina = self.stamina - (dt * 0.5) if self.walk else self.stamina - (dt * 2) if self.run else self.stamina + (
                        dt * self.staminaregen) if self.stamina < self.maxstamina else self.stamina  # consume stamina depending on activity/state

                #v Morale check
                if self.basemorale < self.maxmorale: #TODO change to chance between broken or shattered where broken can regain control, also commander dead chance to completely lose control
                    if self.morale < 1: # Enter broken state when morale reach 0
                        if self.state != 99: # This is top state above other states except dead for subunit
                            self.state = 99 # broken state
                            self.moraleregen -= 0.3 # morale regen gradually slower per broken state
                            for subunit in self.parentunit.subunitsprite:
                                subunit.basemorale -= (15 * subunit.mental) # reduce morale of other subunit, creating panic when seeing friend panic and may cause mass panic
                        self.morale = 0 # morale cannot be lower than 0

                    if self.basemorale < 0: # morale cannot be negative
                        self.basemorale = 0
                    elif self.basemorale > 200: # morale cannot be higher than 200
                        self.basemorale = 200

                    if self.parentunit.leader[0].state not in (96, 97, 98, 99, 100): # If not missing main leader can replenish morale
                        self.basemorale += (dt * self.staminastatecal * self.moraleregen) # Morale replenish based on stamina

                    if self.state == 99:
                        if parentstate not in (98, 99):
                            self.unithealth -= (dt * 100) # Unit begin to desert if broken but parentunit keep fighting
                        if self.moralestate > 0.2:
                            self.state = 0  # Reset state to 0 when exit broken state

                elif self.basemorale > self.maxmorale:
                    self.basemorale -= dt # gradually reduce morale that exceed the starting max amount
                #^ End morale check

                if self.oldlasthealth != self.unithealth:
                    self.troopnumber = self.unithealth / self.troophealth  # Calculate how many troop left based on current hp
                    if self.troopnumber.is_integer() is False:  # always round up if there is decimal
                        self.troopnumber = int(self.troopnumber + 1)
                    self.oldlasthealth = self.unithealth

                #v Hp and stamina regen
                if self.stamina < self.maxstamina:
                    if self.stamina <= 0:  # Collapse and cannot act
                        self.stamina = 0
                        if self.state != 99: # Can only collapse when subunit is not broken
                            self.state = 97 # Collapse
                    if self.state == 97 and self.stamina > self.stamina25: # exit collapse state
                        self.state = 0 # Reset to idle
                elif self.stamina > self.maxstamina: # stamina cannot exceed the max stamina
                    self.stamina = self.maxstamina

                if self.hpregen > 0 and self.unithealth % self.troophealth != 0:  ## hp regen cannot ressurect troop only heal to max hp
                    alivehp = self.troopnumber * self.troophealth  ## Max hp possible for the number of alive subunit
                    self.unithealth += self.hpregen * dt # regen hp back based on time and regen stat
                    if self.unithealth > alivehp: self.unithealth = alivehp # Cannot exceed health of alive subunit (exceed mean resurrection)
                elif self.hpregen < 0:  ## negative regen can kill
                    self.unithealth += self.hpregen * dt # use the same as positive regen (negative regen number * dt will reduce hp)
                    self.troopnumber = self.unithealth / self.troophealth  # Recal number of troop again in case some die from negative regen
                    if round(self.troopnumber) < self.troopnumber: # no method to always round up number so I need to do this manually
                        self.troopnumber = int(self.troopnumber + 1)
                    else:
                        self.troopnumber = int(self.troopnumber)

                if self.unithealth < 0: self.unithealth = 0 # can't have negative hp
                elif self.unithealth > self.maxhealth: self.unithealth = self.maxhealth # hp can't exceed max hp (would increase number of troop)
                if self.state == 97 and self.stamina >= (self.maxstamina/4): self.state = 0 # awake from collaspe when stamina reach 25%
                #^ End regen

            if self.troopnumber <= 0:  # enter dead state
                self.state = 100 # enter dead state
                self.image_original3.blit(self.images[5], self.healthimagerect) # blit white hp bar
                self.imageblock_original.blit(self.images[5], self.healthimagerect)
                self.zoomscale()
                self.lasthealthstate = 0
                self.skillcooldown = {} # remove all cooldown
                self.skilleffect = {} # remove all skill effects

                self.imageblock.blit(self.imageblock_original, self.cornerimagerect)
                self.haveredcorner = True # to prevent red border appear when dead

                self.parentunit.deadchange = True

                self.maingame.battlecamera.change_layer(sprite=self, new_layer=1)
                self.maingame.allsubunitlist.remove(self)
                self.parentunit.subunitsprite.remove(self)

                for subunit in self.parentunit.armysubunit.flat: # remove from index array
                    if subunit == self.gameid:
                        self.parentunit.armysubunit = np.where(self.parentunit.armysubunit == self.gameid, 0, self.parentunit.armysubunit)
                        break

                #v Leader change subunit or gone/die
                if self.leader is not None and self.leader.state != 100: # Find new subunit for leader if there is one in this subunit
                    for subunit in self.nearbysquadlist:
                        if subunit != 0 and subunit.state != 100 and subunit.leader == None:
                            subunit.leader = self.leader
                            self.leader.subunit = subunit
                            for index, subunit in enumerate(self.parentunit.subunitsprite):  # loop to find new subunit pos based on new subunitsprite list
                                if subunit.gameid == self.leader.subunit.gameid:
                                    subunit.leader.subunitpos = index
                                    if self.unitleader:  # set leader subunit to new one
                                        self.parentunit.leadersubunit = subunit
                                        subunit.unitleader = True

                            self.leader = None
                            break

                    if self.leader is not None:  # if can't find near subunit to move leader then find from first subunit to last place in parentunit
                        for index, subunit in enumerate(self.parentunit.subunitsprite):
                            if subunit.state != 100 and subunit.leader == None:
                                subunit.leader = self.leader
                                self.leader.subunit = subunit
                                subunit.leader.subunitpos = index
                                self.leader = None
                                if self.unitleader:  # set leader subunit to new one
                                    self.parentunit.leadersubunit = subunit
                                    subunit.unitleader = True

                                break

                        if self.leader is not None: # Still can't find new subunit so leader disappear with chance of different result
                            self.leader.state = random.randint(97,100) # captured, retreated, wounded, dead
                            self.leader.health = 0
                            self.leader.gone()


                    self.unitleader = False
                #^ End leader change

                self.maingame.eventlog.addlog([0, str(self.boardpos) + " " + str(self.name)
                                               + " in " + self.parentunit.leader[0].name
                                               + "'s parentunit is destroyed"], [3]) # add log to say this subunit is destroyed in subunit tab

            self.enemyfront = [] # reset collide
            self.enemyside = [] # reset collide
            self.friendfront = []

    def rotate(self):
        """rotate subunit image may use when subunit can change direction independently from parentunit"""
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        if self.parentunit.selected and self.state != 100:
            self.selectedimage = pygame.transform.rotate(self.selectedimage_original, self.angle)
            self.image.blit(self.selectedimage, self.selectedimagerect)
        self.rect = self.image.get_rect(center=self.pos)

    # def command(self, mouse_pos, mouse_up, mouse_right, squadlastselect):
    #     """For inspect ui clicking"""
    #     self.wholastselect = squadlastselect
    #     if self.rect.collidepoint(mouse_pos[0]):
    #         self.mouse_over = True
    #         self.whomouseover = self.gameid
    #         if mouse_up:
    #             self.parentunit.selected = True
    #             self.parentunit.justselected = True
    #             self.wholastselect = self.gameid

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.parentunit
            del self.leader
            del self.wholastselect
            del self.attacktarget
            del self.meleetarget
            del self.closetarget
            if self in self.maingame.combatpathqueue:
                self.maingame.combatpathqueue.remove(self)


