import math
import random

import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale

from gamescript import gamelongscript


class Rangearrow(pygame.sprite.Sprite):
    images = []
    gamemapheight = None

    def __init__(self, shooter, shootrange, maxrange, viewmode):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speed = 50 # arrow speed
        self.image = self.images[0]
        self.image_original = self.image.copy()
        self.shooter = shooter # squad that shoot arrow
        self.arcshot = False # direct shot will no go pass collided battalion
        if self.shooter.arcshot and self.shooter.battalion.shoothow != 2: self.arcshot = True # arc shot will go pass battalion to land at final target
        self.startheight = self.shooter.battalion.height
        self.accuracy = self.shooter.accuracy
        if self.shooter.state in (12, 13) and self.shooter.agileaim == False: self.accuracy -= 10 # accuracy penalty for shoot while moving
        self.passwho = 0 # check which battalion arrow passing through
        self.side = None # hitbox side that arrow collided last
        randomposition1 = random.randint(0, 1)  ## randpos1 is for left or right random

        #v Calculate hitchance and final target where arrow will land
        hitchance = self.accuracy * (
                    100 - ((shootrange * 100 / maxrange) / 2)) / 100  ## the further hitchance from 0 the further arrow will land from target
        if hitchance == 0: hitchance = 1
        if self.shooter.norangepenal: # 73 no range penalty
            hitchance = self.accuracy
        elif self.shooter.longrangeacc: #  74 long rance accuracy
            hitchance = self.accuracy * (100 - ((shootrange * 100 / maxrange) / 4)) / 100  ## range penalty half
        howlong = shootrange / self.speed # shooting distance divide arrow speed to find travel time
        targetnow = self.shooter.battalion.baseattackpos
        if self.shooter.attacktarget != 0:
            targetnow = self.shooter.attacktarget.basepos # target is at the enemy position

            #v target moving, predictively find position the enemy will be at based on movement speed and arrow travel time
            if self.shooter.attacktarget.state in (1, 3, 5, 7) and self.shooter.attacktarget.moverotate == 0 and howlong > 0.5: # target walking
                targetmove = self.shooter.attacktarget.basetarget - self.shooter.attacktarget.basepos # calculate target movement distance
                if targetmove.length() > 1:
                    targetmove.normalize_ip()
                    targetnow = self.shooter.attacktarget.basepos + ((targetmove * (self.shooter.attacktarget.walkspeed * howlong)) / 11)
                    if self.shooter.agileaim == False: hitchance -= 10
                else: # movement too short, simiply hit the current position
                    targetnow = self.shooter.attacktarget.basepos
            elif self.shooter.attacktarget.state in (2, 4, 6, 8, 96, 98, 99) and self.shooter.attacktarget.moverotate == 0 and howlong > 0.5: # target running
                targetmove = self.shooter.attacktarget.target - self.shooter.attacktarget.basepos
                if targetmove.length() > 1:
                    targetmove.normalize_ip()
                    targetnow = self.shooter.attacktarget.basepos + ((targetmove * (self.shooter.attacktarget.runspeed * howlong)) / 11)
                    if self.shooter.agileaim == False: hitchance -= 20
                else:
                    targetnow = self.shooter.attacktarget.basepos
            #^ End target moving

        hitchance = random.randint(int(hitchance), 100) # random hit chance
        if random.randint(0, 100) > hitchance: # miss, not land exactly at target
            if randomposition1 == 0: # hitchance convert to percentage from target
                hitchance = 100 + (hitchance / 20)
            else:
                hitchance = 100 - (hitchance / 20)
            self.basetarget = pygame.Vector2(targetnow[0] * hitchance / 100, targetnow[1] * hitchance / 100)
        else: # perfect hit, slightly (randomly) land near target
            self.basetarget = targetnow * random.uniform(0.99, 1.01)
        self.targetheight = self.gamemapheight.getheight(self.basetarget) # get the height at target
        #^ End calculate hitchance and target


        #v Rotate arrow sprite
        myradians = math.atan2(self.basetarget[1] - self.shooter.battalion.basepos[1], self.basetarget[0] - self.shooter.battalion.basepos[0])
        self.angle = math.degrees(myradians)
        # """upper left and upper right"""
        if self.angle >= -180 and self.angle < 0:
            self.angle = -self.angle - 90
        # """lower right -"""
        elif self.angle >= 0 and self.angle <= 90:
            self.angle = -(self.angle + 90)
        # """lower left +"""
        elif self.angle > 90 and self.angle <= 180:
            self.angle = 270 - self.angle
        self.image = pygame.transform.rotate(self.image, self.angle)
        #^ End rotate

        self.rect = self.image.get_rect(midbottom=(self.shooter.truepos[0] , self.shooter.truepos[1]))
        self.basepos = pygame.Vector2(self.shooter.truepos[0] , self.shooter.truepos[1])
        self.pos = self.basepos * viewmode
        self.target = self.basetarget * viewmode

    def rangedmgcal(self, who, target, targetside,sidepercent = [1, 0.3, 0.3, 0]):
        """Calculate hitchance and defense chance, sidepercent is more punishing than melee attack"""
        wholuck = random.randint(-20, 20) # luck of the attacker squad
        targetluck = random.randint(-20, 20) # luck of the defender squad
        targetpercent = sidepercent[targetside] # side penalty
        if target.fulldef or target.tempfulldef: targetpercent = 1 # no side penalty for all round defend
        whohit = float(self.accuracy) + wholuck # calculate hit chance
        if whohit < 0: whohit = 0 # hitchance cannot be negative
        targetdefense = float(target.rangedef * targetpercent) + targetluck # calculate defense
        if targetdefense < 0: targetdefense = 0 # defense cannot be negative
        whodmg, whomoraledmg, wholeaderdmg = gamelongscript.losscal(who, target, whohit, targetdefense, 1)
        target.unithealth -= whodmg
        target.basemorale -= whomoraledmg
        if who.elemrange not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
            target.elemcount[who.elemrange - 1] += round(whodmg * (100 - target.elemresist[who.elemrange - 1] / 100))
        if target.leader != None and target.leader.health > 0 and random.randint(0, 10) > 5:  ## dmg on leader
            target.leader.health -= wholeaderdmg

    def registerhit(self, unitlist, squadlist, squadindexlist):
        """Calculatte damage when arrow reach target"""
        if self.arcshot: # arcshot for now randomly pick squad in battalion including empty slot
            if self.side is None: self.side = random.randint(0, 3) # to prevent bug where somehow cannot find side of hitbox
            for unit in pygame.sprite.spritecollide(self, unitlist, 0):
                posmask = int(self.pos[0] - unit.rect.x), int(self.pos[1] - unit.rect.y)
                try:
                    if unit.mask.get_at(posmask) == 1:
                        calsquadlist = np.where(unit.squadalive > 1, unit.armysquad, unit.squadalive).flat
                        calsquadlist = np.delete(calsquadlist,
                                                 (calsquadlist <= 1).nonzero()[0][:round((np.count_nonzero(calsquadlist <= 1)) * self.accuracy / 100)])
                        squadhit = calsquadlist[random.randint(0, len(calsquadlist) - 1)] # randomly pick one squad to receive damage
                        if squadhit not in (0, 1):
                            squadhit = np.where(squadindexlist == squadhit)[0][0]
                            self.rangedmgcal(self.shooter, squadlist[squadhit], self.side)
                except: pass
        elif self.arcshot == False and self.passwho != 0: # direct shot will always hit squad in frontline of the side that get hit
            calsquadlist = self.passwho.frontline[self.side] # get frontline of the side that get hit
            calsquadlist = np.delete(calsquadlist, (calsquadlist == 0).nonzero()[0])
            calsquadlist = np.delete(calsquadlist, (calsquadlist <= 1).nonzero()[0][:round(
                (np.count_nonzero(calsquadlist <= 1)) * self.accuracy / 100)])
            squadhit = calsquadlist[random.randint(0, len(calsquadlist) - 1)] # randomly pick one squad to receive damage
            if squadhit not in (0, 1): # if squad exist
                squadhit = np.where(squadindexlist == squadhit)[0][0] # get squad object from index
                self.rangedmgcal(self.shooter, squadlist[squadhit], self.side) # calculate damage

    def update(self, unitlist, hitbox, squadlist, squadindexlist, dt, viewmode):
        move = self.basetarget - self.basepos
        move_length = move.length()
        #v Calculate which side arrow will hit when it pass unit's hitbox
        for thishitbox in pygame.sprite.spritecollide(self, hitbox, 0):
            if thishitbox.who.gameid != self.shooter.battalion.gameid:
                posmask = int(self.pos[0] - thishitbox.rect.x), int(self.pos[1] - thishitbox.rect.y)
                try:
                    if thishitbox.mask.get_at(posmask) == 1:
                        self.passwho = thishitbox.who
                        self.side = thishitbox.side
                        if self.arcshot == False: # if directshot then register damage right away when hit
                            self.registerhit(unitlist, squadlist, squadindexlist)
                            self.kill()
                except:
                    pass
        #^ End calculate side

        #v Sprite move
        if move_length >= 1:
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.basepos += move
                if self.arcshot == False: ## Non-arc range will not be able to shoot pass higher height terrain midway
                    if self.gamemapheight.getheight(self.basepos) > self.targetheight + 20:
                        self.kill()
                self.pos = self.basepos * viewmode
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.basepos = self.basetarget
                self.pos = self.basepos * viewmode
                self.rect.center = self.pos
        else: # reach target
            self.registerhit(unitlist, squadlist, squadindexlist) # register hit whatever unit the sprite land at
            self.kill() # remove sprite
