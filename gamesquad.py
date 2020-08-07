import random, os.path, glob, csv, math
import pygame
from pygame.transform import scale
import pygame.freetype
from RTS import mainmenu
main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class unitsquad(pygame.sprite.Sprite):
    images = []

    def __init__(self, unitid, gameid, weaponlist, statlist, battalion, position,inspectuipos):
        # super().__init__()
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.wholastselect = 0
        self.mouse_over = False
        self.gameid = gameid
        self.angle, self.newangle = 0, 0
        """index of battleside: 0 = front 1 = left 2 =rear 3 =right (different than battalion for proper combat rotation)"""
        """battleside keep index of enemy battalion -1 is no combat 0 is no current enemy (idle in combat)"""
        self.battleside = [-1, -1, -1, -1]
        self.moverotate, self.rotatecal, self.rotatecheck  = 0, 0, 0
        # self.offset = pygame.Vector2(-25, 0)
        """state 0 = idle, 1 = walking, 2 = running, 3 = attacking/fighting, 4 = retreating"""
        self.state= 0
        self.gamestart = 0
        self.battalion = battalion
        self.authority = battalion.authority
        with open(main_dir + "\data" + '\\unit_stat.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if str(unitid) == row[0]:
                    self.stat = row
                    for n, i in enumerate(self.stat):
                        if i.isdigit():
                            self.stat[n] = int(i)
                        if n in [5,6]:
                            if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit(): row[n] = [int(i)]
        self.name = self.stat[1]
        self.unitclass = self.stat[2]
        self.grade = self.stat[3]
        self.race = self.stat[4]
        self.trait = self.stat[5]
        self.skill = self.stat[6]
        self.skillcooldown = {}
        self.cost = self.stat[7]
        self.baseattack = round(self.stat[8] + int(statlist.gradelist[self.grade][1]), 0)
        self.basemeleedef = round(self.stat[9] + int(statlist.gradelist[self.grade][2]), 0)
        self.baserangedef = round(self.stat[10] + int(statlist.gradelist[self.grade][2]), 0)
        self.basearmour = self.stat[11]
        self.basespeed = round(self.stat[12] + int(statlist.gradelist[self.grade][3]), 0)
        self.baseaccuracy = self.stat[13]
        self.baserange = self.stat[14] * 20
        self.ammo = self.stat[15]
        self.basereload = self.stat[16]
        self.reloadtime = 0
        self.basecharge = self.stat[17]
        self.basechargedef = 10
        self.chargeskill = self.stat[18]
        self.charging = False
        self.skill.insert(0, self.chargeskill)
        self.skill = {x: statlist.abilitylist[x] for x in self.skill if x != 0}
        self.troophealth = round(self.stat[19] * (int(statlist.gradelist[self.grade][7])/100))
        self.stamina = int(self.stat[20] * (int(statlist.gradelist[self.grade][8])/100))*10
        self.mana = self.stat[21]
        self.meleeweapon = self.stat[22]
        self.rangeweapon = self.stat[23]
        self.basemorale = int(self.stat[24] + int(statlist.gradelist[self.grade][9]))
        self.basediscipline = int(self.stat[25] + int(statlist.gradelist[self.grade][10]))
        self.troopnumber = self.stat[28]
        self.type = self.stat[29]
        self.description = self.stat[33]
        self.criteffect = 100
        self.dmgeffect = 100
        self.basehpregen = 0
        self.basestaminaregen = 1
        self.statuseffect = {}
        self.skilleffect = {}
        self.baseinflictstatus = {}
        """Add trait to base stat"""
        if 0 not in self.trait:
            self.trait = {x: statlist.traitlist[x] for x in self.trait}
            for trait in self.trait.values():
                self.baseattack *= (trait[3]/100)
                self.basemeleedef *= (trait[4]/100)
                self.baserangedef *= (trait[5]/100)
                self.basearmour *= (trait[6]/100)
                self.basespeed *= (trait[7]/100)
                self.baseaccuracy *= (trait[8]/100)
                self.baserange *= (trait[9]/100)
                self.basereload *= (trait[10]/100)
                self.basecharge *= (trait[11]/100)
                self.basechargedef *= (trait[12]/100)
                self.basehpregen += trait[13]
                self.basestaminaregen += trait[14]
                self.basemorale += trait[15]
                self.basediscipline += trait[16]
                self.criteffect += trait[17]
                if trait[32] != [0]:
                    for effect in trait[32]:
                        self.baseinflictstatus[effect] = trait[1]
            if 3 in self.trait:
                self.baseattack *= (random.randint(80,120)/100)
                self.basemeleedef *= (random.randint(80,120)/100)
                self.baserangedef *= (random.randint(80,120)/100)
                self.basearmour *= (random.randint(80,120)/100)
                self.basespeed *= (random.randint(80,120)/100)
                self.baseaccuracy *= (random.randint(80,120)/100)
                self.baserange *= (random.randint(80,120)/100)
                self.basereload *= (random.randint(80,120)/100)
                self.basecharge *= (random.randint(80,120)/100)
                self.basechargedef *= (random.randint(80,120)/100)
                self.basemorale += random.randint(-10, 10)
                self.basediscipline += random.randint(-10, 10)
                # self.statuseffect[trait]
        """Role is not type, it represent unit classification from base stat to tell what it excel and has no influence on stat"""
        """1 = Offensive, 2 = Defensive, 3 = Skirmisher, 4 = Shock, 5 = Support, 6 = Magic, 7 = Ambusher, 8 = Sniper , 9 = Recon, 10 = Command"""
        # self.role =
        # self.loyalty
        self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 75/100), round(self.stamina * 50/100), round(self.stamina * 25/100)
        self.unithealth = self.troophealth * self.troopnumber
        self.lasthealthstate, self.laststaminastate = 4, 4
        self.maxmorale = self.basemorale
        self.attack, self.meleedef,self.rangedef,self.armour,self.speed,self.accuracy,self.reload,self.morale,self.discipline, self.range, self.charge, self.chargedef \
            = self.baseattack,self.basemeleedef,self.baserangedef,self.basearmour,self.basespeed,self.baseaccuracy,self.basereload,self.basemorale, self.basediscipline, self.baserange, self.basecharge, self.basechargedef
        self.maxhealth,self.health75,self.health50,self.health25, = self.unithealth, round(self.unithealth*75/100), round(self.unithealth*50/100) , round(self.unithealth*25/100)
        self.maxtroop  = self.troopnumber
        self.walkspeed, self.runspeed = self.basespeed/15, self.basespeed/10
        self.moralestate = round((self.basemorale * 100) / self.maxmorale)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.image = self.images[0]
        """squad block colour"""
        if self.gameid >= 20000:
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
        image1 = weaponlist.imgs[weaponlist.weaponlist[self.unitclass][4]]
        self.dmg = weaponlist.weaponlist[self.meleeweapon][1]
        self.penetrate = weaponlist.weaponlist[self.meleeweapon][2]
        self.rangedmg = weaponlist.weaponlist[self.rangeweapon][1]
        self.rangepenetrate = weaponlist.weaponlist[self.rangeweapon][2]
        image1rect = image1.get_rect(center=self.image.get_rect().center)
        self.image.blit(image1, image1rect)
        self.image_original = self.image.copy()
        """position in inspect ui"""
        self.inspposition = (position[0]+inspectuipos[0], position[1]+inspectuipos[1])
        self.rect = self.image.get_rect(topleft=self.inspposition)
        """self.pos is pos for army inspect ui"""
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        """self.pos is pos of battalion"""
        self.combatpos = 0

    def useskill(self,whichskill):
        if whichskill == 0: ##charge skill need to seperate since charge power will be used only for charge skill
            skillstat = self.skill[list(self.skill)[0]].copy()
            self.skilleffect[self.chargeskill] = skillstat
            self.skillcooldown[self.chargeskill] = skillstat[4]
        else: ##other skill
            skillstat = self.skill[whichskill].copy()
            self.skilleffect[whichskill] = skillstat
            self.skillcooldown[whichskill] = skillstat[4]
        self.stamina -= skillstat[9]
        # self.skillcooldown[whichskill] =
    # def receiveskill(self,whichskill):

    def checkskillcondition(self):
        self.availableskill = []
        for skill in self.skill:
            if skill not in self.skillcooldown.keys() and skill not in self.skilleffect.keys() and self.state in self.skill[skill][7] and self.discipline >= self.skill[skill][8] and self.stamina > self.skill[skill][9]:
                self.availableskill.append(skill)

    def findnearbysquad(self):
        """Find nearby friendly squads in the same battalion for applying buff"""
        self.nearbysquadlist = []
        cornersquad = []
        for rowindex, rowlist in enumerate(self.battalion.armysquad.tolist()):
            if self.gameid in rowlist:
                if rowlist.index(self.gameid) - 1 != -1: ##get squad from left if not at first column
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex][rowlist.index(self.gameid) - 1])
                else: self.nearbysquadlist.append(0)
                if rowlist.index(self.gameid) + 1 != len(rowlist): ##get squad from right if not at last column
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex][rowlist.index(self.gameid) + 1])
                else: self.nearbysquadlist.append(0)
                if rowindex != 0: ##get top squad
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex-1][rowlist.index(self.gameid)])
                    if rowlist.index(self.gameid) - 1 != -1: ##get top left squad
                        cornersquad.append(self.battalion.spritearray[rowindex-1][rowlist.index(self.gameid) - 1])
                    else: cornersquad.append(0)
                    if rowlist.index(self.gameid) + 1 != len(rowlist): ## get top right
                        cornersquad.append(self.battalion.spritearray[rowindex-1][rowlist.index(self.gameid) + 1])
                    else: cornersquad.append(0)
                else: self.nearbysquadlist.append(0)
                if rowindex != len(self.battalion.spritearray) - 1: ##get bottom squad
                    self.nearbysquadlist.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid)])
                    if rowlist.index(self.gameid) - 1 != -1: ##get bottom left squad
                        cornersquad.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid) - 1])
                    else: cornersquad.append(0)
                    if rowlist.index(self.gameid) + 1 != len(rowlist): ## get bottom  right squad
                        cornersquad.append(self.battalion.spritearray[rowindex + 1][rowlist.index(self.gameid) + 1])
                    else: cornersquad.append(0)
                else: self.nearbysquadlist.append(0)
        self.nearbysquadlist = self.nearbysquadlist + cornersquad

    def statustonearby(self,aoe,id,statuslist):
        """apply status effect to nearby unit depending on aoe stat"""
        if aoe in [2, 3]:
            if aoe > 1:
                for squad in self.nearbysquadlist[0:4]:
                    if squad != 0: squad.statuseffect[id] = statuslist[id].copy()
            if aoe > 2:
                for squad in self.nearbysquadlist[4:]:
                    if squad != 0: squad.statuseffect[id] = statuslist[id].copy()
        elif aoe == 4:
            for squad in self.battalion.spritearray.flat:
                if squad.state != 100:
                    squad.statuseffect[id] = statuslist[id].copy()

    def statusupdate(self,statuslist,dt):
        """calculate stat from stamina and morale state"""
        self.morale = self.basemorale
        self.moralestate  = round(((self.basemorale * 100)/self.maxmorale) * (self.authority / 100), 0)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.discipline = round((self.basediscipline * (self.moralestate / 100)) * (self.staminastate / 100) + (self.authority / 10), 0)
        self.attack = round((self.baseattack  * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100), 0)
        self.meleedef = round((self.basemeleedef  * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100), 0)
        self.rangedef = round((self.baserangedef  * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100), 0)
        self.accuracy = round(self.baseaccuracy * (self.staminastate / 100), 0)
        self.reload = round(self.basereload * ((200 - self.staminastate) / 100), 0)
        self.chargedef = round((self.basechargedef  * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100), 0)
        self.speed = round(self.basespeed * self.staminastate / 100, 0)
        self.charge = round((self.basecharge  * ((self.moralestate / 100) + 0.1)) * (self.staminastate / 100), 0)
        self.criteffect = 100
        self.dmgeffect = 100
        self.hpregen = self.basehpregen
        self.staminaregen = self.basestaminaregen
        self.inflictstatus = self.baseinflictstatus
        """apply status effect from trait"""
        if 0 not in self.trait:
            for trait in self.trait.values():
                if trait[18] != [0]:
                    for effect in trait[18]:
                        self.statuseffect[effect] = statuslist[effect].copy()
                        if self.statuseffect[effect][2] > 1:
                            self.statustonearby(self.statuseffect[effect][2], effect, statuslist)

        """apply effect from skill"""
        if len(self.skilleffect) > 0:
            for status in self.skilleffect:
                self.attack = round(self.attack * (self.skilleffect[status][10]/100), 0)
                self.meleedef = round(self.meleedef * (self.skilleffect[status][11]/100), 0)
                self.rangedef = round(self.rangedef * (self.skilleffect[status][12]/100), 0)
                self.speed = round(self.speed * (self.skilleffect[status][13]/100), 0)
                self.accuracy = round(self.accuracy * (self.skilleffect[status][14]/100), 0)
                self.range = round(self.range * (self.skilleffect[status][15] / 100), 0)
                self.reload = round(self.reload / (self.skilleffect[status][16]/100), 0)
                self.charge = round(self.charge * (self.skilleffect[status][17]/100), 0)
                self.chargedef = round(self.charge * (self.skilleffect[status][18]/100), 0)
                self.hpregen += self.skilleffect[status][19]
                self.staminaregen += self.skilleffect[status][20]
                self.morale = self.basemorale + self.skilleffect[status][21]
                self.discipline = self.discipline + self.skilleffect[status][22]
                #self.sight += self.skilleffect[status][18]
                #self.hidden += self.skilleffect[status][19]
                self.criteffect = round(self.criteffect *(self.skilleffect[status][23]/100), 0)
                self.dmgeffect = round(self.dmgeffect * (self.skilleffect[status][24]/100), 0)
                """Apply status to self if there is one in skill effect"""
                if self.skilleffect[status][27] != [0]:
                    for effect in self.skilleffect[status][27]:
                        self.statuseffect[effect] = statuslist[effect].copy()
                        if self.statuseffect[effect][2] > 1:
                            self.statustonearby(self.statuseffect[effect][2], effect, statuslist)
                        # if status[2] > 1:
                        #     self.battalion.armysquad
                        # if status[2] > 2:
                """apply inflict status effect to enemy from skill to inflict list"""
                if self.skilleffect[status][30] != [0]:
                    for effect in self.skilleffect[status][30]:
                        if effect != [0]: self.inflictstatus[effect] = effect[1]
            if self.chargeskill in self.skilleffect: self.charging = True
            else: self.charging = False
        """apply effect from status effect"""
        """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no attack, 5 no skill, 6 no spell, 7 no exp gain, 
        7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal"""
        if len(self.statuseffect) > 0:
            for status in self.statuseffect:
                self.attack = round(self.attack * (statuslist[status][4]/100), 0)
                self.meleedef = round(self.meleedef * (statuslist[status][5]/100), 0)
                self.rangedef = round(self.rangedef * (statuslist[status][6]/100), 0)
                self.armour = round(self.armour * (statuslist[status][7]/100), 0)
                self.speed = round(self.speed * (statuslist[status][8]/100), 0)
                self.accuracy = round(self.accuracy * (statuslist[status][9]/100), 0)
                self.reload = round(self.reload / (statuslist[status][10]/100), 0)
                self.charge = round(self.charge * (statuslist[status][11]/100), 0)
                self.chargedef = round(self.chargedef * (statuslist[status][12]/100), 0)
                self.hpregen += self.statuseffect[status][13]
                self.staminaregen += self.statuseffect[status][14]
                self.morale = self.basemorale + self.statuseffect[status][15]
                self.discipline = self.discipline + self.statuseffect[status][16]
                #self.sight += status[18]
                #self.hidden += status[19]
        self.attack = round((self.attack + (self.discipline/10)), 0)
        self.meleedef = round((self.meleedef + (self.discipline/10)), 0)
        self.rangedef = round((self.rangedef + (self.discipline/10)), 0)
        self.chargedef = round((self.basechargedef + (self.discipline/10)), 0)
        self.charge = round((self.basecharge + (self.discipline/10)), 0)
        if self.attack < 0: self.attack = 0
        if self. meleedef <0: self.meleedef = 0
        if self.rangedef <0: self.rangedef = 0
        if self.armour < 0: self.armour = 0
        if self.speed <0: self.speed = 0
        if self.accuracy <0: self.accuracy = 0
        if self.reload <0 : self.reload = 0
        if self.charge <0: self.charge = 0
        if self.chargedef <0: self.chargedef = 0
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

    def update(self,statuslist,squadgroup,dt,viewmode):
        if self.gamestart == 0:
            self.rotate()
            self.findnearbysquad()
            self.gamestart = 1
        self.statusupdate(statuslist,dt)
        self.oldlasthealth,self.oldlaststamina = self.lasthealthstate, self.laststaminastate
        if self.state != 100:
            """Stamina and Health Function"""
            if self.unithealth <= 0 and self.lasthealthstate != 0:
                self.healthimage = self.images[7]
                self.healthimagerect = self.healthimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.healthimage, self.healthimagerect)
                self.lasthealthstate = 0
            elif self.unithealth > 0 and self.unithealth <= self.health25 and self.lasthealthstate != 1:
                self.healthimage = self.images[6]
                self.healthimagerect = self.healthimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.healthimage, self.healthimagerect)
                self.lasthealthstate = 1
            elif self.unithealth > self.health25 and self.unithealth <= self.health50 and self.lasthealthstate != 2:
                self.healthimage = self.images[5]
                self.healthimagerect = self.healthimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.healthimage, self.healthimagerect)
                self.lasthealthstate = 2
            elif self.unithealth > self.health50 and self.unithealth <= self.health75 and self.lasthealthstate != 3:
                self.healthimage = self.images[4]
                self.healthimagerect = self.healthimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.healthimage, self.healthimagerect)
                self.lasthealthstate = 3
            elif self.unithealth > self.health75 and self.lasthealthstate != 4:
                self.healthimage = self.images[3]
                self.healthimagerect = self.healthimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.healthimage, self.healthimagerect)
                self.lasthealthstate = 4
            if self.state == 97:
                self.staminaimage = self.images[12]
                self.staminaimagerect = self.staminaimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.staminaimage, self.staminaimagerect)
                self.laststaminastate = 0
            elif self.stamina > 0 and self.stamina <= self.stamina25 and self.laststaminastate != 1 and self.state != 97:
                self.staminaimage = self.images[11]
                self.staminaimagerect = self.staminaimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.staminaimage, self.staminaimagerect)
                self.laststaminastate = 1
            elif self.stamina > self.stamina25 and self.stamina <= self.stamina50 and self.laststaminastate != 2:
                self.staminaimage = self.images[10]
                self.staminaimagerect = self.staminaimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.staminaimage, self.staminaimagerect)
                self.laststaminastate = 2
            elif self.stamina > self.stamina50 and self.stamina <= self.stamina75 and self.laststaminastate != 3:
                self.staminaimage = self.images[9]
                self.staminaimagerect = self.staminaimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.staminaimage, self.staminaimagerect)
                self.laststaminastate = 3
            elif self.stamina > self.stamina75 and self.laststaminastate != 4:
                self.staminaimage = self.images[8]
                self.staminaimagerect = self.staminaimage.get_rect(center=self.image_original.get_rect().center)
                self.image_original.blit(self.staminaimage, self.staminaimagerect)
                self.laststaminastate = 4
            if self.battleside != [-1,-1,-1,-1]:
                for index, side in enumerate(self.battleside):
                    if side > 0:
                        self.imagerect = self.images[14+index].get_rect(center=self.image_original.get_rect().center)
                        self.image.blit(self.images[14+index], self.imagerect)
            else: self.image = self.image_original.copy()
            if self.oldlasthealth != self.lasthealthstate or self.oldlaststamina != self.laststaminastate: self.rotate()
                    # if self.retreatstart == 0:
                    #     self.angle = 180
                    #     self.rotate()
                    #     self.retreatstart = 1
            # else: self.retreatstart = 0
            # """Rotate Function"""
            # self.set_target(battalion.target)
            # self.previousposition = [self.rect.centerx, self.rect.centery]
            # myradians = math.atan2(self.target[1] - self.previousposition[1], self.target[0] - self.previousposition[0])
            # self.newangle = math.degrees(myradians)
            # # """upper left -"""
            # if self.newangle >= -180 and self.newangle <= -90:
            #     self.newangle = -self.newangle - 90
            # # """upper right +"""
            # elif self.newangle > -90 and self.newangle < 0:
            #     self.newangle = (-self.newangle) - 90
            # # """lower right -"""
            # elif self.newangle >= 0 and self.newangle <= 90:
            #     self.newangle = -(self.newangle + 90)
            # # """lower left +"""
            # elif self.newangle > 90 and self.newangle <= 180:
            #     self.newangle = 270 - self.newangle
            if self.battalion.state in [0,1,2,3,4,5,6,96,97,98,99,100]:
                self.state = self.battalion.state
            """Using skill condition"""
            self.checkskillcondition()
            if self.state in [3,4]:
                if self.attackpos.distance_to(self.combatpos) < 300 and self.chargeskill not in self.statuseffect and self.chargeskill not in self.skillcooldown and self.moverotate == 0:
                    self.useskill(0)
            skillchance = random.randint(0,10)
            if skillchance >= 6 and len(self.availableskill) > 0:
                # print('use', self.gameid)
                self.useskill(self.availableskill[random.randint(0, len(self.availableskill)-1)])
            """Melee combat act"""
            if self.battalion.state == 10 and self.state not in [97]:
                self.state = 0
                if any(battle > 0 for battle in self.battleside) == True:
                    self.state = 10
                elif self.ammo > 0 and 16 in self.trait: ##help range attack when battalion in melee combat
                    self.state = 11
            if self.battalion.state == 11:
                self.state = 0
                if self.ammo >0 and self.range+150 >= self.attackpos.distance_to(self.combatpos):
                    self.state = 11
            if self.state == 11 and self.reloadtime<self.reload:
                self.reloadtime += dt
            if self.stamina < self.maxstamina: self.stamina += (dt*self.staminaregen)
            self.stamina = self.stamina - (dt*4) if self.state in [1, 3, 5, 11] and self.battalion.pause == False else self.stamina - (dt*7) if self.state in [2,4, 6,10, 96, 98, 99] and self.battalion.pause == False \
                else self.stamina + (dt*2) if self.state == 97 else self.stamina
            if self.basemorale < self.maxmorale: self.basemorale += dt
            if self.unithealth < 0: self.unithealth = 0
            if self.unithealth > self.maxhealth: self.unithealth = self.maxhealth
            self.troopnumber = self.unithealth / self.troophealth
            if round(self.troopnumber) < self.troopnumber: self.troopnumber = round(self.troopnumber + 1)
            else: self.troopnumber = round(self.troopnumber)
            self.battleside = [-1, -1, -1, -1]
            if self.basemorale <= 0:self.basemorale = 0
            if self.stamina <= 0:
                self.state = 97
                self.stamina = 0
            if self.state == 97 and self.stamina > 1000: self.state = 0
            """cannot be higher than max hp and max stamina"""
            if self.morale > self.maxmorale: self.morale = self.maxmorale
            if self.stamina > self.maxstamina: self.stamina = self.maxstamina
            """dead state"""
            if self.troopnumber <= 0: self.state = 100
            # self.rect.topleft = self.pos[0],self.pos[1]
        else:
            self.morale = 0
            self.stamina = 0

        self.unitcardvalue = [self.name, str(self.troopnumber) + " (" + str(self.maxtroop) + ")", int(self.stamina), int(self.morale),
                              int(self.discipline), int(self.attack), int(self.meleedef), int(self.rangedef), int(self.armour), int(self.speed), int(self.accuracy),
                              int(self.range), self.ammo, str(int(self.reloadtime)) + " ("  + str(self.reload) + ")", self.charge, self.chargedef, self.description]
        self.unitcardvalue2 = [self.trait, self.skill, self.skillcooldown, self.skilleffect, self.statuseffect]

    def rotate(self):
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def command(self, mouse_pos, mouse_up, mouse_right,squadlastselect):
        self.wholastselect = squadlastselect
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            self.whomouseover = self.gameid
            if mouse_up:
                self.selected = True
                self.wholastselect = self.gameid
                    # self.image = self.images[2] 100))
        # if wholastselect == self.gameid:
            # if mouse_right and self.rect.collidepoint(mouse_pos) == True:
