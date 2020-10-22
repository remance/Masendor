import csv
import random

import pygame
import pygame.freetype
from pygame.transform import scale

from RTS import mainmenu

SCREENRECT = mainmenu.SCREENRECT

class Unitsquad(pygame.sprite.Sprite):
    images = []
    eventlog = None

    def __init__(self, unitid, gameid, weaponlist, armourlist, statlist, battalion, position, inspectuipos):
        # super().__init__()
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.wholastselect = 0
        self.mouse_over = False
        self.gameid = gameid
        self.unitid = int(unitid)
        self.angle, self.newangle = 0, 0
        """index of battleside: 0 = front 1 = left 2 =rear 3 =right (different than battalion for proper combat rotation)"""
        """battleside keep index of enemy battalion -1 is no combat 0 is no current enemy (idle in combat)"""
        self.battleside = [-1, -1, -1, -1]
        self.moverotate, self.rotatecal, self.rotatecheck = 0, 0, 0
        # self.offset = pygame.Vector2(-25, 0)
        """state 0 = idle, 1 = walking, 2 = running, 3 = attacking/fighting, 4 = retreating"""
        self.state = 0
        self.gamestart = 0
        self.nocombat = 0
        self.battalion = battalion
        stat = statlist.unitlist[self.unitid].copy()
        self.leader = None
        self.boardpos = None ## Used for event log position of squad (Assigned in maingame unit setup)
        self.name = stat[0]
        self.unitclass = stat[1]
        self.grade = stat[2]
        self.race = stat[3]
        self.trait = stat[4]
        self.trait = self.trait + statlist.gradelist[self.grade][11]
        skill = stat[5]
        self.skillcooldown = {}
        self.cost = stat[6]
        self.baseattack = round(stat[8] + int(statlist.gradelist[self.grade][1]), 0)
        self.basemeleedef = round(stat[9] + int(statlist.gradelist[self.grade][2]), 0)
        self.baserangedef = round(stat[10] + int(statlist.gradelist[self.grade][2]), 0)
        self.armourgear = stat[11]
        self.basearmour = armourlist.armourlist[self.armourgear[0]][1] * (
                    armourlist.quality[self.armourgear[1]] / 100)  ## Armour stat is cal from based armour * quality
        self.baseaccuracy = stat[12]
        self.baserange = stat[13]
        self.ammo = stat[14]
        self.basereload = stat[15]
        self.reloadtime = 0
        self.basecharge = stat[16]
        self.basechargedef = 10
        self.chargeskill = stat[17]
        self.charging = False
        skill = [self.chargeskill] + skill
        self.skill = {x: statlist.abilitylist[x].copy() for x in skill if x != 0 and x in statlist.abilitylist}
        self.troophealth = round(stat[18] * (int(statlist.gradelist[self.grade][7]) / 100))
        self.stamina = int(stat[19] * (int(statlist.gradelist[self.grade][8]) / 100)) * 10
        self.mana = stat[20]
        self.meleeweapon = stat[21]
        self.rangeweapon = stat[22]
        self.dmg = weaponlist.weaponlist[self.meleeweapon[0]][1] * (weaponlist.quality[self.meleeweapon[1]] / 100)
        self.penetrate = weaponlist.weaponlist[self.meleeweapon[0]][2] * (weaponlist.quality[self.meleeweapon[1]] / 100)
        if self.penetrate > 100: self.penetrate == 100
        self.rangedmg = weaponlist.weaponlist[self.rangeweapon[0]][1] * (weaponlist.quality[self.rangeweapon[1]] / 100)
        self.rangepenetrate = weaponlist.weaponlist[self.rangeweapon[0]][2] * (weaponlist.quality[self.rangeweapon[1]] / 100)
        self.trait = self.trait + weaponlist.weaponlist[self.meleeweapon[0]][4] ## apply trait from range weapon
        self.trait = self.trait + weaponlist.weaponlist[self.rangeweapon[0]][4] ## apply trait from melee weapon
        if self.rangepenetrate > 100: self.rangepenetrate == 100
        self.basemorale = int(stat[23] + int(statlist.gradelist[self.grade][9]))
        self.basediscipline = int(stat[24] + int(statlist.gradelist[self.grade][10]))
        self.troopnumber = stat[27]
        self.basespeed = 50
        self.mount = statlist.mountlist[stat[29]]
        if stat[29] != 1:
            self.basespeed = self.mount[1]
            self.troophealth += self.mount[2]
            self.basecharge += self.mount[3]
            self.trait = self.trait + self.mount[5] ## Apply mount trait to unit
        self.weight = weaponlist.weaponlist[stat[21][0]][3] + weaponlist.weaponlist[stat[22][0]][3] + \
                      armourlist.armourlist[stat[11][0]][2]
        self.trait = self.trait + armourlist.armourlist[stat[11][0]][4] ## Apply armour trait to unit
        self.basespeed = round((self.basespeed * ((100 - self.weight) / 100)) + int(statlist.gradelist[self.grade][3]), 0)
        if stat[28] in (1, 2):
            self.unittype = stat[28] - 1
            self.featuremod = 1 ## the starting column in unit_terrainbonus of infantry
        elif stat[28] in (3, 4, 5, 6, 7):
            self.unittype = 2
            self.featuremod = 3 ## the starting column in unit_terrainbonus of cavalry
        self.description = stat[-1]
        # if self.hidden
        self.baseelemmelee = 0
        self.baseelemrange = 0
        self.elemcount = [0, 0, 0, 0, 0]  ## Elemental threshold count in this order fire,water,air,earth,poison
        self.tempcount = 0
        fireres = 0
        waterres = 0
        airres = 0
        earthres = 0
        self.magicres = 0
        self.heatres = 0
        self.coldres = 0
        poisonres = 0
        self.criteffect = 1
        self.frontdmgeffect = 1
        self.sidedmgeffect = 1
        self.corneratk = False
        self.flankbonus = 1
        self.flankdef = 0
        self.baseauthpenalty = 0.1
        self.authpenalty = 0.1
        self.basehpregen = 0
        self.basestaminaregen = 1
        self.statuslist = self.battalion.statuslist
        self.statuseffect = {}
        self.skilleffect = {}
        self.baseinflictstatus = {}
        self.specialstatus = []
        """Add trait to base stat"""
        self.trait = list(set([trait for trait in self.trait if trait != 0]))
        if len(self.trait) > 0:
            self.trait = {x: statlist.traitlist[x] for x in self.trait if x in statlist.traitlist} ## Any trait not available in ruleset will be ignored
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
                self.basechargedef *= trait[12]
                self.basehpregen += trait[13]
                self.basestaminaregen += trait[14]
                self.basemorale += trait[15]
                self.basediscipline += trait[16]
                self.criteffect += trait[17]
                fireres += (trait[21]/100)
                waterres += (trait[22]/100)
                airres += (trait[23]/100)
                earthres += (trait[24]/100)
                self.magicres += (trait[25]/100)
                self.heatres += (trait[26]/100)
                self.coldres += (trait[27]/100)
                poisonres += (trait[28]/100)
                if trait[32] != [0]:
                    for effect in trait[32]:
                        self.baseinflictstatus[effect] = trait[1]
                # self.baseelemmelee =
                # self.baseelemrange =
            if 3 in self.trait:  ## Varied training
                self.baseattack *= (random.randint(80, 120) / 100)
                self.basemeleedef *= (random.randint(80, 120) / 100)
                self.baserangedef *= (random.randint(80, 120) / 100)
                # self.basearmour *= (random.randint(80, 120) / 100)
                self.basespeed *= (random.randint(80, 120) / 100)
                self.baseaccuracy *= (random.randint(80, 120) / 100)
                self.baserange *= (random.randint(80, 120) / 100)
                self.basereload *= (random.randint(80, 120) / 100)
                self.basecharge *= (random.randint(80, 120) / 100)
                self.basechargedef *= (random.randint(80, 120) / 100)
                self.basemorale += random.randint(-10, 10)
                self.basediscipline += random.randint(-10, 10)
            if 149 in self.trait:  ## Impetuous
                self.baseauthpenalty += 0.5
        # self.loyalty
        self.elemresist = (fireres,waterres,airres,earthres, poisonres)
        """Role is not type, it represent unit classification from base stat to tell what it excel and has no influence on stat"""
        """1 = Offensive, 2 = Defensive, 3 = Skirmisher, 4 = Shock, 5 = Support, 6 = Magic, 7 = Ambusher, 8 = Sniper , 9 = Recon, 10 = Command"""
        self.role = []
        if self.basearmour > 60 and self.basemeleedef > 60: self.role.append(2)
        if self.baseattack > 60: self.role.append(1)
        if self.basespeed > 40 and self.basearmour < 30: self.role.append(3)
        if self.basecharge > 70: self.role.append(4)
        self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 75 / 100), round(
            self.stamina * 50 / 100), round(self.stamina * 25 / 100)
        self.unithealth = self.troophealth * self.troopnumber
        self.lasthealthstate, self.laststaminastate = 4, 4
        self.maxmorale = self.basemorale
        self.attack, self.meleedef, self.rangedef, self.armour, self.speed, self.accuracy, self.reload, self.morale, self.discipline, self.shootrange, self.charge, self.chargedef \
            = self.baseattack, self.basemeleedef, self.baserangedef, self.basearmour, self.basespeed, self.baseaccuracy, self.basereload, self.basemorale, self.basediscipline, self.baserange, self.basecharge, self.basechargedef
        self.elemmelee = self.baseelemmelee
        self.elemrange = self.baseelemrange
        self.maxhealth, self.health75, self.health50, self.health25, = self.unithealth, round(self.unithealth * 75 / 100), round(
            self.unithealth * 50 / 100), round(self.unithealth * 25 / 100)
        self.oldlasthealth, self.oldlaststamina = self.unithealth, self.stamina
        self.maxtroop = self.troopnumber
        self.walkspeed, self.runspeed = self.basespeed / 15, self.basespeed / 10
        self.moralestate = round((self.basemorale * 100) / self.maxmorale)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.image = self.images[0] ## squad block blue colour for player
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
        image1 = weaponlist.imgs[weaponlist.weaponlist[self.unitclass][5]]
        image1rect = image1.get_rect(center=self.image.get_rect().center)
        self.image.blit(image1, image1rect)
        self.image_original = self.image.copy()
        """position in inspect ui"""
        self.inspposition = (position[0] + inspectuipos[0], position[1] + inspectuipos[1])
        self.rect = self.image.get_rect(topleft=self.inspposition)
        """self.pos is pos for army inspect ui"""
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        """self.combatpos is pos of battalion"""
        self.combatpos = 0
        self.attackpos = self.battalion.baseattackpos

    def useskill(self, whichskill):
        if whichskill == 0:  ##charge skill need to seperate since charge power will be used only for charge skill
            skillstat = self.skill[list(self.skill)[0]].copy()
            self.skilleffect[self.chargeskill] = skillstat
            self.skillcooldown[self.chargeskill] = skillstat[4]
        else:  ##other skill
            skillstat = self.skill[whichskill].copy()
            self.skilleffect[whichskill] = skillstat
            self.skillcooldown[whichskill] = skillstat[4]
        self.stamina -= skillstat[9]
        # self.skillcooldown[whichskill] =

    # def receiveskill(self,whichskill):

    def checkskillcondition(self):
        """Check which skill can be used"""
        self.availableskill = [skill for skill in self.skill if
                               skill not in self.skillcooldown.keys() and skill not in self.skilleffect.keys() and self.state in self.skill[skill][
                                   6] and self.discipline >= self.skill[skill][8] and self.stamina > self.skill[skill][9] and skill != self.chargeskill]
        if self.useskillcond == 1:
            self.availableskill = [skill for skill in self.availableskill if self.staminastate > 50 or self.availableskill[skill][9] == 0]
        elif self.useskillcond == 2:
            self.availableskill = [skill for skill in self.availableskill if self.staminastate > 25 or self.availableskill[skill][9] == 0]

    def findnearbysquad(self):
        """Find nearby friendly squads in the same battalion for applying buff"""
        self.nearbysquadlist = []
        cornersquad = []
        for rowindex, rowlist in enumerate(self.battalion.armysquad.tolist()):
            if self.gameid in rowlist:
                if rowlist.index(self.gameid) - 1 != -1:  ##get squad from left if not at first column
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex][rowlist.index(self.gameid) - 1])
                else:
                    self.nearbysquadlist.append(0)
                if rowlist.index(self.gameid) + 1 != len(rowlist):  ##get squad from right if not at last column
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex][rowlist.index(self.gameid) + 1])
                else:
                    self.nearbysquadlist.append(0)
                if rowindex != 0:  ##get top squad
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex - 1][rowlist.index(self.gameid)])
                    if rowlist.index(self.gameid) - 1 != -1:  ##get top left squad
                        cornersquad.append(self.battalion.spritearray[rowindex - 1][rowlist.index(self.gameid) - 1])
                    else:
                        cornersquad.append(0)
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  ## get top right
                        cornersquad.append(self.battalion.spritearray[rowindex - 1][rowlist.index(self.gameid) + 1])
                    else:
                        cornersquad.append(0)
                else:
                    self.nearbysquadlist.append(0)
                if rowindex != len(self.battalion.spritearray) - 1:  ##get bottom squad
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid)])
                    if rowlist.index(self.gameid) - 1 != -1:  ##get bottom left squad
                        cornersquad.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid) - 1])
                    else:
                        cornersquad.append(0)
                    if rowlist.index(self.gameid) + 1 != len(rowlist):  ## get bottom  right squad
                        cornersquad.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid) + 1])
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

    def statusupdate(self, thisweather, dt):
        """calculate stat from stamina, morale state, skill, status, terrain"""
        ## Maybe make trigger for status update instead of doing it every update for optimise
        self.morale = self.basemorale
        self.authority = self.battalion.authority
        self.commandbuff = self.battalion.commandbuff[self.unittype]
        self.moralestate = round(((self.basemorale * 100) / self.maxmorale) * (self.authority / 100), 0)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.discipline = (self.basediscipline * (self.moralestate / 100)) * (self.staminastate / 100) +self.battalion.leadersocial[self.grade + 1] + (self.authority / 10)
        self.attack = (self.baseattack * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100) + (self.commandbuff * 2)
        self.meleedef = (self.basemeleedef * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100) + (self.commandbuff * 2)
        self.rangedef = (self.baserangedef * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100) + (self.commandbuff * 2)
        self.accuracy = self.baseaccuracy * (self.staminastate / 100) + (self.commandbuff * 2)
        self.reload = self.basereload * ((200 - self.staminastate) / 100)
        self.chargedef = (self.basechargedef * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100) + (self.commandbuff * 2)
        self.speed = self.basespeed * self.staminastate / 100
        self.charge = (self.basecharge * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100) + (self.commandbuff * 2)
        self.shootrange = self.baserange
        self.criteffect = 100
        self.frontdmgeffect = 1
        self.sidedmgeffect = 1
        self.authpenalty = self.baseauthpenalty
        self.corneratk = False
        self.hpregen = self.basehpregen
        self.staminaregen = self.basestaminaregen
        self.inflictstatus = self.baseinflictstatus
        self.elemmelee = self.baseelemmelee
        self.elemrange = self.baseelemrange
        """apply height to range"""
        if self.battalion.height > 100:
            self.shootrange = self.shootrange * self.battalion.height / 100
        """apply status effect from trait"""
        if len(self.trait) > 1:
            for trait in self.trait.values():
                if trait[18] != [0]:
                    for effect in trait[18]:
                        self.statuseffect[effect] = self.statuslist[effect].copy()
                        if trait[1] > 1: # status buff range to nearby friend
                            self.statustonearby(trait[1], effect, self.statuslist[effect].copy())
        """apply effect from terrain and weather"""
        weather = thisweather
        self.attack += weather.meleeatk_buff
        self.meleedef += weather.meleedef_buff
        self.rangedef += weather.rangedef_buff
        self.armour += weather.armour_buff
        self.speed += weather.speed_buff
        self.accuracy += weather.accuracy_buff
        self. reload += weather.reload_buff
        self.charge += weather.charge_buff
        self.chargedef += weather.chargedef_buff
        self.hpregen += weather.hpregen_buff
        self.staminaregen += weather.staminaregen_buff
        self.morale += weather.morale_buff
        self.discipline += weather.discipline_buff
        ## Map feature modifier
        mapfeaturemod = self.battalion.gamemapfeature.featuremod[self.battalion.feature]
        if mapfeaturemod[self.featuremod] != 100:
            speedmod = mapfeaturemod[self.featuremod]
            self.speed *= speedmod
            self.charge *= speedmod
        if mapfeaturemod[self.featuremod + 1] != 100:
            # combatmod = self.battalion.gamemapfeature.featuremod[self.battalion.feature][self.featuremod + 1]
            self.attack *= mapfeaturemod[self.featuremod + 1]
        if mapfeaturemod[self.featuremod + 2] != 100:
            combatmod = mapfeaturemod[self.featuremod + 2]
            self.meleedef *= combatmod
            self.chargedef *= combatmod
        if mapfeaturemod[10] != [0]:
            if 1 in mapfeaturemod[10]:
                self.statuseffect[93] = self.statuslist[93].copy()
                if self.weight > 60 or self.stamina <= 0: ## Drowning
                    self.statuseffect[102] = self.statuslist[102].copy()
                elif self.weight > 30: ## Sinking
                    self.statuseffect[101] = self.statuslist[101].copy()
                elif self.weight < 30: ## Swiming
                    self.statuseffect[104] = self.statuslist[104].copy()
            if 2 in mapfeaturemod[10]: ## Rot feature
                self.statuseffect[54] = self.statuslist[54].copy()
            if 3 in mapfeaturemod[10]: ## Poison
                self.elemcount[4] += (dt * (100 - self.elemresist[5])/100)
        if weather.elem[0] != 0:
            self.elemcount[weather.elem[0]] += (dt * weather.elem[1] * (100 - self.elemresist[weather.elem[0]]) / 100)
        self.rangedef += mapfeaturemod[7]
        # self.hidden += self.battalion.gamemapfeature[self.battalion.feature][6]
        tempreach = mapfeaturemod[9] + weather.temperature
        if tempreach < 0:
            tempreach = tempreach * (100 - self.coldres)/100
        else:
            tempreach = tempreach * (100 - self.heatres)/100
        if self.tempcount != tempreach:
            if tempreach > 0:
                if self.tempcount < tempreach:
                    self.tempcount += dt * (100 - self.heatres)/100
            elif tempreach < 0:
                if self.tempcount > tempreach:
                    self.tempcount -= dt * (100 - self.coldres)/100
            else:
                if self.tempcount > 0:
                    self.tempcount -= dt * (100 - self.heatres)/100
                else:
                    self.tempcount += dt * (100 - self.coldres)/100
        """apply effect from skill"""
        if len(self.skilleffect) > 0:
            for status in self.skilleffect:  ## apply elemental effect to dmg if skill has element
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
                    if calstatus[2] == 3: self.corneratk = True
                """Apply status to self if there is one in skill effect"""
                if calstatus[27] != [0]:
                    for effect in calstatus[27]:
                        self.statuseffect[effect] = self.statuslist[effect].copy()
                        if self.statuseffect[effect][2] > 1:
                            self.statustonearby(self.statuseffect[effect][2], effect, self.statuslist)
                        # if status[2] > 1:
                        #     self.battalion.armysquad
                        # if status[2] > 2:
                """apply inflict status effect to enemy from skill to inflict list"""
                if calstatus[30] != [0]:
                    for effect in calstatus[30]:
                        if effect != [0]: self.inflictstatus[effect] = calstatus[2]
            self.charging = False
            if self.chargeskill in self.skilleffect:
                self.charging = True
                self.authpenalty += 0.5
        """apply effect if elem attack reach 100 threshold"""
        if self.elemcount != [0, 0, 0, 0, 0]:
            self.elemcount[0] = self.thresholdcount(self.elemcount[0], 28, 92)
            self.elemcount[1] = self.thresholdcount(self.elemcount[1], 31, 93)
            self.elemcount[2] = self.thresholdcount( self.elemcount[2], 30, 94)
            self.elemcount[3] = self.thresholdcount(self.elemcount[3], 23, 35)
            self.elemcount[4] = self.thresholdcount(self.elemcount[4], 26, 27)
            self.elemcount = [elem - dt if elem > 0 else elem for elem in self.elemcount]
        """temperature effect"""
        if self.tempcount > 50:
            self.statuseffect[96] = self.statuslist[96].copy()
            if self.tempcount > 100:
                self.statuseffect[97] = self.statuslist[97].copy()
                del self.statuseffect[96]
        if self.tempcount < -50:
            self.statuseffect[95] = self.statuslist[95].copy()
            if self.tempcount < -100:
                self.statuseffect[29] = self.statuslist[29].copy()
                del self.statuseffect[95]
        """apply effect from status effect"""
        """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no attack, 5 no skill, 6 no spell, 7 no exp gain, 
        7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal"""
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
        self.discipline = round(self.discipline, 0)
        self.attack = round((self.attack + (self.discipline / 10)), 0)
        self.meleedef = round((self.meleedef + (self.discipline / 10)), 0)
        self.rangedef = round((self.rangedef + (self.discipline / 10)), 0)
        self.armour = round(self.armour, 0)
        self.speed = round(self.speed, 0)
        self.accuracy = round(self.accuracy, 0)
        self.reload = round(self.reload, 0)
        self.chargedef = round((self.chargedef + (self.discipline / 10)), 0)
        self.charge = round((self.charge + (self.discipline / 10)), 0)
        if self.attack < 0: self.attack = 0
        if self.meleedef < 0: self.meleedef = 0
        if self.rangedef < 0: self.rangedef = 0
        if self.armour < 0: self.armour = 0
        if self.speed < 0: self.speed = 0
        if self.accuracy < 0: self.accuracy = 0
        if self.reload < 0: self.reload = 0
        if self.charge < 0: self.charge = 0
        if self.chargedef < 0: self.chargedef = 0
        if self.discipline < 0: self.discipline = 0
        """remove cooldown if time reach 0"""
        self.skillcooldown = {key: val - dt for key, val in self.skillcooldown.items()}
        self.skillcooldown = {key: val for key, val in self.skillcooldown.items() if val > 0}
        """remove effect if time reach 0 and restriction is met"""
        for a, b in self.skilleffect.items():
            b[3] -= dt
        self.skilleffect = {key: val for key, val in self.skilleffect.items() if val[3] > 0 and self.state in val[5]}
        for a, b in self.statuseffect.items():
            b[3] -= dt
        self.statuseffect = {key: val for key, val in self.statuseffect.items() if val[3] > 0}

    def update(self, weather, squadgroup, dt, viewmode, playerposlist, poslist):
        if self.gamestart == 0:
            self.rotate()
            self.findnearbysquad()
            self.statusupdate(weather, dt)
            self.gamestart = 1
        self.viewmode = viewmode
        if dt > 0:
            self.statusupdate(weather, dt)
        if self.state != 100:
            """Stamina and Health bar function"""
            ## TODO Make all squad image blit happen only when zoom closest or squad shown in inspectui
            if self.oldlasthealth != self.unithealth:
                if self.unithealth > self.health75:
                    if self.lasthealthstate != 4:
                        self.healthimage = self.images[3]
                        self.image_original.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 4
                elif self.unithealth > self.health50:
                    if self.lasthealthstate != 3:
                        self.healthimage = self.images[4]
                        self.image_original.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 3
                elif self.unithealth > self.health25:
                    if self.lasthealthstate != 2:
                        self.healthimage = self.images[5]
                        self.image_original.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 2
                elif self.unithealth > 0:
                    if self.lasthealthstate != 1:
                        self.healthimage = self.images[6]
                        self.image_original.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 1
                self.oldlasthealth = self.unithealth
            if self.oldlaststamina != self.stamina:
                if self.stamina > self.stamina75:
                    if self.laststaminastate != 4:
                        self.staminaimage = self.images[8]
                        self.image_original.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 4
                elif self.stamina > self.stamina50:
                    if self.laststaminastate != 3:
                        self.staminaimage = self.images[9]
                        self.image_original.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 3
                elif self.stamina > self.stamina25:
                    if self.laststaminastate != 2:
                        self.staminaimage = self.images[10]
                        self.image_original.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 2
                elif self.stamina > 0 and self.state != 97:
                    if self.laststaminastate != 1:
                        self.staminaimage = self.images[11]
                        self.image_original.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 1
                elif self.state == 97:
                    if self.laststaminastate != 0:
                        self.staminaimage = self.images[12]
                        self.image_original.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 0
                self.oldlaststamina = self.stamina
            if self.battleside != [-1, -1, -1, -1]:  ## red corner when engage in melee combat
                for index, side in enumerate(self.battleside):
                    if side > 0:
                        self.imagerect = self.images[14 + index].get_rect(center=self.image_original.get_rect().center)
                        self.image.blit(self.images[14 + index], self.imagerect)
            else:
                self.image = self.image_original.copy()
            self.attackpos = self.battalion.baseattackpos
            if self.battalion.attacktarget != 0:
                self.attackpos = self.battalion.attacktarget.basepos
            self.attacktarget = self.battalion.attacktarget
            if self.battalion.state in (0, 1, 2, 3, 4, 5, 6, 96, 97, 98, 99, 100):
                self.state = self.battalion.state
            self.availableskill = []
            if self.useskillcond != 3:
                self.checkskillcondition()
            if self.state in (3, 4):
                if self.attackpos.distance_to(self.combatpos) < 30 \
                        and self.chargeskill not in self.skillcooldown and self.moverotate == 0:
                    self.useskill(0)
            skillchance = random.randint(0, 10)
            if skillchance >= 6 and len(self.availableskill) > 0 and dt != 0:
                self.useskill(self.availableskill[random.randint(0, len(self.availableskill) - 1)])
            """Melee combat act"""
            if self.nocombat > 0: # For avoiding squad go into idle state while battalion auto move in melee combat
                self.nocombat += dt
                if self.battalion.state != 10:
                    self.nocombat = 0
            if self.battalion.state == 10 and self.state != 97:
                if any(battle > 0 for battle in self.battleside):
                    self.state = 10
                elif self.ammo > 0 and 16 in self.trait:  # Help range attack when battalion in melee combat if has arcshot
                    self.state = 11
                elif any(battle > 0 for battle in self.battleside) == False:
                    if self.nocombat == 0:
                        self.nocombat = 0.1
                    if self.nocombat > 1:
                        self.state = 0
                        self.nocombat = 1
            if self.battalion.state == 11:
                if self.ammo > 0 and self.attackpos != 0 and self.shootrange >= self.attackpos.distance_to(self.combatpos):
                    self.state = 11
                else:
                    self.state = 0
            elif self.battalion.fireatwill == 0 and (self.state == 0 or (self.battalion.state in (1, 2, 3, 4, 5, 6)
                                                                         and 18 in self.trait)) and self.ammo > 0: # Fire at will
                if self.attacktarget == 0 and self.battalion.neartarget != 0 and len(
                        self.battalion.neartarget) > 0:  # get near target if no attack target yet
                    self.attackpos = list(self.battalion.neartarget.values())[0]
                    self.attacktarget = list(self.battalion.neartarget.keys())[0]
                    if self.shootrange >= self.attackpos.distance_to(self.combatpos):
                        self.state = 11
                        if self.battalion.state in (1, 3, 5):  # Walk and shoot
                            self.state = 12
                        elif self.battalion.state in (2, 4, 6):  # Run and shoot
                            self.state = 13
            if self.state in (11, 12, 13) and self.reloadtime < self.reload:
                self.reloadtime += dt
            if self.stamina < self.maxstamina: self.stamina += (dt * self.staminaregen)
            self.stamina = self.stamina - (dt * 3) if self.state in (1, 3, 5, 11) and self.battalion.pause == False else self.stamina - (
                    dt * 7) if self.state in (2, 4, 6, 10, 96, 98, 99) and self.battalion.pause == False \
                else self.stamina - (dt * 6) if self.state == 12 else self.stamina - (dt * 14) if self.state == 13 else self.stamina + (
                        dt * self.staminaregen) if self.state == 97 else self.stamina
            if self.basemorale < self.maxmorale and self.state != 99 and self.battalion.leader[0].state not in (96,97,98,99,100):
                self.basemorale += dt
            self.troopnumber = self.unithealth / self.troophealth
            if round(self.troopnumber) < self.troopnumber:  # Calculate how many troop left based on current hp
                self.troopnumber = round(self.troopnumber + 1)
            else:
                self.troopnumber = round(self.troopnumber)
            if self.unithealth % self.troophealth != 0 and self.hpregen > 0:  ## hp regen cannot ressurect troop only heal to max hp
                alivehp = self.troopnumber * self.troophealth  ## Max hp possible for the number of alive unit
                self.unithealth += self.hpregen * dt
                if self.unithealth > alivehp: self.unithealth = alivehp
            elif self.hpregen < 0:  ## negative regen can kill
                self.unithealth += self.hpregen * dt
                self.troopnumber = self.unithealth / self.troophealth  ## recal number of troop again in case some die from negative regen
                if round(self.troopnumber) < self.troopnumber:
                    self.troopnumber = round(self.troopnumber + 1)
                else:
                    self.troopnumber = round(self.troopnumber)
            if self.unithealth < 0: self.unithealth = 0
            if self.unithealth > self.maxhealth: self.unithealth = self.maxhealth
            if self.stamina <= 0:
                self.state = 97
                self.stamina = 0
            if self.state == 97 and self.stamina > 1000: self.state = 0
            """cannot be higher than max hp and max stamina"""
            if self.basemorale <= 0: self.basemorale = 0
            elif self.basemorale > self.maxmorale: self.basemorale -= dt
            if self.stamina > self.maxstamina: self.stamina = self.maxstamina
            if self.troopnumber <= 0:  ## enter dead state
                if self.lasthealthstate != 0:
                    self.healthimage = self.images[7]
                    self.image_original.blit(self.healthimage, self.healthimagerect)
                    self.lasthealthstate = 0
                self.image = self.image_original.copy()
                if self.leader != None and self.leader.state != 100:
                    for squad in self.nearbysquadlist:
                        if squad != 0 and squad.state != 100 and squad.leader == None:
                            squad.leader = self.leader
                            self.leader.squad = squad
                            for index, squad in enumerate(self.battalion.squadsprite):  ## loop to find new squad pos based on new squadsprite list
                                if squad.gameid == self.leader.squad.gameid:
                                    squad.leader.squadpos = index
                            self.leader = None
                            break
                    if self.leader != None:  ## if can't find new near squad to move leader then find from first squad to last place in battalion
                        for index, squad in enumerate(self.battalion.squadsprite):
                            if squad.state != 100 and squad.leader == None:
                                squad.leader = self.leader
                                self.leader.squad = squad
                                squad.leader.squadpos = index
                                self.leader = None
                                break
                self.state = 100
                self.eventlog.addlog([0, str(self.boardpos) + " " + str(self.name) + " in " + self.battalion.leader[0].name +  "'s battalion is destroyed"], [3])
        # else:
        #     self.morale = 0
        #     self.stamina = 0

    def rotate(self):
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def command(self, mouse_pos, mouse_up, mouse_right, squadlastselect):
        self.wholastselect = squadlastselect
        if self.rect.collidepoint(mouse_pos[0]):
            self.mouse_over = True
            self.whomouseover = self.gameid
            if mouse_up:
                self.selected = True
                self.wholastselect = self.gameid