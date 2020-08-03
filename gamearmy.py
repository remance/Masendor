import random, os.path, glob, csv, math
import pygame
from pygame.transform import scale
from pygame.locals import *
import pygame.freetype
from RTS import mainmenu
from statistics import mean
from RTS import maingame
import ast
from collections import defaultdict
import numpy as np
main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

def rotationxy(origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x,y)

class weaponstat():
    def __init__(self, img):
        self.imgs = img
        self.weaponlist = {}
        with open(main_dir + "\data" + '\\unit_weapon.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.weaponlist[row[0]] = row[1:]
        # self.weaponlist = self.weaponlist[1:]
        unitfile.close()

class unitstat():
    def __init__(self,statusicon,abilityicon,traiticon,roleicon):
        """Stat data read"""
        """status effect list"""
        self.statuslist = {}
        self.statusicon = statusicon
        with open(main_dir + "\data" + '\\unit_status.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif i == "":
                        row[n] = 1
                        if n in [2,3]:
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                    # elif i.isdigit(): row[n] = [int(i)]
                self.statuslist[row[0]] = row[1:]
        unitfile.close()
        """Unit grade list"""
        self.gradelist = {}
        with open(main_dir + "\data" + '\\unit_grade.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                    if n in [12]:
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.gradelist[row[0]] = row[1:]
        unitfile.close()
        """Unit skill list"""
        self.abilitylist = {}
        self.abilityicon = abilityicon
        with open(main_dir + "\data" + '\\unit_ability.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                for n, i in enumerate(row):
                    # print(n, type(n))
                    if run != 0:
                        if n in [2,3,4,5,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,29,30]:
                            if i == "": row[n] = 100
                            else: row[n] = float(i)
                        elif n in [6,8,28,31]:
                            """Convert all condition and status to list"""
                            if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit(): row[n] = [int(i)]
                        elif n == 0: row[n] = int(i)
                run+=1
                self.abilitylist[row[0]] = row[1:]
        unitfile.close()
        """Unit property list"""
        self.traitlist = {}
        self.traiticon = traiticon
        with open(main_dir + "\data" + '\\unit_property.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                    elif i == "": row[n] = 100
                    if n in [19]:
                        if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit(): row[n] = [int(i)]
                    # elif i.isdigit(): row[n] = [int(i)]
                self.traitlist[row[0]] = row[1:]
        unitfile.close()
        """unit role list"""
        self.role = {}
        self.roleicon = roleicon
        with open(main_dir + "\data" + '\\unit_type.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                self.role[row[0]] = row[1:]
        unitfile.close()

class leader():
    def __init__(self, img,option):
        self.imgs = img
        self.leaderlist = {}
        with open(main_dir + "\data\leader" + str(option) + '\\historical_leader.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderlist[row[0]] = row[1:]
        unitfile.close()

class directionarrow(pygame.sprite.Sprite):
    def __init__(self, who):
        """Layer must be called before sprite_init"""
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = who
        self.who.directionarrow = True
        self.lengthgap = self.who.image.get_height()/2
        length = self.who.pos.distance_to(self.who.target) + self.lengthgap
        self.image = pygame.Surface((length*2, length*2), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 0))
        self.image_original = self.image.copy()
        pygame.draw.line(self.image, (0, 0, 0), (self.image.get_width()/2,self.image.get_height()/2), (self.image.get_width()/2-(self.who.pos[0] - self.who.target[0]),
                         self.image.get_height()/2 - (self.who.pos[1] - self.who.target[1])), 5)
        self.rect = self.image.get_rect(center = self.who.pos)

    def update(self, who, enmy, squad, hitbox, squadindex, dt):
        length = self.who.allsidepos[0].distance_to(self.who.target) + self.lengthgap
        if length > 1 and self.who.state != 0:
            self.image = pygame.Surface((length*2, length*2), pygame.SRCALPHA)
            self.image.fill((255, 255, 255, 0))
            # self.image = self.image_original.copy()
            pygame.draw.line(self.image, (0, 0, 0), (self.image.get_width() / 2, self.image.get_height() / 2),
                             (self.image.get_width() / 2 - (self.who.pos[0] - self.who.target[0]),
                              self.image.get_height() / 2 - (self.who.pos[1] - self.who.target[1])), 5)
            self.rect = self.image.get_rect(center=self.who.pos)
        else:
            self.who.directionarrow = False
            self.kill()

class hitbox(pygame.sprite.Sprite):
    def __init__(self, who, side, width, height):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.who = who
        self.side = side
        self.collide = 0
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 128))
        self.image_original = self.image.copy()
        self.oldpos = self.who.allsidepos[self.side]
        self.rect = self.image.get_rect(center=self.who.allsidepos[self.side])
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, who, enmy, squad, squadindex):
        if self.oldpos != self.who.allsidepos[self.side]:
            self.image = pygame.transform.rotate(self.image_original, self.who.angle)
            self.rect = self.image.get_rect(center=self.who.allsidepos[self.side])
            # self.rect.center = self.who.allsidepos[self.side]
            self.mask = pygame.mask.from_surface(self.image)
            self.oldpos = self.who.allsidepos[self.side]
        self.collide = 0


class unitsquad(pygame.sprite.Sprite):
    images = []

    def __init__(self, unitid, gameid, weaponlist, statlist, battalion, position):
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
        self.basechargedef = 100
        self.chargeskill = self.stat[18]
        self.charging = False
        self.skill.insert(0, self.chargeskill)
        self.skill = {x: statlist.abilitylist[x] for x in self.skill}
        self.troophealth = round(self.stat[19] * (int(statlist.gradelist[self.grade][7])/100))
        self.stamina = int(self.stat[20] * (int(statlist.gradelist[self.grade][8])/100))*10
        self.mana = self.stat[21]
        self.meleeweapon = self.stat[22]
        self.rangeweapon = self.stat[23]
        self.basemorale = int(self.stat[24] + int(statlist.gradelist[self.grade][9]))
        self.basediscipline = int(self.stat[25] + int(statlist.gradelist[self.grade][10]))
        self.troopnumber = self.stat[28]
        self.type = self.stat[29]
        self.description = self.stat[32]
        self.criteffect = 100
        self.dmgeffect = 100
        self.hpregen = 0
        self.staminaregen = 1
        self.statuseffect = {}
        self.skilleffect = {}
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
                self.hpregen += trait[13]
                self.staminaregen += trait[14]
                self.basemorale += trait[15]
                self.basediscipline += trait[16]
                self.criteffect += trait[17]
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
        self.inspposition = (position[0]+988, position[1]+37)
        self.rect = self.image.get_rect(topleft=self.inspposition)
        """self.pos is pos for army inspect ui"""
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        """self.pos is pos of battalion"""
        self.combatpos = 0
    #
    # def draw(self, gamescreen):
    #     self.rect = self.image_original.get_rect(topleft=self.inspposition)
    #     gamescreen.blit(self.image, self.rect)

    def useskill(self,whichskill):
        ##charge skill need to seperate since charge power will be used only for charge skill
        if whichskill == 0:
            skillstat = self.skill[list(self.skill)[0]].copy()
            self.skilleffect[self.chargeskill] = skillstat
            self.skillcooldown[self.chargeskill] = skillstat[4]
        ##other skill
        else:
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

    def statusupdate(self,statuslist,dt):
        """calculate stat from stamina and morale state"""
        self.moralestate  = round(((self.basemorale * 100)/self.maxmorale) * (self.authority / 100), 0)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)
        self.discipline = round((self.basediscipline * (self.moralestate / 100)) * (self.staminastate / 100) + (self.authority / 10), 0)
        self.attack = round(((self.baseattack + (self.discipline/10)) * ((self.moralestate/100)+0.1)) * (self.staminastate/100), 0)
        self.meleedef = round(((self.basemeleedef + (self.discipline/10)) * ((self.moralestate/100)+0.1)) * (self.staminastate/100), 0)
        self.rangedef = round(((self.baserangedef + (self.discipline/10)) * ((self.moralestate/100)+0.1)) * (self.staminastate/100), 0)
        self.accuracy = round(self.baseaccuracy * (self.staminastate/100), 0)
        self.reload = round(self.basereload * ((200 - self.staminastate)/100), 0)
        self.chargedef = round(((self.basechargedef + (self.discipline/10)) * ((self.moralestate/100)+0.1)) * (self.staminastate/100), 0)
        self.speed = round(self.basespeed * self.staminastate/100, 0)
        self.charge = round(((self.basecharge + (self.discipline/10)) * ((self.moralestate/100)+0.1)) * (self.staminastate/100), 0)
        self.criteffect = 100
        self.dmgeffect = 100
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
                # self.healthregen += self.skilleffect[status][19]
                # self.staminaregen += self.skilleffect[status][20]
                self.morale = self.basemorale + self.skilleffect[status][21]
                self.discipline = self.discipline + self.skilleffect[status][22]
                #self.sight += self.skilleffect[status][18]
                #self.hidden += self.skilleffect[status][19]
                self.criteffect = round(self.criteffect * (self.skilleffect[status][24] / 100), 0)
                self.dmgeffect = round(self.dmgeffect*(self.skilleffect[status][24]/100), 0)
                """Apply status to self if there is one in skill effect"""
                if self.skilleffect[status][27] != [0]:
                    for effect in self.skilleffect[status][27]:
                        self.statuseffect[effect] = statuslist[effect]
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
                self.range = round(self.range * (statuslist[status][10]/100), 0)
                self.reload = round(self.reload / (statuslist[status][11]/100), 0)
                self.charge = round(self.charge * (statuslist[status][12]/100), 0)
                self.chargedef = round(self.chargedef * (statuslist[status][13]/100), 0)
                # self.healthregen += self.statuseffect[status][14]
                # self.staminaregen += self.statuseffect[status][15]
                self.morale = self.basemorale + self.statuseffect[status][16]
                self.discipline = self.discipline + self.statuseffect[status][17]
                #self.sight += status[18]
                #self.hidden += status[19]
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
        else: self.morale = round(self.basemorale, 0)
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
            if self.stamina < self.maxstamina: self.stamina += dt
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

        self.unitcardvalue = [self.name, str(self.troopnumber) + " (" + str(self.maxtroop) + ")", int(self.stamina), self.morale,
                              self.discipline, self.attack, self.meleedef, self.rangedef, self.armour, self.speed, self.accuracy,
                              self.range, self.ammo, str(int(self.reloadtime)) + " ("  + str(self.reload) + ")", self.charge, self.description]

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

class unitarmy(pygame.sprite.Sprite):
    images = []
    def __init__(self, startposition, gameid, leaderlist, statlist, leader, squadlist,imgsize,colour,control,coa,commander=False):
        # super().__init__()
        self._layer = 3
        pygame.sprite.Sprite.__init__(self, self.containers)
        # self.unitarray = unitarray
        self.armysquad = squadlist
        self.squadsprite = []
        self.commander = commander
        """Alive state array 0 = not exist, 1 = dead, 2 = alive"""
        self.squadalive = np.copy(self.armysquad)
        self.squadalive = np.where(self.squadalive > 0, 2,self.squadalive)
        self.recalsquadcombat = False
        self.groupsquadindex = []
        self.startwhere = []
        self.imgsize = imgsize
        self.widthbox, self.heightbox = len(squadlist[0])*self.imgsize[0], len(squadlist)*self.imgsize[1]
        self.gameid = gameid
        self.control = control
        self.pos, self.attackpos = pygame.Vector2(startposition), 0
        self.angle, self.newangle = 0, 0
        self.moverotate, self.rotatecal, self.rotatecheck  = 0, 0, 0
        self.pause = False
        self.hitbox = []
        self.directionarrow = False
        self.rotateonly = False
        self.retreatstart = 0
        self.retreattimer, self.retreatmax = 0, 0
        self.combatcheck = 0
        self.rangecombatcheck = 0
        self.attacktarget = 0
        self.gotkilled = 0
        self.combatpreparestate = 0
        self.ammo = 0
        self.useminrange = False
        # self.offset = pygame.Vector2(-25, 0)
        self.set_target(startposition)
        self.previousposition = pygame.Vector2(startposition)
        """state 0 = idle, 1 = walking, 2 = running, 3 = attacking/walk, 4 = attacking/walk, 5 = melee combat, 6 = range attack"""
        self.state =  0
        self.preparetimer = 0
        self.deadchange = 0
        self.gamestart = 0
        """leaderwholist is list of 4 leader in 1 battalion. Based on list order: 1st = general, 
        2nd and 3rd = subgeneral, 4th = special role likes advisor, shaman, priest, mage, supporter"""
        self.leaderwho = [leaderlist.leaderlist[oneleader] for oneleader in leader]
        self.authority = round(self.leaderwho[0][3] + self.leaderwho[1][3]/2 + self.leaderwho[2][3]/2 +self.leaderwho[3][3]/4)
        self.tacticeffect = {}
        self.image = pygame.Surface((self.widthbox,self.heightbox), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 128))
        pygame.draw.rect(self.image, (0,0,0),(0, 0, self.widthbox, self.heightbox),2)
        pygame.draw.rect(self.image, colour, (1, 1, self.widthbox-2, self.heightbox-2))
        self.image_empty = self.image.copy()
        self.imagerect = self.images[10].get_rect(center=self.image.get_rect().center)
        self.image.blit(self.images[10], self.imagerect)
        self.healthimage = self.images[0]
        self.healthimagerect = self.healthimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.healthimage, self.healthimagerect)
        self.staminaimage = self.images[5]
        self.staminaimagerect = self.staminaimage.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.staminaimage, self.staminaimagerect)
        self.imagerect = coa.get_rect(center=self.image.get_rect().center)
        self.image.blit(coa, self.imagerect)
        self.image_original, self.image_original2 = self.image.copy(), self.image.copy()
        self.rect = self.image.get_rect(midtop=startposition)
        self.testangle = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.offsetx = self.rect.x
        self.offsety = self.rect.y
        """generate all four side position"""
        self.allsidepos = [(self.rect.center[0], (self.rect.center[1] - self.heightbox / 2) + 1),
                           ((self.rect.center[0] - self.widthbox / 2) + 1, self.rect.center[1]),
                           ((self.rect.center[0] + self.widthbox / 2) - 1, self.rect.center[1]),
                           (self.rect.center[0], (self.rect.center[1] + self.heightbox / 2) - 1)]
        self.squadpositionlist = []
        """index of battleside and frontline: 0 = front 1 = left 2 =right 3 =rear"""
        """battleside keep index of enemy battalion"""
        self.battleside = [0, 0, 0, 0]
        """frontline keep list of squad at the front of each side in combat"""
        self.frontline = {0:[],1:[],2:[],3:[]}
        self.viewmode = 0
        width, height = 0, 0
        squadnum = 0
        """Set up squad position list for drawing"""
        for squad in self.armysquad.flat:
            width += self.imgsize[0]
            self.squadpositionlist.append((width,height))
            squadnum+=1
            if squadnum >= len(self.armysquad[0]):
                width = 0
                height += self.imgsize[1]
                squadnum = 0

    def squadtoarmy(self, squads):
        """drawing squad"""
        squadnum = 0
        truesquadnum = 0
        width, height = 0, 0
        for squad in self.armysquad.flat:
            if squad != 0:
                # def drawtobattalion(self, startposition, battalion):
                # self.rect = self.image.get_rect(topleft=(battalion.image.get_rect(startposition)))
                # self.image.blit(self.image, self.rect)
                self.squadrect = squads[self.groupsquadindex[truesquadnum]].image.copy().get_rect(topleft=(width, height))
                self.image_original.blit(squads[self.groupsquadindex[truesquadnum]].image.copy(), self.squadrect)
                # squad.pos = pygame.Vector2((width,height))
                # squads[self.groupsquadindex[truesquadnum]].drawtobattalion(startposition=(width,height),battalion=self.image)
                # squads[self.groupsquadindex[truesquadnum]].pos = pygame.Vector2(width,height)
                truesquadnum+=1
            width += self.imgsize[0]
            squadnum += 1
            if squadnum >= len(self.armysquad[0]):
                width = 0
                height += self.imgsize[1]
                squadnum = 0

    def setuparmy(self,squadgroup):
        self.stat = {'troop':[],'stamina':[],'morale':[],'speed':[],'disci':[], 'ammo': [], 'range':[], 'novice':[],'militant':[],'pro':[],'vet':[],'elite':[],'champ':[],'hero':[],'religmili':[],'religelite':[],'merc':[],'noble':[]}
        for squad in self.groupsquadindex:
            self.stat['troop'].append(squadgroup[squad].troopnumber)
            if squadgroup[squad].state != 100:
                self.stat['stamina'].append(squadgroup[squad].stamina)
                self.stat['morale'].append(squadgroup[squad].morale)
                self.stat['speed'].append(squadgroup[squad].speed)
                self.stat['disci'].append(squadgroup[squad].discipline)
                self.stat['ammo'].append(squadgroup[squad].ammo)
                self.stat['range'].append(squadgroup[squad].range)
                squadgroup[squad].combatpos = self.pos
                squadgroup[squad].attackpos = self.attackpos
            # self.stat['speed'].append(squad.troopnumber)
            # self.stat['speed'].append(squad.troopnumber)
            else:
                """Update squad alive list if squad die"""
                deadindex = np.where(self.armysquad == squadgroup[squad].gameid)
                deadindex = [deadindex[0], deadindex[1]]
                if self.squadalive[deadindex[0],deadindex[1]] != 1:
                    self.squadalive[deadindex[0],deadindex[1]] = 1
                    self.deadchange = 1
            # self.squadindex = np.where(self.squadalive > -1, self.armysquad, self.squadalive)
        self.troopnumber = int(sum(self.stat['troop']))
        if self.troopnumber > 0:
            self.stamina = int(mean(self.stat['stamina']))
            self.morale = int(mean(self.stat['morale']))
            self.speed = mean(self.stat['speed'])
            self.discipline = mean(self.stat['disci'])
            self.ammo = int(sum(self.stat['ammo']))
            self.maxrange = max(self.stat['range'])
            self.minrange = min(self.stat['range'])
        else:self.stamina,self.morale,self.speed,self.discipline = 0,0,0,0
        if self.gamestart == 0:
            self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 75/100), round(self.stamina * 50/100), round(self.stamina * 25/100)
            self.lasthealthstate, self.laststaminastate = 4, 4
            self.maxmorale = self.morale
            self.maxhealth,self.health75,self.health50,self.health25, = self.troopnumber, round(self.troopnumber*75/100), round(self.troopnumber*50/100) , round(self.troopnumber*25/100)
            self.maxtroop  = self.troopnumber
        self.moralestate = round((self.morale * 100) / self.maxmorale)
        self.staminastate = round((self.stamina * 100) / self.maxstamina)

    def setupfrontline(self,specialcall = False):
        """def to setup frontline"""
        gotanother = 0
        startwhere = 0
        whoarray = np.where(self.squadalive > 1, self.armysquad, self.squadalive)
        """rotate the array based on the side being attack"""
        fullwhoarray = [whoarray, np.fliplr(whoarray.swapaxes(0, 1)),np.rot90(whoarray),np.fliplr([whoarray])[0]]
        # print('full',fullwhoarray)
        whoarray = [whoarray[0], fullwhoarray[1][0], fullwhoarray[2][0],
                    fullwhoarray[3][0]]
        # print('sub', whoarray)
        for index, whofrontline in enumerate(whoarray):
            if self.gamestart == 0 and specialcall == False:
                """Add zero to the frontline so it become 8 row array"""
                emptyarray = np.array([0, 0, 0, 0, 0, 0, 0, 0])
                """Adjust the position of frontline to center of empty 8 array"""
                if len(whofrontline) == 7:whocenter = random.randint(0, 1)
                elif len(whofrontline) == 5:whocenter = random.randint(1, 2)
                elif len(whofrontline) == 3:whocenter = random.randint(2, 3)
                else:whocenter = (8 - len(whofrontline)) / 2
                emptyarray[int(whocenter):int(len(whofrontline) + whocenter)] = whofrontline
                newwhofrontline = emptyarray.copy()
                self.startwhere.append(int(whocenter))
            elif self.gamestart == 1 or specialcall == True:
                newwhofrontline = whofrontline.copy()
                emptyarray = np.array([0, 0, 0, 0, 0, 0, 0, 0])
                """replace the dead in frontline with other squad in the same column"""
                # print('whofront', whofrontline)
                dead = np.where((newwhofrontline == 0) | (newwhofrontline == 1))
                # print('list', dead)
                for deadsquad in dead[0]:
                    run = 0
                    while gotanother == 0:
                        if fullwhoarray[index][run, deadsquad] not in [0, 1]:
                            # print('gotit', fullwhoarray[index][run, deadsquad], 'index', index)
                            newwhofrontline[deadsquad] = fullwhoarray[index][run, deadsquad]
                            gotanother = 1
                        else:
                            # print('notyet', run, fullwhoarray[index][run, deadsquad])
                            run+=1
                            if len(fullwhoarray[index]) == run:
                                # print('fullreach', len(fullwhoarray[index]))
                                newwhofrontline[deadsquad] = 0
                                gotanother = 1
                    gotanother = 0
                whocenter = self.startwhere[startwhere]
                emptyarray[int(whocenter):int(len(newwhofrontline) + whocenter)] = newwhofrontline
                newwhofrontline = emptyarray.copy()
            startwhere += 1
            # print('whofrontline', whofrontline)
            self.frontline[index] = newwhofrontline

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

    def statusupdate(self,statuslist):
        """calculate stat from stamina and morale state"""
        self.moralestate  = round((self.morale * 100)/self.maxmorale)
        self.staminastate = round((self.stamina * 100)/self.maxstamina)
        # """remove cooldown if time reach 0"""
        # removelist = []
        # self.skillcooldown = {key: self.skillcooldown[key]-1 for key in self.skillcooldown}
        # for a, b in self.skillcooldown.items():
        #     if b <= 0: removelist.append(a)
        # for a in sorted(removelist, reverse = True):
        #     self.skillcooldown.pop(a)
        # """remove effect if time reach 0"""
        # removelist = []
        # for a, b in self.skilleffect.items():
        #     b[3] -= 1
        #     if b[3] <= 0: removelist.append(a)
        # for a in sorted(removelist, reverse = True):
        #     self.skilleffect.pop(a)
        # """apply effect from skill"""
        # if len(self.skilleffect) > 0:
        #     for status in self.skilleffect:
        #         self.attack = round(self.attack * self.skilleffect[status][10]/100, 0)
        #         self.meleedef = round(self.meleedef * self.skilleffect[status][11]/100, 0)
        #         self.rangedef = round(self.rangedef * self.skilleffect[status][12]/100, 0)
        #         self.speed = round(self.speed * self.skilleffect[status][13]/100, 0)
        #         self.accuracy = round(self.accuracy * self.skilleffect[status][14]/100, 0)
        #         self.reload = round(self.reload * self.skilleffect[status][15]/100, 0)
        #         self.charge = round(self.charge * self.skilleffect[status][16]/100, 0)
        #         self.chargedef = round(self.charge * self.skilleffect[status][17]/100, 0)
        #         # self.healthregen += self.skilleffect[status][18]
        #         # self.staminaregen += self.skilleffect[status][19]
        #         self.morale = self.basemorale + self.skilleffect[status][20]
        #         self.discipline = self.discipline + self.skilleffect[status][21]
        #         #self.sight += self.skilleffect[status][18]
        #         #self.hidden += self.skilleffect[status][19]
        # """apply effect from status effect"""
        # removelist=[]
        # for a, b in self.statuseffect.items():
        #     if b <= 0: removelist.append(a)
        # for a in sorted(removelist, reverse = True):
        #     self.statuseffect.pop(a)
        # if len(self.statuseffect) > 0:
        #     for status in self.statuseffect:
        #         self.attack = round(self.attack * statuslist[status][4]/100, 0)
        #         self.meleedef = round(self.meleedef * statuslist[status][5]/100, 0)
        #         self.rangedef = round(self.rangedef * statuslist[status][6]/100, 0)
        #         self.armour = round(self.armour * statuslist[status][7]/100, 0)
        #         self.speed = round(self.speed * statuslist[status][8]/100, 0)
        #         self.accuracy = round(self.accuracy * statuslist[status][9]/100, 0)
        #         self.reload = round(self.reload * statuslist[status][10]/100, 0)
        #         self.charge = round(self.charge * statuslist[status][11]/100, 0)
        #         self.chargedef = round(self.chargedef * statuslist[status][12]/100, 0)
        #         # self.healthregen += self.statuseffect[status][13]
        #         # self.staminaregen += self.statuseffect[status][14]
        #         self.morale = self.basemorale + self.statuseffect[status][15]
        #         self.discipline = self.discipline + self.statuseffect[status][16]
        #         #self.sight += status[18]
        #         #self.hidden += status[19]
        # else:
        #     self.morale = round(self.basemorale, 0)
        if self.troopnumber>0:
            self.walkspeed, self.runspeed = (self.speed + self.discipline/100) / 15, (self.speed + self.discipline/100) / 10
            self.rotatespeed = round(self.runspeed*6) / (self.troopnumber/100)
            if self.state in [1,3,5]: self.rotatespeed = round(self.walkspeed*6) / (self.troopnumber/100)
            if self.rotatespeed < 1: self.rotatespeed = 1

    def combatprepare(self,enemyhitbox):
        self.combatpreparestate = 1
        # side, side2 = enemy.allsidepos.copy(), {}
        # for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.allsidepos[0])
        # side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])}
        # self.attackpos = pygame.Vector2(side[list(side2.keys())[0]])
        self.attackpos = enemyhitbox.who.allsidepos[enemyhitbox.side]
        # if list(side2.keys())[0] == 1:
        self.target = enemyhitbox.who.allsidepos[enemyhitbox.side]
        # self.commandtarget = enemyhitbox.who.allsidepos[enemyhitbox.side]
        # enemyhitbox.who.battleside[enemyhitbox.side] = self.gameid
        # self.battleside[0] = enemyhitbox.who.gameid
        self.set_target(self.target)

    def makeallsidepos(self):
        """generate all four side position"""
        self.allsidepos = [(self.rect.center[0], (self.rect.center[1] - self.heightbox / 2)),
                           ((self.rect.center[0] - self.widthbox / 2), self.rect.center[1]),
                           ((self.rect.center[0] + self.widthbox / 2), self.rect.center[1]),
                           (self.rect.center[0], (self.rect.center[1] + self.heightbox / 2))]
        """generate again but with rotation in calculation"""
        self.allsidepos = [rotationxy(self.rect.center, self.allsidepos[0], self.testangle),
                           rotationxy(self.rect.center, self.allsidepos[1], self.testangle)
            , rotationxy(self.rect.center, self.allsidepos[2], self.testangle), rotationxy(self.rect.center, self.allsidepos[3], self.testangle)]

    def update(self,statuslist,squadgroup,dt,viewmode):
        if self.gamestart == 0:
            self.setuparmy(squadgroup)
            self.setupfrontline()
            self.setupfrontline(specialcall=True)
            self.oldarmyhealth, self.oldarmystamina = self.troopnumber, self.stamina
            self.rotate()
            self.makeallsidepos()
            self.target = self.allsidepos[0]
            self.commandtarget = self.allsidepos[0]
            self.gamestart = 1
        if self.state != 100:
            self.offsetx = self.rect.x
            self.offsety = self.rect.y
            self.makeallsidepos()
            self.oldarmyhealth, self.oldarmystamina = self.troopnumber, self.stamina
            self.setuparmy(squadgroup)
            self.statusupdate(statuslist)
            """redraw if troop num or stamina change"""
            if (self.troopnumber != self.oldarmyhealth or self.stamina != self.oldarmystamina) or self.viewmode != viewmode:
                self.viewmode = viewmode
                if self.viewmode == 1:
                    self.image_original = self.image_empty.copy()
                    self.squadtoarmy(squadgroup)
                else:
                    """Change health and stamina bar Function"""
                    if self.troopnumber <= 0 and self.lasthealthstate != 0:
                        self.healthimage = self.images[4]
                        self.healthimagerect = self.healthimage.get_rect(center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 0
                    elif self.troopnumber > 0 and self.troopnumber <= self.health25 and self.lasthealthstate != 1:
                        self.healthimage = self.images[3]
                        self.healthimagerect = self.healthimage.get_rect(center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 1
                    elif self.troopnumber > self.health25 and self.troopnumber <= self.health50 and self.lasthealthstate != 2:
                        self.healthimage = self.images[2]
                        self.healthimagerect = self.healthimage.get_rect(center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 2
                    elif self.troopnumber > self.health50 and self.troopnumber <= self.health75 and self.lasthealthstate != 3:
                        self.healthimage = self.images[1]
                        self.healthimagerect = self.healthimage.get_rect(center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 3
                    elif self.troopnumber > self.health75 and self.lasthealthstate != 4:
                        self.healthimage = self.images[0]
                        self.healthimagerect = self.healthimage.get_rect(center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.healthimage, self.healthimagerect)
                        self.lasthealthstate = 4
                    if self.stamina <= 0 and self.laststaminastate != 0:
                        self.staminaimage = self.images[9]
                        self.staminaimagerect = self.staminaimage.get_rect(center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 0
                    elif self.stamina > 0 and self.stamina <= self.stamina25 and self.laststaminastate != 1:
                        self.staminaimage = self.images[8]
                        self.staminaimagerect = self.staminaimage.get_rect(center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 1
                    elif self.stamina > self.stamina25 and self.stamina <= self.stamina50 and self.laststaminastate != 2:
                        self.staminaimage = self.images[7]
                        self.staminaimagerect = self.staminaimage.get_rect(
                            center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 2
                    elif self.stamina > self.stamina50 and self.stamina <= self.stamina75 and self.laststaminastate != 3:
                        self.staminaimage = self.images[6]
                        self.staminaimagerect = self.staminaimage.get_rect(
                            center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 3
                    elif self.stamina > self.stamina75 and self.laststaminastate != 4:
                        self.staminaimage = self.images[5]
                        self.staminaimagerect = self.staminaimage.get_rect(
                            center=self.image_original2.get_rect().center)
                        self.image_original2.blit(self.staminaimage, self.staminaimagerect)
                        self.laststaminastate = 4
                    self.image_original = self.image_original2.copy()
                self.rotate()
            self.oldlasthealth, self.oldlaststamina = self.lasthealthstate, self.laststaminastate
            """setup frontline again when squad die"""
            if self.deadchange == 1:
                self.setupfrontline()
                for squad in self.groupsquadindex:
                    squadgroup[squad].basemorale -= 20
                self.deadchange = 0
                self.recalsquadcombat = True
            if self.attacktarget != 0: self.attackpos = self.attacktarget.pos
            # """Stamina and Health Function"""
            # if self.troopnumber < 0: self.troopnumber = 0
            # if self.stamina < 0: self.stamina = 0
            # if self.troopnumber > self.maxhealth: self.troopnumber = self.maxhealth
            # if round(self.troopnumber) < self.troopnumber: self.troopnumber = round(self.troopnumber + 1)
            # else: self.troopnumber = round(self.troopnumber)
            # if self.state in [3,4]:
            #     self.target = self.attackpos
            #     if self.attackpos.distance_to(self.pos) < 200 and self.chargeskill not in self.statuseffect and self.chargeskill not in self.skillcooldown:
            #         self.useskill(0)
            if self.battleside != [0,0,0,0]:
                """can not use range attack in melee combat"""
                self.rangecombatcheck = 0
                """enter melee combat state when check"""
                if self.state not in [96,98]:
                    self.state = 10
            if self.rangecombatcheck == 1: self.state = 11
            self.mask = pygame.mask.from_surface(self.image)
            """retreat state"""
            if round(self.morale) <= 20:
                self.state = 98
                if self.retreatstart == 0:
                    self.retreatstart = 1
                """broken state"""
                if self.morale <= 0:
                    self.morale, self.state = 0, 99
                    if self.retreatstart == 0:
                        self.retreatstart = 1
            """only start retreating when ready"""
            if self.retreattimer > 0:
                self.retreattimer += dt
                # print(self.retreatmax, self.retreattimer, self.retreatstart,self.target)
            if self.retreatstart == 1:
                self.retreatmax = len([item for item in self.battleside if item > 0]) * 2 + round(4 - self.preparetimer)
                if self.retreattimer > self.retreatmax:
                    if self.state == 98: self.set_target((self.allsidepos[0][0], self.allsidepos[0][1] - 300))
                    else: self.state = 96
                    self.combatcheck = 0
                    self.retreattimer = 0
                    self.retreatstart = 0
            """Rotate Function"""
            if self.angle != round(self.newangle) and self.stamina > 0 and ((self.hitbox[0].collide == 0 and self.hitbox[3].collide == 0) or (self.preparetimer > 0 and self.preparetimer < 4)):
                self.rotatecal = abs(round(self.newangle) - self.angle)
                self.rotatecheck = 360-self.rotatecal
                self.moverotate = 1
                self.testangle = math.radians(360 - self.angle)
                if self.angle < 0:
                    self.testangle = math.radians(-self.angle)
                if round(self.newangle)>self.angle:
                    if self.rotatecal > 180:
                        self.angle -= self.rotatespeed * dt *50
                        self.rotatecheck -= self.rotatespeed * dt *50
                        if self.rotatecheck <= 0: self.angle = round(self.newangle)
                    else:
                        self.angle += self.rotatespeed * dt *50
                        if self.angle >= self.newangle: self.angle = round(self.newangle)
                elif round(self.newangle)<self.angle:
                    if self.rotatecal > 180:
                        self.angle += self.rotatespeed * dt *50
                        self.rotatecheck -= self.rotatespeed * dt *50
                        if self.rotatecheck <= 0: self.angle = round(self.newangle)
                    else:
                        self.angle -=self.rotatespeed * dt *50
                        if self.angle < self.newangle: self.angle = round(self.newangle)
                self.rotate()
                self.makeallsidepos()
            else:
                self.moverotate = 0
                """Can only enter range attack state after finishing rotate"""
                if self.allsidepos[0].distance_to(self.commandtarget) <= self.maxrange and self.state in [5,6] and self.useminrange != True:
                    self.target = self.allsidepos[0]
                    self.rangecombatcheck = 1
                elif self.allsidepos[0].distance_to(self.commandtarget) <= self.minrange and self.state in [5,6] and self.useminrange == True:
                    self.target = self.allsidepos[0]
                    self.rangecombatcheck = 1
            """Move Function"""
            if self.allsidepos[0] != self.commandtarget and self.rangecombatcheck != 1:
                # """Setup target to move to give position command, this can be changed in move fuction (i.e. stopped due to fight and resume moving after finish fight)"""
                # if self.state not in [10]: self.target = self.commandtarget
                """Chase target and rotate accordingly"""
                if self.state in [3,4,5,6,7,8] and self.target != self.attacktarget.pos:
                    # print(self.attacktarget.pos,self.target)
                    self.target = self.attacktarget.pos
                    self.setrotate(self.target, instant=True)
                """check for hitbox collide according to which ever closest to the target position"""
                if self.state not in [0, 97] and self.stamina > 0 and self.target != self.allsidepos[0] and self.retreattimer == 0:
                    side, side2 = self.allsidepos.copy(), {}
                    for n, thisside in enumerate(side): side2[n] = pygame.Vector2(thisside).distance_to(self.target)
                    side2 = {k: v for k, v in sorted(side2.items(), key=lambda item: item[1])}
                    if ((self.hitbox[list(side2.keys())[0]].collide == 0 and self.hitbox[list(side2.keys())[1]].collide == 0) or (self.preparetimer > 0 and self.preparetimer < 4)) and self.moverotate == 0 and self.rotateonly != True:
                        self.pause = False
                        move = self.target - self.allsidepos[0]
                        move_length = move.length()
                        if (move_length < self.walkspeed and move_length < self.runspeed) and self.battleside == [0,0,0,0] and self.rangecombatcheck == 0:
                            """Stop moving when reach target and go to idle"""
                            self.allsidepos[0] = self.commandtarget
                            self.state =  0
                        # if self.state == 5: self.target = self.pos
                        elif move_length > 1:
                            # if self.state != 3 and self.retreatcommand == 1:
                            move.normalize_ip()
                            if self.state in [2,4,6,96,98,99]: move = move * self.runspeed * dt * 50
                            elif self.state in [1,3,5]: move = move * self.walkspeed * dt * 50
                            elif self.state in [10]: move = move * 3 * dt * 50
                            self.pos += move
                        self.rect.center = list(int(v) for v in self.pos)
                        self.makeallsidepos()
                    elif (self.hitbox[list(side2.keys())[0]].collide != 0 and self.preparetimer <= 0) and self.moverotate == 0 and self.rotateonly != True:
                        self.pause = True
                    elif self.moverotate == 0 and self.rotateonly == True:
                        self.state = 0
                        self.commandtarget = self.allsidepos[0]
                        self.target = self.commandtarget
                        self.rotateonly = False
            if self.stamina <= 0:
                self.state = 97
                self.target = self.allsidepos[0]
                # self.target = self.allsidepos[0]
                self.rangecombatcheck = 0
            if self.state == 97 and self.stamina > 1000: self.state = 0
            if self.battleside == [0, 0, 0, 0]:
                self.combatpreparestate = 0
            self.battleside = [0, 0, 0, 0]
            if self.troopnumber <= 0: self.state = 100
            # self.rect.topleft = self.pos[0],self.pos[1]
        self.valuefortopbar = [str(self.troopnumber) + " (" + str(self.maxtroop) + ")", self.stamina,self.moralestate, self.state]

    def set_target(self, pos):
        self.target = pygame.Vector2(pos)
        # print(self.target)

    def rotate(self):
        # Rotate the image.
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        # Rotate the offset vector.
        # offset_rotated = self.offset.rotate(self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=self.pos)#+offset_rotated)

    def setrotate(self,settarget=0,instant=False):
        self.previousposition = [self.rect.centerx, self.rect.centery]
        if settarget ==0:
            myradians = math.atan2(self.commandtarget[1] - self.previousposition[1], self.commandtarget[0] - self.previousposition[0])
        else: myradians = math.atan2(settarget[1] - self.previousposition[1], settarget[0] - self.previousposition[0])
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

    def command(self, mouse_pos, mouse_up, mouse_right, double_mouse_right, wholastselect, whomouseover,enemyposlist,keystate):
        self.rect = self.rect.clamp(SCREENRECT)
            # self.image = self.images[2] 100))
        if wholastselect == self.gameid and self.control == True and self.state not in [100]:
            """check if right click in mask or not. if not, move unit"""
            posmask = mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y
            if self.state not in [10,97,98,99,100] and mouse_right:
                try:
                    if self.mask.get_at(posmask) == 0:
                        self.state = 1
                        self.rotateonly = False
                        self.attacktarget = 0
                        if whomouseover != 0:
                            if self.ammo <= 0 or keystate[pygame.K_LCTRL] == True:
                                self.state = 3
                            elif self.ammo > 0:
                                """Move to range attack"""
                                self.state = 5
                            self.attacktarget = whomouseover
                            self.attackpos = whomouseover.pos
                        # else: self.attacktarget = 0
                        if double_mouse_right:
                            # if self.combatcheck == 0:
                            self.state = 2
                            if whomouseover != 0:
                                if self.ammo <= 0 or keystate[pygame.K_LCTRL] == True:
                                    self.state = 4
                                elif self.ammo > 0:
                                    self.state = 6
                                self.attacktarget = whomouseover
                                self.attackpos = whomouseover.pos
                            # else:
                            #     self.attacktarget = 0
                        self.rangecombatcheck = 0
                        if keystate[pygame.K_LSHIFT] == True: self.rotateonly = True
                        self.set_target(pygame.mouse.get_pos())
                        self.commandtarget = self.target
                        self.setrotate()
                except:
                    self.state = 1
                    self.rotateonly = False
                    self.attacktarget = 0
                    if whomouseover != 0:
                        if self.ammo <= 0 or keystate[pygame.K_LCTRL] == True:
                            self.state = 3
                        elif self.ammo > 0:
                            """Move to range attack"""
                            self.state = 5
                        self.attacktarget = whomouseover
                        self.attackpos = whomouseover.pos
                    # else: self.attacktarget = 0
                    if double_mouse_right:
                        # if self.combatcheck == 0:
                        self.state = 2
                        if whomouseover != 0:
                            if self.ammo <= 0 or keystate[pygame.K_LCTRL] == True:
                                self.state = 4
                            elif self.ammo > 0:
                                self.state = 6
                            self.attacktarget = whomouseover
                            self.attackpos = whomouseover.pos
                        # else:
                        #     self.attacktarget = 0
                    self.rangecombatcheck = 0
                    if keystate[pygame.K_LSHIFT] == True:self.rotateonly = True
                    self.set_target(pygame.mouse.get_pos())
                    self.commandtarget = self.target
                    self.setrotate()
            elif self.state == 10 and mouse_right:
                """Enter Fall back state if in combat and move command issue"""
                try:
                    if self.mask.get_at(posmask) == 0:
                        if whomouseover == 0:
                            self.state = 96
                            if self.retreattimer == 0:
                                self.retreattimer = 0.1
                                self.retreatstart = 1
                            self.set_target(pygame.mouse.get_pos())
                            self.commandtarget = self.target
                            # self.combatcheck = 0
                except:
                    if whomouseover == 0:
                        self.state = 96
                        if self.retreattimer == 0:
                            self.retreattimer = 0.1
                            self.retreatstart = 1
                        self.set_target(pygame.mouse.get_pos())
                        self.commandtarget = self.target
                        # self.combatcheck = 0

class deadarmy(pygame.sprite.Sprite):
    def __init__(self):
        # super().__init__()
        pygame.sprite.Sprite.__init__(self, self.containers)

    # def statusupdate(self):

    # def update(self):
    #     """Stamina and Health Function"""
    #     self.combatcheck = 0
    #     self.valuefortopbar = [str(self.troopnumber) + " (" + str(self.maxtroop) + ")", self.stamina,self.moralestate, self.state]
    #     self.unitcardvalue = [self.name, str(self.troopnumber) + " (" + str(self.maxtroop) + ")", self.stamina, self.morale,
    #                           self.discipline, self.attack, self.meleedef, self.rangedef, self.armour, self.speed, self.accuracy,
    #                           self.baserange, self.ammo, self.reload, self.basecharge, self.description]

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

class arrow(pygame.sprite.Sprite):
    speed = 8
    images = []
    def __init__(self, shooter, range, maxrange):
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        # if 16 in shooter.trait: self.arcshot = True
        # else self.arcshot = False
        self.image_original = self.image.copy()
        self.shooter = shooter
        self.accuracy = shooter.accuracy
        # self.arc = True
        # self.arcshot = False
        self.passwho = 0
        self.side = None
        # self.lastpasswho = 0
        randomposition1, randomposition2 = random.randint(0,1), random.randint(0,20)
        hitchance = round((100 - self.accuracy * random.randint(1,5)) / (maxrange / range))
        if randomposition1 == 0:
            self.target = pygame.Vector2(shooter.attackpos[0]-hitchance, shooter.attackpos[1]-hitchance)
        else:
            self.target = pygame.Vector2(shooter.attackpos[0]+hitchance, shooter.attackpos[1]+hitchance)
        myradians = math.atan2(self.target[1] - shooter.combatpos[1], self.target[0] - shooter.combatpos[0])
        self.angle = math.degrees(myradians)
        # """upper left -"""
        if self.angle >= -180 and self.angle <= -90:
            self.angle = -self.angle - 90
        # """upper right +"""
        elif self.angle > -90 and self.angle < 0:
            self.angle = (-self.angle) - 90
        # """lower right -"""
        elif self.angle >= 0 and self.angle <= 90:
            self.angle = -(self.angle + 90)
        # """lower left +"""
        elif self.angle > 90 and self.angle <= 180:
            self.angle = 270 - self.angle
        self.image = pygame.transform.rotate(self.image, self.angle)
        if randomposition1 == 0:
            self.rect = self.image.get_rect(midbottom=(shooter.combatpos[0]-randomposition2,shooter.combatpos[1]-randomposition2))
            self.pos = pygame.Vector2(shooter.combatpos[0]-randomposition2,shooter.combatpos[1]-randomposition2)
        else:
            self.rect = self.image.get_rect(midbottom=(shooter.combatpos[0]+randomposition2,shooter.combatpos[1]+randomposition2))
            self.pos = pygame.Vector2(shooter.combatpos[0]+randomposition2,shooter.combatpos[1]+randomposition2)
        self.mask = pygame.mask.from_surface(self.image)

    def rangedmgcal(self, who, target, targetside):
        """Calculate hitchance and defense chance"""
        if targetside == 2: targetside = 3
        elif targetside == 3: targetside = 2
        wholuck, wholuck2 = random.randint(0, 50), random.randint(0, 50)
        targetluck, targetluck2 = random.randint(0, 50), random.randint(0, 50)
        targetpercent = [1,0.8,0.6,0.8][targetside]
        whohit = float(self.accuracy) - wholuck + wholuck2
        targetdefense = float(target.rangedef * targetpercent) - targetluck + targetluck2
        whodmg, whomoraledmg = maingame.battle.losscal(maingame.battle, who=who, target=target, hit=whohit, defense=targetdefense, type='range')
        target.unithealth -= whodmg
        target.basemorale -= whomoraledmg

    def update(self,who,target,hitbox,squadlist,squadindexlist,dt):
        """Who is the player battalion group, target is the enemy battalion group"""
        move = self.target - self.pos
        # if self.state == 5: self.target = self.pos
            # if self.state != 3 and self.retreatcommand == 1:
        move_length = move.length()
        """Calculate which side arrow will hit when it pass unit"""
        for hitbox in pygame.sprite.spritecollide(self, hitbox, 0, collided=pygame.sprite.collide_mask):
            if hitbox.who.gameid != self.shooter.battalion.gameid:
                self.passwho = hitbox.who.gameid
                # if self.passwho != self.lastpasswho:
                self.side = hitbox.side
                # self.lastpasswho = hitbox.who.gameid
        if move_length >= self.speed:
            move.normalize_ip()
            move = move * self.speed * dt * 50
            self.pos += move
            self.rect.center = list(int(v) for v in self.pos)
            self.mask = pygame.mask.from_surface(self.image)
        elif move_length < self.speed:
            """Calculatte damage when arrow reach target"""
            for unit in pygame.sprite.spritecollide(self, who, 0, collided = pygame.sprite.collide_mask):
                calsquadlist = np.where(unit.squadalive > 1, unit.armysquad, unit.squadalive).flat
                calsquadlist = np.delete(calsquadlist, (calsquadlist <= 1).nonzero()[0][:round((np.count_nonzero(calsquadlist <= 1))*self.accuracy/100)])
                squadhit = calsquadlist[random.randint(0, len(calsquadlist) - 1)]
                if squadhit not in [0, 1]:
                    squadhit = np.where(squadindexlist == squadhit)[0][0]
                self.rangedmgcal(self.shooter,squadlist[squadhit],self.side)
            for unit in pygame.sprite.spritecollide(self, target, 0, collided = pygame.sprite.collide_mask):
                calsquadlist = np.where(unit.squadalive > 1, unit.armysquad, unit.squadalive).flat
                calsquadlist = np.delete(calsquadlist, (calsquadlist <= 1).nonzero()[0][:round(
                    (np.count_nonzero(calsquadlist <= 1)) * self.accuracy / 100)])
                squadhit = calsquadlist[random.randint(0, len(calsquadlist) - 1)]
                if squadhit not in [0, 1]:
                    squadhit = np.where(squadindexlist == squadhit)[0][0]
                self.rangedmgcal(self.shooter, squadlist[squadhit], self.side)
            self.kill()
