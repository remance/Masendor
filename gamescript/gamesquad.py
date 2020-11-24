import random
import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale
from gamescript import rangeattack, gamelongscript

class Unitsquad(pygame.sprite.Sprite):
    images = []
    maingame = None
    dmgcal = gamelongscript.dmgcal
    battlesidecal = (1, 0.5, 0.1, 0.5)  # battlesidecal is for melee combat side modifier,
    # use same position as squad front index 0 = front, 1 = left, 2 = rear, 3 = right

    def __init__(self, unitid, gameid, weaponlist, armourlist, statlist, battalion, position, inspectuipos, starthp, startstamina):
        """Although squad in code, this is referred as sub-unit ingame"""
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.wholastselect = 0
        self.mouse_over = False
        self.gameid = gameid # ID of this squad
        self.unitid = int(unitid) # ID of preset used for this squad
        self.angle, self.newangle = 0, 0
        self.battleside = [None, None, None, None] # index of battleside: 0 = front 1 = left 2 =rear 3 =right (different than battalion for combat rotation)
        self.battlesideid = [0, 0, 0, 0] # battlesideid keep index of enemy battalion 0 is no current enemy (idle in combat)
        self.haveredcorner = False
        self.state = 0 # Current squad state, similar to battalion state
        self.gamestart = False # Game start yet? for stuff only need to be done at the start
        self.nocombat = 0 # time when not fighting before going into idle (1 second)
        self.timer = 0 # may need to use random.random()
        self.battalion = battalion # reference to the parent battlion of this squad
        stat = statlist.unitlist[self.unitid].copy()
        self.leader = None # Leader in the sub-unit if there is one
        self.boardpos = None  # Used for event log position of squad (Assigned in maingame unit setup)
        self.terrain = None # Current terrain climate
        self.feature = None # Current terrain feature
        self.height = None # Current terrain height
        self.gamemapfeature = self.battalion.gamemapfeature
        self.name = stat[0] # name according to the preset
        self.unitclass = stat[1] # used to determine whether to use melee or range weapon as icon
        self.grade = stat[2]
        self.race = stat[3]
        self.trait = stat[4]
        self.trait = self.trait + statlist.gradelist[self.grade][11]
        skill = stat[5] # skill list according to the preset
        self.skillcooldown = {}
        self.cost = stat[6]
        self.baseattack = round(stat[8] + int(statlist.gradelist[self.grade][1]), 0)
        self.basemeleedef = round(stat[9] + int(statlist.gradelist[self.grade][2]), 0)
        self.baserangedef = round(stat[10] + int(statlist.gradelist[self.grade][2]), 0)
        self.armourgear = stat[11]
        self.basearmour = armourlist.armourlist[self.armourgear[0]][1] \
                          * armourlist.quality[self.armourgear[1]]  # Armour stat is cal from based armour * quality
        self.baseaccuracy = stat[12] + int(statlist.gradelist[self.grade][4])
        self.baserange = stat[13]
        self.ammo = stat[14]
        self.basereload = stat[15] - int(statlist.gradelist[self.grade][5])
        self.reloadtime = 0 # Unit can only shoot when reloadtime is equal or more than reload stat
        self.basecharge = stat[16]
        self.basechargedef = 10 # All infantry unit has default 10 charge defence
        self.chargeskill = stat[17] # For easier reference to check what charge skill this unit has
        self.charging = False # For checking if battalion in charging state or not for using charge skill
        skill = [self.chargeskill] + skill # Add charge skill as first item in the list
        self.skill = {x: statlist.abilitylist[x].copy() for x in skill if x != 0 and x in statlist.abilitylist} # grab skill stat into dict
        self.troophealth = round(stat[18] * (int(statlist.gradelist[self.grade][7]) / 100)) # Health of each troop
        self.stamina = int(stat[19] * (int(statlist.gradelist[self.grade][8]) / 100) * (startstamina / 100))
        self.mana = stat[20] # Resource for magic skill
        self.meleeweapon = stat[21]
        self.rangeweapon = stat[22]
        self.dmg = weaponlist.weaponlist[self.meleeweapon[0]][1] * weaponlist.quality[self.meleeweapon[1]]
        self.penetrate = 1 - (weaponlist.weaponlist[self.meleeweapon[0]][2] * weaponlist.quality[self.meleeweapon[1]] / 100)  # the lower the number the less effectiveness of enemy armour
        if self.penetrate > 1: self.penetrate = 1
        elif self.penetrate < 0: self.penetrate = 0
        self.rangedmg = weaponlist.weaponlist[self.rangeweapon[0]][1] * weaponlist.quality[self.rangeweapon[1]]
        self.rangepenetrate = 1- (weaponlist.weaponlist[self.rangeweapon[0]][2] * weaponlist.quality[self.rangeweapon[1]]/100)
        self.trait = self.trait + weaponlist.weaponlist[self.meleeweapon[0]][4]  # apply trait from range weapon
        self.trait = self.trait + weaponlist.weaponlist[self.rangeweapon[0]][4]  # apply trait from melee weapon
        if self.rangepenetrate > 1: self.rangepenetrate = 1
        elif self.rangepenetrate < 0: self.rangepenetrate = 0
        self.basemorale = int(stat[23] + int(statlist.gradelist[self.grade][9]))
        self.basediscipline = int(stat[24] + int(statlist.gradelist[self.grade][10]))
        self.troopnumber = int(stat[27] * starthp / 100)
        self.basespeed = 50 # All infantry has base speed at 50
        self.unittype = stat[28] - 1 # 0 is melee infantry and 1 is range for command buff
        self.featuremod = 1  # the starting column in unit_terrainbonus of infantry
        self.mount = statlist.mountlist[stat[29]]
        if stat[29] != 1: # have mount
            self.basechargedef = 5 # charge defence only 5 for cav
            self.basespeed = self.mount[1] # use mount base speed instead
            self.troophealth += self.mount[2] # Add mount health to the troop health
            self.basecharge += self.mount[3] # Add charge power of mount to troop
            self.trait = self.trait + self.mount[5]  # Apply mount trait to unit
            self.unittype = 2 # If unit has mount, count as cav for command buff
            self.featuremod = 4  # the starting column in unit_terrainbonus of cavalry
        self.weight = weaponlist.weaponlist[stat[21][0]][3] + weaponlist.weaponlist[stat[22][0]][3] + \
                      armourlist.armourlist[stat[11][0]][2] # Weight from both melee and range weapon and armour
        self.trait = self.trait + armourlist.armourlist[stat[11][0]][4]  # Apply armour trait to unit
        self.basespeed = round((self.basespeed * ((100 - self.weight) / 100)) + int(statlist.gradelist[self.grade][3]), 0) # finalise base speed with weight and grade bonus
        self.description = stat[-1] # squad description for inspect ui
        # if self.hidden
        self.baseelemmelee = 0
        self.baseelemrange = 0
        self.elemcount = [0, 0, 0, 0, 0]  # Elemental threshold count in this order fire,water,air,earth,poison
        self.tempcount = 0 # Temperature threshold count
        fireres = 0
        waterres = 0
        airres = 0
        earthres = 0
        self.magicres = 0 # Resistance to any magic
        self.heatres = 0 # Resistance to heat temperature
        self.coldres = 0 # Resistance to cold temperature
        poisonres = 0
        self.criteffect = 1
        self.frontdmgeffect = 1 # Some skill affect only frontal combat damage
        self.sidedmgeffect = 1 # Some skill affect damage for side combat as well (AOE)
        self.corneratk = False # Check if squad can attack corner enemy or not
        self.flankbonus = 1 # Combat bonus when flanking
        self.baseauthpenalty = 0.1 # penalty to authority when bad event happen
        self.bonusmoraledmg = 0
        self.bonusstaminadmg = 0
        self.authpenalty = 0.1
        self.basehpregen = 0
        self.basestaminaregen = 1
        self.statuslist = self.battalion.statuslist
        self.statuseffect = {}
        self.skilleffect = {}
        self.baseinflictstatus = {}
        self.specialstatus = []
        #v Set up trait variable
        self.arcshot = False
        self.antiinf = False
        self.anticav = False
        self.shootmove = False
        self.agileaim = False
        self.norangepenal = False
        self.longrangeacc = False
        self.ignorechargedef = False
        self.ignoredef = False
        self.fulldef = False
        self.tempfulldef = False
        self.backstab = False
        self.oblivious = False
        self.flanker = False
        self.unbreakable = False
        self.tempunbraekable = False
        self.stationplace = False
        #^ End setup trait variable
        #v Add trait to base stat
        self.trait = list(set([trait for trait in self.trait if trait != 0]))
        if len(self.trait) > 0:
            self.trait = {x: statlist.traitlist[x] for x in self.trait if
                          x in statlist.traitlist}  # Any trait not available in ruleset will be ignored
            for trait in self.trait.values():
                self.baseattack *= trait[3]
                self.basemeleedef *= trait[4]
                self.baserangedef *= trait[5]
                self.basearmour += trait[6]
                self.basespeed *= trait[7]
                self.baseaccuracy *= trait[8]
                self.baserange *= trait[9]
                self.basereload *= trait[10]
                self.basecharge *= trait[11]
                self.basechargedef += trait[12]
                self.basehpregen += trait[13]
                self.basestaminaregen += trait[14]
                self.basemorale += trait[15]
                self.basediscipline += trait[16]
                self.criteffect += trait[17]
                fireres += (trait[21] / 100)
                waterres += (trait[22] / 100)
                airres += (trait[23] / 100)
                earthres += (trait[24] / 100)
                self.magicres += (trait[25] / 100)
                self.heatres += (trait[26] / 100)
                self.coldres += (trait[27] / 100)
                poisonres += (trait[28] / 100)
                if trait[32] != [0]:
                    for effect in trait[32]:
                        self.baseinflictstatus[effect] = trait[1]
                # self.baseelemmelee =
                # self.baseelemrange =
            if 3 in self.trait:  # Varied training
                self.baseattack *= (random.randint(80, 120) / 100)
                self.basemeleedef *= (random.randint(80, 120) / 100)
                self.baserangedef *= (random.randint(80, 120) / 100)
                # self.basearmour *= (random.randint(80, 120) / 100)
                self.basespeed *= (random.randint(80, 120) / 100)
                self.baseaccuracy *= (random.randint(80, 120) / 100)
                # self.baserange *= (random.randint(80, 120) / 100)
                self.basereload *= (random.randint(80, 120) / 100)
                self.basecharge *= (random.randint(80, 120) / 100)
                self.basechargedef *= (random.randint(80, 120) / 100)
                self.basemorale += random.randint(-10, 10)
                self.basediscipline += random.randint(-10, 10)
            if 149 in self.trait:  # Impetuous
                self.baseauthpenalty += 0.5
            #v Change trait variable
            if 16 in self.trait: self.arcshot = True
            if 17 in self.trait: self.agileaim = True
            if 18 in self.trait: self.shootmove = True
            if 29 in self.trait: self.ignorechargedef = True
            if 30 in self.trait: self.ignoredef = True
            if 34 in self.trait: self.fulldef = True
            if 33 in self.trait: self.backstab = True
            if 47 in self.trait: self.flanker = True
            if 55 in self.trait: self.oblivious = True
            if 73 in self.trait: self.norangepenal = True
            if 74 in self.trait: self.longrangeacc = True
            if 111 in self.trait:
                self.unbreakable = True
                self.tempunbraekable = True
            #^ End change trait variable
        #^ End add trait to stat
        # self.loyalty
        self.elemresist = (fireres, waterres, airres, earthres, poisonres) # list of elemental resistance
        self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 0.75), round(
            self.stamina * 0.5), round(self.stamina * 0.25)
        self.unithealth = self.troophealth * self.troopnumber # Total health of unit from all troop
        self.lasthealthstate, self.laststaminastate = 4, 4
        #v Stat for after receive effect from various source
        self.maxmorale = self.basemorale
        self.attack = self.baseattack
        self.meleedef = self.basemeleedef
        self.rangedef = self.baserangedef
        self.armour = self.basearmour
        self.speed = self.basespeed
        self.accuracy = self.baseaccuracy
        self.reload = self.basereload
        self.morale = self.basemorale
        self.discipline = self.basediscipline
        self.shootrange = self.baserange
        self.charge = self.basecharge
        self.chargedef = self.basechargedef
        #^ End stat for status effect
        self.elemmelee = self.baseelemmelee
        self.elemrange = self.baseelemrange
        self.maxhealth, self.health75, self.health50, self.health25, = self.unithealth, round(self.unithealth * 0.75), round(
            self.unithealth * 0.5), round(self.unithealth * 0.25)
        self.oldlasthealth, self.oldlaststamina = self.unithealth, self.stamina
        self.maxtroop = self.troopnumber
        self.moralestate = round((self.basemorale * 100) / self.maxmorale)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.staminastatecal = self.staminastate / 100
        self.moralestatecal = self.moralestate / 100
        self.image = self.images[0]  # Squad block blue colour for player
        """squad block colour"""
        if self.battalion.gameid >= 2000:
            self.image = self.images[19]
        """armour circle colour"""
        image1 = self.images[1]
        if self.basearmour <= 50: image1 = self.images[2]
        image1rect = image1.get_rect(center=self.image.get_rect().center)
        self.image.blit(image1, image1rect)
        """health circle"""
        self.healthimage = self.images[3]
        self.healthimagerect = self.healthimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.healthimage, self.healthimagerect)
        """stamina circle"""
        self.staminaimage = self.images[8]
        self.staminaimagerect = self.staminaimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.staminaimage, self.staminaimagerect)
        """weapon class in circle"""
        if self.unitclass == 0:
            image1 = weaponlist.imgs[weaponlist.weaponlist[self.meleeweapon[0]][5]]
        else:
            image1 = weaponlist.imgs[weaponlist.weaponlist[self.rangeweapon[0]][5]]
        image1rect = image1.get_rect(center=self.image.get_rect().center)
        self.image.blit(image1, image1rect)
        self.image_original = self.image.copy()
        """position in inspect ui"""
        self.armypos = position
        self.inspposition = (self.armypos[0] + inspectuipos[0], self.armypos[1] + inspectuipos[1])
        self.rect = self.image.get_rect(topleft=self.inspposition)
        """self.pos is pos for army inspect ui"""
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        """self.combatpos is pos of battalion"""
        self.combatpos = 0
        battaliontopleft = pygame.Vector2(self.battalion.basepos[0] - self.battalion.basewidthbox / 2,
                           self.battalion.basepos[1] - self.battalion.baseheightbox / 2)
        self.truepos = pygame.Vector2(battaliontopleft[0] + (self.armypos[0]/10), battaliontopleft[1] + (self.armypos[1]/10))
        self.attackpos = self.battalion.baseattackpos

    def useskill(self, whichskill):
        if whichskill == 0:  # charge skill need to seperate since charge power will be used only for charge skill
            skillstat = self.skill[list(self.skill)[0]].copy()
            self.skilleffect[self.chargeskill] = skillstat
            self.skillcooldown[self.chargeskill] = skillstat[4]
        else:  # other skill
            skillstat = self.skill[whichskill].copy()
            self.skilleffect[whichskill] = skillstat
            self.skillcooldown[whichskill] = skillstat[4]
        self.stamina -= skillstat[9]
        # self.skillcooldown[whichskill] =

    # def receiveskill(self,whichskill):

    def checkskillcondition(self):
        """Check which skill can be used"""
        self.availableskill = [skill for skill in self.skill if
                               skill not in self.skillcooldown.keys() and self.state in self.skill[skill][
                                   6] and self.discipline >= self.skill[skill][8] and self.stamina > self.skill[skill][
                                   9] and skill != self.chargeskill]
        if self.useskillcond == 1 and self.staminastate < 50:
            self.availableskill = []
        elif self.useskillcond == 2 and self.staminastate < 25:
            self.availableskill = []

    def findnearbysquad(self):
        """Find nearby friendly squads in the same battalion for applying buff"""
        self.nearbysquadlist = []
        cornersquad = []
        for rowindex, rowlist in enumerate(self.battalion.armysquad.tolist()):
            if self.gameid in rowlist:
                if rowlist.index(self.gameid) - 1 != -1:  #get squad from left if not at first column
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex][rowlist.index(self.gameid) - 1]) # 0
                else:
                    self.nearbysquadlist.append(0)
                if rowlist.index(self.gameid) + 1 != len(rowlist):  #get squad from right if not at last column
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex][rowlist.index(self.gameid) + 1]) # 1
                else:
                    self.nearbysquadlist.append(0)
                if rowindex != 0:  #get top squad
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex - 1][rowlist.index(self.gameid)]) # 2
                    if rowlist.index(self.gameid) - 1 != -1:  # get top left squad
                        cornersquad.append(self.battalion.spritearray[rowindex - 1][rowlist.index(self.gameid) - 1]) # 3
                    else:
                        cornersquad.append(0)
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get top right
                        cornersquad.append(self.battalion.spritearray[rowindex - 1][rowlist.index(self.gameid) + 1]) # 4
                    else:
                        cornersquad.append(0)
                else:
                    self.nearbysquadlist.append(0)
                if rowindex != len(self.battalion.spritearray) - 1:  # get bottom squad
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid)]) # 5
                    if rowlist.index(self.gameid) - 1 != -1:  # get bottom left squad
                        cornersquad.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid) - 1]) # 6
                    else:
                        cornersquad.append(0)
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  # get bottom  right squad
                        cornersquad.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid) + 1]) # 7
                    else:
                        cornersquad.append(0)
                else:
                    self.nearbysquadlist.append(0)
        self.nearbysquadlist = self.nearbysquadlist + cornersquad

    def statustonearby(self, aoe, id, statuslist):
        """apply status effect to nearby unit depending on aoe stat"""
        if aoe in (2, 3):
            if aoe > 1:
                for squad in self.nearbysquadlist[0:4]:
                    if squad != 0: squad.statuseffect[id] = statuslist
            if aoe > 2:
                for squad in self.nearbysquadlist[4:]:
                    if squad != 0: squad.statuseffect[id] = statuslist
        elif aoe == 4:
            for squad in self.battalion.spritearray.flat:
                if squad.state != 100:
                    squad.statuseffect[id] = statuslist

    def thresholdcount(self, elem, t1status, t2status):
        if elem > 50:
            self.statuseffect[t1status] = self.statuslist[t1status].copy()
            if elem > 100:
                self.statuseffect[t2status] = self.statuslist[t2status].copy()
                del self.statuseffect[t1status]
                elem = 0
        return elem

    def statusupdate(self, thisweather):
        """calculate stat from stamina, morale state, skill, status, terrain"""
        if self.maxstamina > 100:
            self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.maxstamina-(self.timer*0.05), round(self.maxstamina * 0.75), round(
                self.maxstamina * 0.5), round(self.maxstamina * 0.25)
        self.morale = self.basemorale
        self.authority = self.battalion.authority
        self.commandbuff = self.battalion.commandbuff[self.unittype] * 100
        self.moralestate = round(((self.basemorale * 100) / self.maxmorale) * (self.authority / 100), 0)
        self.moralestatecal = self.moralestate / 100
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.staminastatecal = self.staminastate / 100
        self.discipline = (self.basediscipline * self.moralestatecal * self.staminastatecal) + self.battalion.leadersocial[
            self.grade + 1] + (self.authority / 10)
        self.attack = (self.baseattack * (self.moralestatecal + 0.1)) * self.staminastatecal + self.commandbuff
        self.meleedef = (self.basemeleedef * (self.moralestatecal + 0.1)) * self.staminastatecal + self.commandbuff
        self.rangedef = (self.baserangedef * (self.moralestatecal + 0.1)) * self.staminastatecal + self.commandbuff
        self.accuracy = self.baseaccuracy * self.staminastatecal + self.commandbuff
        self.reload = self.basereload * ((200 - self.staminastate) / 100)
        self.chargedef = (self.basechargedef * (self.moralestatecal + 0.1)) * self.staminastatecal + self.commandbuff
        self.speed = self.basespeed * self.staminastate / 100
        self.charge = (self.basecharge * (self.moralestatecal + 0.1)) * self.staminastatecal + self.commandbuff
        self.shootrange = self.baserange
        self.criteffect = 1
        self.frontdmgeffect = 1
        self.sidedmgeffect = 1
        self.authpenalty = self.baseauthpenalty
        self.corneratk = False
        self.tempunbraekable = False
        self.tempfulldef = False
        self.hpregen = self.basehpregen
        self.staminaregen = self.basestaminaregen
        self.inflictstatus = self.baseinflictstatus
        self.elemmelee = self.baseelemmelee
        self.elemrange = self.baseelemrange
        """apply height to range"""
        if self.height > 100:
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
        self.morale += weather.morale_buff
        self.discipline += weather.discipline_buff
        if weather.elem[0] != 0: # Weather can cause elemental effect such as wet
            self.elemcount[weather.elem[0]] += ((weather.elem[1] * (100 - self.elemresist[weather.elem[0]]) / 100))
        #^ End weather
        #v Map feature modifier to stat
        mapfeaturemod = self.gamemapfeature.featuremod[self.feature]
        if mapfeaturemod[self.featuremod] != 1: # speed/charge
            speedmod = mapfeaturemod[self.featuremod] # get the speed mod appropiate to unit type
            self.speed *= speedmod
            self.charge *= speedmod
        if mapfeaturemod[self.featuremod + 1] != 1: # melee attack
            # combatmod = self.battalion.gamemapfeature.featuremod[self.battalion.feature][self.featuremod + 1]
            self.attack *= mapfeaturemod[self.featuremod + 1] # get the attack mod appropiate to unit type
        if mapfeaturemod[self.featuremod + 2] != 1: # melee/charge defense
            combatmod = mapfeaturemod[self.featuremod + 2] # get the defence mod appropiate to unit type
            self.meleedef *= combatmod
            self.chargedef *= combatmod
        if mapfeaturemod[10] != [0]: # Some terrain feature can also cause status effect such as swimming in water
            if 1 in mapfeaturemod[10]: # Water type terrain
                self.statuseffect[93] = self.statuslist[93].copy() # drench
                if self.weight > 60 or self.stamina <= 0: # weight too much or tired will cause drowning
                    self.statuseffect[102] = self.statuslist[102].copy() # Drowning
                elif self.weight > 30:  # Medium weight squad has trouble travel through water and will sink and progressively lose troops
                    self.statuseffect[101] = self.statuslist[101].copy() # Sinking
                elif self.weight < 30:  # Light weight squad has no trouble travel through water
                    self.statuseffect[104] = self.statuslist[104].copy() # Swiming
            if 2 in mapfeaturemod[10]:  # Rot type terrain
                self.statuseffect[54] = self.statuslist[54].copy()
            if 3 in mapfeaturemod[10]:  # Poison type terrain
                self.elemcount[4] += ((100 - self.elemresist[5]) / 100)
        self.rangedef += mapfeaturemod[7] # range defense from terrain bonus
        # self.hidden += self.battalion.gamemapfeature[self.battalion.feature][6]
        #^ End map feature
        #v Temperature mod function from terrain and weather
        tempreach = mapfeaturemod[9] + weather.temperature # temperature the squad will change to based on current terrain feature and weather
        if tempreach < 0: # cold temperature
            tempreach = tempreach * (100 - self.coldres) / 100 # lowest temperature the squad will change based on cold resist
        else: # hot temperature
            tempreach = tempreach * (100 - self.heatres) / 100 # highest temperature the squad will change based on heat resist
        if self.tempcount != tempreach:
            if tempreach > 0:
                if self.tempcount < tempreach:
                    self.tempcount += (100 - self.heatres) / 100 * self.timer # increase squad temperature, rate depends on heat resistance (negative make rate faster)
            elif tempreach < 0:
                if self.tempcount > tempreach:
                    self.tempcount -= (100 - self.coldres) / 100 * self.timer # reduce squad temperature, rate depends on cold resistance
            else: # tempreach is 0, squad temp revert back to 0
                if self.tempcount > 0:
                    self.tempcount -= (100 - self.heatres) / 100 * self.timer # revert faster with higher resist
                else:
                    self.tempcount += (100 - self.coldres) / 100 * self.timer # revert faster with higher resist
        #^ End temperature
        #v Apply effect from skill
        if len(self.skilleffect) > 0:
            for status in self.skilleffect:  # apply elemental effect to dmg if skill has element
                calstatus = self.skilleffect[status]
                if calstatus[1] == 0 and calstatus[31] != 0:
                    self.elemmelee = int(calstatus[31])
                elif calstatus[1] == 1 and calstatus[31] != 0:
                    self.elemrange = int(calstatus[31])
                self.attack = self.attack * calstatus[10]
                self.meleedef = self.meleedef * calstatus[11]
                self.rangedef = self.rangedef * calstatus[12]
                self.speed = self.speed * calstatus[13]
                self.accuracy = self.accuracy * calstatus[14]
                self.shootrange = self.shootrange * calstatus[15]
                self.reload = self.reload / calstatus[16]
                self.charge = self.charge * calstatus[17]
                self.chargedef = self.chargedef + calstatus[18]
                self.hpregen += calstatus[19]
                self.staminaregen += calstatus[20]
                self.morale = self.morale + calstatus[21]
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
                        #     self.battalion.armysquad
                        # if status[2] > 2:
                #^ End apply status to
                self.bonusmoraledmg += calstatus[28]
                self.bonusstaminadmg += calstatus[29]
                if calstatus[30] != [0]: # Apply inflict status effect to enemy from skill to inflict list
                    for effect in calstatus[30]:
                        if effect != [0]: self.inflictstatus[effect] = calstatus[2]
            self.charging = False
            if self.chargeskill in self.skilleffect:
                self.charging = True
                self.authpenalty += 0.5 # higher authority penalty when charging (retreat while charging)
        #^ End skill effect
        if self.elemcount != [0, 0, 0, 0, 0]: # Apply effect if elem threshold reach 50 or 100
            self.elemcount[0] = self.thresholdcount(self.elemcount[0], 28, 92)
            self.elemcount[1] = self.thresholdcount(self.elemcount[1], 31, 93)
            self.elemcount[2] = self.thresholdcount(self.elemcount[2], 30, 94)
            self.elemcount[3] = self.thresholdcount(self.elemcount[3], 23, 35)
            self.elemcount[4] = self.thresholdcount(self.elemcount[4], 26, 27)
            self.elemcount = [elem - self.timer if elem > 0 else elem for elem in self.elemcount]
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
        # 7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal"""
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
                self.morale = self.morale + calstatus[15]
                self.discipline += calstatus[16]
                # self.sight += status[18]
                # self.hidden += status[19]
                if status == 1: # Fearless status
                    self.tempunbraekable = True
                elif status == 91: # All round defense status
                    self.tempfulldef = True
        #^ End status effect
        #v Rounding up, add discipline to stat and forbid negative int
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
        #v cooldown, active and effect timer function
        self.skillcooldown = {key: val - self.timer for key, val in self.skillcooldown.items()} # cooldown decrease overtime
        self.skillcooldown = {key: val for key, val in self.skillcooldown.items() if val > 0} # remove cooldown if time reach 0
        for a, b in self.skilleffect.items(): # Can't use dict comprehension here since value include all other skill stat
            b[3] -= self.timer
        self.skilleffect = {key: val for key, val in self.skilleffect.items() if val[3] > 0 and self.state in val[5]} # remove effect if time reach 0 and restriction is not met
        for a, b in self.statuseffect.items():
            b[3] -= self.timer
        self.statuseffect = {key: val for key, val in self.statuseffect.items() if val[3] > 0}
        #^ End timer effect

    def update(self, weather, newdt, viewmode, combattimer):
        if self.gamestart == False: # run once when game start or unit just get created
            self.rotate()
            self.findnearbysquad()
            self.statusupdate(weather)
            self.gamestart = True
        self.viewmode = viewmode
        if self.state != 100: # no point update these for dead squad
            dt = newdt
            self.walk = self.battalion.walk # check if battalion walking for stamina use
            self.run = self.battalion.run # check if battalion running for stamina use
            #v Stamina and Health bar and melee combat indicator function
            if self.battalion.hitbox[0].stillclick or self.viewmode == 10:
                if self.oldlasthealth != self.unithealth:
                    healthlist = (self.health75, self.health50, self.health25, 0)
                    for index, health in enumerate(healthlist):
                        if self.unithealth > health:
                            if self.lasthealthstate != abs(4-index):
                                self.image_original.blit(self.images[index+3], self.healthimagerect)
                                self.lasthealthstate = abs(4-index)
                                self.image = self.image_original.copy()
                                self.battalion.squadimgchange.append(self.gameid)
                            break
                    self.troopnumber = self.unithealth / self.troophealth
                    if round(self.troopnumber) < self.troopnumber:  # Calculate how many troop left based on current hp
                        self.troopnumber = round(self.troopnumber + 1)
                    else:
                        self.troopnumber = round(self.troopnumber)
                    self.oldlasthealth = self.unithealth
                if self.oldlaststamina != self.stamina:
                    staminalist = (self.stamina75, self.stamina50, self.stamina25, 0, -1)
                    for index, stamina in enumerate(staminalist):
                        if self.stamina > stamina:
                            if self.laststaminastate != abs(4 - index):
                                if index != 3:
                                    self.image_original.blit(self.images[index + 8], self.staminaimagerect)
                                    self.laststaminastate = abs(4 - index)
                                    self.image = self.image_original.copy()
                                    self.battalion.squadimgchange.append(self.gameid)
                                else:
                                    if self.state != 97:
                                        self.image_original.blit(self.images[12], self.staminaimagerect)
                                        self.laststaminastate = 0
                                        self.oldlaststamina = self.stamina
                                        self.image = self.image_original.copy()
                                        self.battalion.squadimgchange.append(self.gameid)
                            break
                    self.oldlaststamina = self.stamina
                if self.battleside != [None, None, None, None]:  # red corner for side that engage in melee combat
                    for index, side in enumerate(self.battlesideid):
                        if side > 0:
                            self.imagerect = self.images[14 + index].get_rect(center=self.image_original.get_rect().center)
                            self.image.blit(self.images[14 + index], self.imagerect)
                            self.battalion.squadimgchange.append(self.gameid)
                            self.haveredcorner = True
                elif self.haveredcorner == True:
                    self.image = self.image_original.copy()
                    self.haveredcorner = False
            #^ End hp/stamina/melee bar
            if dt > 0: # only run these when game not pause
                self.timer += dt
                battalionstate = self.battalion.state
                if battalionstate in (0, 1, 2, 3, 4, 5, 6, 96, 97, 98, 99) and self.state not in (97, 98, 99):
                    self.state = battalionstate # Enforce battalion state to squad when moving and breaking
                if self.timer > 1: # Update status and skill use around every 1 second
                    self.statusupdate(weather)
                    self.availableskill = []
                    if self.useskillcond != 3:
                        self.checkskillcondition()
                    if self.state == 4 and self.battalion.charging and self.chargeskill not in self.skillcooldown: # use charge skill if run only
                        self.useskill(0) # Use charge skill
                    skillchance = random.randint(0, 10)
                    if skillchance >= 6 and len(self.availableskill) > 0:
                        self.useskill(self.availableskill[random.randint(0, len(self.availableskill) - 1)])
                    self.timer -= 1
                """Melee combat act"""
                if self.nocombat > 0:  # For avoiding squad go into idle state while battalion auto move in melee combat
                    self.nocombat += dt
                    if battalionstate != 10:
                        self.nocombat = 0
                if battalionstate == 10 and self.state not in (97,98,99):
                    if any(battle > 0 for battle in self.battlesideid):
                        self.state = 10
                    elif self.ammo > 0 and (self.arcshot or self.nearbysquadlist[2] == 0):  # Help range attack when battalion in melee combat if has arcshot or frontline
                        self.state = 11
                    elif any(battle > 0 for battle in self.battlesideid) == False: # if suddenly not fighting anyone while in melee combat state
                        if self.nocombat == 0: # Start countdown
                            self.nocombat = 0.1
                        if self.nocombat > 1: # Countdown reach 1 second and still not fight anyone
                            self.state = 0 # Go to idle state
                            self.nocombat = 0
                #v Range attack function
                elif battalionstate == 11 and self.state not in (97,98,99): # Unit in range attack state and self is not collapse or broken
                    self.state = 0 # Default state at idle
                    if self.ammo > 0 and self.attackpos != 0 \
                            and self.shootrange >= self.attackpos.distance_to(self.combatpos): # can shoot if have ammo and in shoot range
                        self.state = 11 # range combat state
                elif self.ammo > 0 and self.battalion.fireatwill == 0 and (self.state == 0 or (battalionstate in (1, 2, 3, 4, 5, 6)
                                                                             and self.shootmove)):  # Fire at will, auto pick closest enemy
                    if self.battalion.neartarget != {}:  # get near target
                        if self.attacktarget == 0:
                            self.attackpos = list(self.battalion.neartarget.values())[0] # replace attacktarget with enemy pos
                            self.attacktarget = list(self.battalion.neartarget.keys())[0] # replace attacktarget with enemy id
                        if self.shootrange >= self.attackpos.distance_to(self.combatpos):
                            self.state = 11
                            if battalionstate in (1, 3, 5):  # Walk and shoot
                                self.state = 12
                            elif battalionstate in (2, 4, 6):  # Run and shoot
                                self.state = 13
                if self.state in (11, 12, 13) and self.reloadtime < self.reload: # reloading ammo
                    self.reloadtime += dt
                    self.stamina = self.stamina - (dt * 2) # use stamina while reloading
                #^ End range attack function
                #v Combat related
                if combattimer >= 0.5: # combat is calculated every 0.5 second in game time
                    if any(battle > 0 for battle in self.battlesideid): # if melee combat (engaging anyone on any side)
                        for index, combat in enumerate(self.battleside):
                            if combat is not None:
                                if self.gameid not in combat.battlesideid:
                                    self.battleside[index] = 0
                                else:
                                    self.dmgcal(combat, index, combat.battlesideid.index(self.gameid), self.maingame.gameunitstat.statuslist, combattimer)
                                    self.stamina = self.stamina - (combattimer * 2)
                    elif self.state in (11, 12, 13): # range combat
                        if type(self.attacktarget) == int and self.attacktarget != 0: # For fire at will, which attacktarge is int
                            allunitindex = self.maingame.allunitindex
                            if self.attacktarget in allunitindex: # if the attack target still alive (if dead it would not be in index list)
                                self.attacktarget = self.maingame.allunitlist[allunitindex.index(self.attacktarget)] # change attacktarget index into sprite
                            else: # enemy dead
                                self.attackpos = 0 # reset attackpos to 0
                                self.attacktarget = 0 # reset attacktarget to 0
                                for target in list(self.battalion.neartarget.values()): # find other nearby target to shoot
                                    if target in allunitindex: # check if target alive
                                        self.attackpos = target[1]
                                        self.attacktarget = target[1]
                                        self.attacktarget = self.maingame.allunitlist[allunitindex.index(self.attacktarget)]
                                        break # found new target break loop
                        if self.reloadtime >= self.reload and (
                                (self.attacktarget == 0 and self.attackpos != 0) or (
                                self.attacktarget != 0 and self.attacktarget.state != 100)): # if reload finish and target existed and not dead
                            rangeattack.Rangearrow(self, self.combatpos.distance_to(self.attackpos), self.shootrange,
                                                   self.viewmode) # Shoot at enemy
                            self.ammo -= 1 # use 1 ammo
                            self.reloadtime = 0 # reset reload time
                        elif self.attacktarget != 0 and self.attacktarget.state == 100: # if target die when it about to shoot
                            self.battalion.rangecombatcheck, self.battalion.attacktarget = 0, 0 # reset range combat check and target
                self.stamina = self.stamina - (dt * 0.5) if self.walk else self.stamina - (dt * 2) if self.run else self.stamina + (
                        dt * self.staminaregen) if self.stamina < self.maxstamina else self.stamina
                #^ End combat related
            if self.basemorale < self.maxmorale:
                if (self.unbreakable or self.tempunbraekable) and self.morale < 30: # unbreakable trait means morale cannot be lower than 30
                    self.morale = 30
                elif self.morale <= 0: # Enter broken state when morale reach 0
                    if self.state != 99: # This is top state above other states except dead for squad
                        self.state = 99 # broken state
                        for squad in self.battalion.squadsprite:
                            squad.basemorale -= 15 # reduce morale of other squad, creating panic when seeing friend panic and may cause mass panic
                    self.morale = 0 # morale cannot be lower than 0
                if self.basemorale < 0:
                    self.basemorale = 0
                if self.battalion.leader[0].state not in (96, 97, 98, 99, 100): # If not missing main leader can replenish morale
                    self.basemorale += (dt * self.staminastatecal) # Morale replenish based on stamina
                if self.state == 99:
                    if self.battalion.state != 99:
                        self.unithealth -= dt*100 # Unit begin to desert if broken but battalion keep fighting
                    if self.moralestatecal > 0.2:
                        self.state = 0  # Reset state to 0 when exit broken state
            elif self.basemorale > self.maxmorale:
                self.basemorale -= dt # gradually reduce morale that exceed the starting max amount
            #v Regen logic
            if self.stamina < self.maxstamina:
                if self.stamina <= 0:  # Collapse and cannot act
                    self.stamina = 0
                    if self.state != 99: # Can only collapse when unit is not broken
                        self.state = 97 # Collapse
                if self.state == 97 and self.stamina > self.stamina25: # exit collapse state
                    self.state = 0 # Reset to idle
            elif self.stamina > self.maxstamina:
                self.stamina = self.maxstamina # stamina cannot exceed the max stamina
            if self.hpregen > 0 and self.unithealth % self.troophealth != 0:  ## hp regen cannot ressurect troop only heal to max hp
                alivehp = self.troopnumber * self.troophealth  ## Max hp possible for the number of alive unit
                self.unithealth += self.hpregen * dt # regen hp back based on time and regen stat
                if self.unithealth > alivehp: self.unithealth = alivehp # Cannot exceed health of alive unit (exceed mean resurrection)
            elif self.hpregen < 0:  ## negative regen can kill
                self.unithealth += self.hpregen * dt # use the same as positive regen (negative regen number * dt will reduce hp)
                self.troopnumber = self.unithealth / self.troophealth  # Recal number of troop again in case some die from negative regen
                if round(self.troopnumber) < self.troopnumber: # no method to always round up number so I need to do this manually
                    self.troopnumber = round(self.troopnumber + 1)
                else:
                    self.troopnumber = round(self.troopnumber)
            if self.unithealth < 0: self.unithealth = 0 # can't have negative hp
            elif self.unithealth > self.maxhealth: self.unithealth = self.maxhealth # hp can't exceed max hp (would increase number of troop)
            if self.state == 97 and self.stamina >= (self.maxstamina/4): self.state = 0 # awake from collaspe when stamina reach 25%
            #^ End regen
            if self.troopnumber <= 0:  # enter dead state
                self.image_original.blit(self.images[7], self.healthimagerect) # blit white hp bar
                self.lasthealthstate = 0
                self.image = self.image_original.copy()
                self.battalion.squadimgchange.append(self.gameid) # add list of squad image to change in battalion image
                self.skillcooldown = {} # remove all cooldown
                self.skilleffect = {} # remove all skill effect
                #v Update squad alive list if squad die
                deadindex = np.where(self.battalion.armysquad == self.gameid)
                deadindex = [deadindex[0], deadindex[1]]
                if self.battalion.squadalive[deadindex[0], deadindex[1]] != 1:
                    self.battalion.squadalive[deadindex[0], deadindex[1]] = 1
                    self.battalion.deadchange = True
                #^ End update
                if self.leader != None and self.leader.name != "None" and self.leader.state != 100: # Find new squad for leader if there is one in this squad
                    for squad in self.nearbysquadlist:
                        if squad != 0 and squad.state != 100 and squad.leader == None:
                            squad.leader = self.leader
                            self.leader.squad = squad
                            for index, squad in enumerate(self.battalion.squadsprite):  # loop to find new squad pos based on new squadsprite list
                                if squad.gameid == self.leader.squad.gameid:
                                    squad.leader.squadpos = index
                            self.leader = None
                            break
                    if self.leader != None:  # if can't find new near squad to move leader then find from first squad to last place in battalion
                        for index, squad in enumerate(self.battalion.squadsprite):
                            if squad.state != 100 and squad.leader == None:
                                squad.leader = self.leader
                                self.leader.squad = squad
                                squad.leader.squadpos = index
                                self.leader = None
                                break
                    if self.leader != None: # Can't find new squad so leader disappear with chance of different result
                        self.leader.state = random.randint(97,100) # captured, retreated, wounded, dead
                        self.leader.health = 0
                        self.leader.gone()
                self.state = 100 # enter dead state
                self.maingame.eventlog.addlog([0, str(self.boardpos) + " " + str(self.name)
                                               + " in " + self.battalion.leader[0].name
                                               + "'s battalion is destroyed"], [3]) # add log to say this squad is destroyed in unit tab

    def rotate(self):
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def command(self, mouse_pos, mouse_up, mouse_right, squadlastselect):
        """For inspect ui clicking"""
        self.wholastselect = squadlastselect
        if self.rect.collidepoint(mouse_pos[0]):
            self.mouse_over = True
            self.whomouseover = self.gameid
            if mouse_up:
                self.selected = True
                self.wholastselect = self.gameid
