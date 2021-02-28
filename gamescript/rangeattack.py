import math
import random

import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale

from gamescript import gamelongscript


class Rangearrow(pygame.sprite.Sprite): #TODO make range attack dmg drop the longer it travel
    images = []
    gamemapheight = None

    def __init__(self, shooter, shootrange, maxrange, viewmode):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.speed = 50 # arrow speed
        self.image = self.images[0]
        self.image_original = self.image.copy()
        self.shooter = shooter # subunit that shoot arrow
        self.arcshot = False # direct shot will no go pass collided parentunit
        if self.shooter.arcshot and self.shooter.parentunit.shoothow != 2: self.arcshot = True # arc shot will go pass parentunit to land at final target
        self.startheight = self.shooter.height
        self.accuracy = self.shooter.accuracy
        if self.shooter.state in (12, 13) and self.shooter.agileaim == False: self.accuracy -= 10 # accuracy penalty for shoot while moving
        self.passwho = None # check which parentunit arrow passing through
        self.side = None # hitbox side that arrow collided last
        randomposition1 = random.randint(0, 1)  ## randpos1 is for left or right random
        randomposition2 = random.randint(0, 1)  ## randpos1 is for up or down random

        #v Calculate hitchance and final target where arrow will land
        hitchance = self.accuracy * (
                    100 - ((shootrange * 100 / maxrange) / 2)) / 100  # the further hitchance from 0 the further arrow will land from target
        if hitchance == 0: hitchance = 1
        if self.shooter.norangepenal: # 73 no range penalty
            hitchance = self.accuracy
        elif self.shooter.longrangeacc: #  74 long rance accuracy
            hitchance = self.accuracy * (100 - ((shootrange * 100 / maxrange) / 4)) / 100  ## range penalty half

        howlong = shootrange / self.speed # shooting distance divide arrow speed to find travel time
        targetnow = self.shooter.parentunit.baseattackpos
        if self.shooter.attacktarget != 0:
            listtohit = self.shooter.attacktarget.subunitsprite
            targethit = listtohit[random.randint(0,len(listtohit)-1)]
            targetnow = targethit.basepos # target is at the enemy position

            #v target moving, predictively find position the enemy will be at based on movement speed and arrow travel time
            if targethit.state in (1, 3, 5, 7) and howlong > 0.5: # target walking
                targetmove = targethit.target - self.shooter.attacktarget.basepos # calculate target movement distance
                if targetmove.length() > 1:
                    targetmove.normalize_ip()
                    targetnow = targethit.basepos + ((targetmove * (targethit.parentunit.walkspeed * howlong)) / 11)
                    if self.shooter.agileaim == False: hitchance -= 10
                else: # movement too short, simiply hit the current position
                    targetnow = targethit.basepos

            # target running, use run speed to calculate
            elif targethit.state in (2, 4, 6, 8, 96, 98, 99) and howlong > 0.5: # target running
                targetmove = targethit.target - targethit.basepos
                if targetmove.length() > 1:
                    targetmove.normalize_ip()
                    targetnow = targethit.basepos + ((targetmove * (targethit.parentunit.runspeed * howlong)) / 11)
                    if self.shooter.agileaim == False: hitchance -= 20
                else:
                    targetnow = targethit.basepos
            #^ End target moving

        hitchance = random.randint(int(hitchance), 100) # random hit chance
        if random.randint(0, 100) > hitchance: # miss, not land exactly at target
            if randomposition1 == 0: # hitchance convert to percentage from target
                hitchance1 = 100 + (hitchance / 50)
            else:
                hitchance1 = 100 - (hitchance / 50)
            if randomposition2 == 0:
                hitchance2 = 100 + (hitchance / 50)
            else:
                hitchance2 = 100 + (hitchance / 50)
            self.basetarget = pygame.Vector2(targetnow[0] * hitchance1 / 100, targetnow[1] * hitchance2 / 100)
        else: # perfect hit, slightly (randomly) land near target
            self.basetarget = targetnow * random.uniform(0.999, 1.001)

        self.targetheight = self.gamemapheight.getheight(self.basetarget) # get the height at target
        #^ End calculate hitchance and target


        #v Rotate arrow sprite
        myradians = math.atan2(self.basetarget[1] - self.shooter.parentunit.basepos[1], self.basetarget[0] - self.shooter.parentunit.basepos[0])
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

        self.basepos = pygame.Vector2(self.shooter.basepos[0] , self.shooter.basepos[1])
        self.pos = self.basepos * viewmode
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.target = self.basetarget * viewmode

    def rangedmgcal(self, who, target, targetside,sidepercent = [1, 0.3, 0.3, 0]):
        """Calculate hitchance and defense chance, sidepercent is more punishing than melee attack"""
        wholuck = random.randint(-20, 20) # luck of the attacker subunit
        targetluck = random.randint(-20, 20) # luck of the defender subunit

        targetpercent = sidepercent[targetside] # side penalty
        if target.fulldef or target.tempfulldef: targetpercent = 1 # no side penalty for all round defend
        whohit = float(self.accuracy) + wholuck # calculate hit chance
        if whohit < 0: whohit = 0 # hitchance cannot be negative

        targetdefense = float(target.rangedef * targetpercent) + targetluck # calculate defense
        if targetdefense < 0: targetdefense = 0 # defense cannot be negative

        whodmg, whomoraledmg, wholeaderdmg = gamelongscript.losscal(who, target, whohit, targetdefense, 1)
        target.unithealth -= whodmg
        target.basemorale -= whomoraledmg

        # v Add red corner to indicate damage
        if target.haveredcorner == False:
            target.imageblock.blit(target.images[11], target.cornerimagerect)
            target.haveredcorner = True
        # ^ End red corner

        if who.elemrange not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
            target.elemcount[who.elemrange - 1] += round(whodmg * (100 - target.elemresist[who.elemrange - 1] / 100))

        if target.leader != None and target.leader.health > 0 and random.randint(0, 10) > 5:  ## dmg on leader
            target.leader.health -= wholeaderdmg

    def registerhit(self, subunit=None):
        """Calculatte damage when arrow reach target"""
        if subunit is not None:
            anglecheck = abs(self.angle - subunit.angle) # calculate which side arrow hit the subunit
            if anglecheck >= 135: # front
                self.side = 0
            elif anglecheck >= 45: # side
                self.side = 1
            else:  # rear
                self.side = 2

            self.rangedmgcal(self.shooter, subunit, self.side)  # calculate damage

    def update(self, unitlist, dt, viewmode):
        move = self.basetarget - self.basepos
        move_length = move.length()

        #v Sprite move
        if move_length > 0:
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.basepos += move
                if self.arcshot == False: ## direct shot will not be able to shoot pass higher height terrain midway
                    if self.gamemapheight.getheight(self.basepos) > self.targetheight + 20:
                        self.kill()
                self.pos = self.basepos * viewmode
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.basepos = self.basetarget
                self.pos = self.basepos * viewmode
                self.rect.center = self.pos

            for subunit in pygame.sprite.spritecollide(self, unitlist, 0):
                posmask = int(self.pos[0] - subunit.rect.x), int(self.pos[1] - subunit.rect.y)
                try:
                    if subunit.mask.get_at(posmask) == 1:
                        if self.arcshot == False and subunit != self.shooter:  # direct shot
                            self.registerhit(subunit)
                            self.kill()
                        else:
                            self.passwho = subunit
                        break
                except:
                    if self.passwho is not None and self.passwho != subunit:
                        self.passwho = None

        else: # reach target
            self.registerhit(self.passwho) # register hit whatever subunit the sprite land at
            self.kill() # remove sprite
