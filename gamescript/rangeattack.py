import math
import random

import pygame
import pygame.freetype
from gamescript import longscript
from pygame.transform import scale


class RangeArrow(pygame.sprite.Sprite):
    angle: float
    images = []
    gamemapheight = None

    def __init__(self, shooter, shootrange, maxrange, viewmode):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image_original = self.image.copy()
        self.shooter = shooter  # subunit that shoot arrow
        self.speed = self.shooter.arrowspeed  # arrow speed
        self.arcshot = False  # direct shot will no go pass collided parentunit
        if self.shooter.arcshot and self.shooter.parentunit.shoothow != 2:
            self.arcshot = True  # arc shot will go pass parentunit to land at final base_target
        self.height = self.shooter.height
        self.accuracy = self.shooter.accuracy
        self.dmg = random.randint(self.shooter.rangedmg[0], self.shooter.rangedmg[1])
        self.penetrate = self.shooter.range_penetrate
        if self.shooter.state in (12, 13) and self.shooter.agileaim is False:
            self.accuracy -= 10  # accuracy penalty for shoot while moving
        self.passwho = None  # check which parentunit arrow passing through
        self.side = None  # hitbox side that arrow collided last
        randompos1 = random.randint(0, 1)  # randpos1 is for left or right random
        randompos2 = random.randint(0, 1)  # randpos1 is for up or down random

        # v Calculate hitchance and final base_target where arrow will land
        hitchance = self.accuracy * (
                100 - ((shootrange * 100 / maxrange) / 2)) / 100  # the further hitchance from 0 the further arrow will land from base_target
        if hitchance == 0:
            hitchance = 1
        if self.shooter.no_range_penal:  # 73 no range penalty
            hitchance = self.accuracy
        elif self.shooter.long_range_acc:  # 74 long rance accuracy
            hitchance = self.accuracy * (100 - ((shootrange * 100 / maxrange) / 4)) / 100  # range penalty half

        howlong = shootrange / self.speed  # shooting distance divide arrow speed to find travel time
        targetnow = self.shooter.attack_pos
        if self.shooter.attack_target is not None:
            listtohit = self.shooter.attack_target.subunit_sprite
            if len(listtohit) > 0:
                targethit = self.shooter.find_close_target(listtohit)
                targetnow = targethit.base_pos  # base_target is at the enemy position

                # v base_target moving, predictively find position the enemy will be at based on movement speed and arrow travel time
                if targethit.state in (1, 3, 5, 7) and howlong > 0.5:  # base_target walking
                    targetmove = targethit.base_target - self.shooter.attack_target.base_pos  # calculate base_target movement distance
                    if targetmove.length() > 1:
                        targetmove.normalize_ip()
                        targetnow = targethit.base_pos + ((targetmove * (targethit.parentunit.walkspeed * howlong)) / 11)
                        if self.shooter.agileaim is False:
                            hitchance -= 10
                    else:  # movement too short, simiply hit the current position
                        targetnow = targethit.base_pos

                # base_target running, use run speed to calculate
                elif targethit.state in (2, 4, 6, 8, 96, 98, 99) and howlong > 0.5:  # base_target running
                    targetmove = targethit.base_target - targethit.base_pos
                    if targetmove.length() > 1:
                        targetmove.normalize_ip()
                        targetnow = targethit.base_pos + ((targetmove * (targethit.parentunit.runspeed * howlong)) / 11)
                        if self.shooter.agileaim is False:
                            hitchance -= 20
                    else:
                        targetnow = targethit.base_pos
                # ^ End base_target moving

        hitchance = random.randint(int(hitchance), 100)  # random hit chance
        if random.randint(0, 100) > hitchance:  # miss, not land exactly at base_target
            if randompos1 == 0:  # hitchance convert to percentage from base_target
                hitchance1 = 100 + (hitchance / 50)
            else:
                hitchance1 = 100 - (hitchance / 50)
            if randompos2 == 0:
                hitchance2 = 100 + (hitchance / 50)
            else:
                hitchance2 = 100 + (hitchance / 50)
            self.basetarget = pygame.Vector2(targetnow[0] * hitchance1 / 100, targetnow[1] * hitchance2 / 100)
        else:  # perfect hit, slightly (randomly) land near base_target
            self.basetarget = targetnow * random.uniform(0.999, 1.001)

        self.targetheight = self.gamemapheight.getheight(self.basetarget)  # get the height at base_target

        # ^ End calculate hitchance and base_target

        # v Rotate arrow sprite
        myradians = math.atan2(self.basetarget[1] - self.shooter.parentunit.base_pos[1], self.basetarget[0] - self.shooter.parentunit.base_pos[0])
        self.angle = math.degrees(myradians)

        # """upper left and upper right"""
        if -180 <= self.angle < 0:
            self.angle = -self.angle - 90

        # """lower right -"""
        elif 0 <= self.angle <= 90:
            self.angle = -(self.angle + 90)

        # """lower left +"""
        elif 90 < self.angle <= 180:
            self.angle = 270 - self.angle

        self.image = pygame.transform.rotate(self.image, self.angle)
        # ^ End rotate

        self.base_pos = pygame.Vector2(self.shooter.base_pos[0], self.shooter.base_pos[1])
        self.pos = self.base_pos * viewmode
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.target = self.basetarget * viewmode

    def range_dmgcal(self, who, target, targetside, sidepercent=(1, 0.3, 0.3, 0)):
        """Calculate hitchance and defence chance, sidepercent is more punishing than melee attack"""
        wholuck = random.randint(-20, 20)  # luck of the attacker subunit
        targetluck = random.randint(-20, 20)  # luck of the defender subunit

        targetpercent = sidepercent[targetside]  # side penalty
        if target.fulldef or target.temp_fulldef:
            targetpercent = 1  # no side penalty for all round defend
        whohit = float(self.accuracy) + wholuck  # calculate hit chance
        if whohit < 0:
            whohit = 0  # hitchance cannot be negative

        targetdefence = float(target.rangedef * targetpercent) + targetluck  # calculate defence
        if targetdefence < 0:
            targetdefence = 0  # defence cannot be negative

        whodmg, whomoraledmg, wholeaderdmg = longscript.losscal(who, target, whohit, targetdefence, self)
        target.unit_health -= whodmg
        target.base_morale -= whomoraledmg

        # v Add red corner to indicate dmg
        if target.red_border is False:
            target.imageblock.blit(target.images[11], target.corner_image_rect)
            target.red_border = True
        # ^ End red corner

        if who.elem_range not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
            target.elem_count[who.elem_range - 1] += round(whodmg * (100 - target.elem_res[who.elem_range - 1] / 100))

        if target.leader is not None and target.leader.health > 0 and random.randint(0, 10) > 5:  # dmg on leader
            target.leader.health -= wholeaderdmg

    def register_hit(self, subunit=None):
        """Calculatte dmg when arrow reach base_target"""
        if subunit is not None:
            anglecheck = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
            if anglecheck >= 135:  # front
                self.side = 0
            elif anglecheck >= 45:  # side
                self.side = 1
            else:  # rear
                self.side = 2

            self.range_dmgcal(self.shooter, subunit, self.side)  # calculate dmg

    def update(self, unitlist, dt, viewmode):
        move = self.basetarget - self.base_pos
        move_length = move.length()

        # v Sprite move
        if move_length > 0:
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.base_pos += move
                if self.arcshot is False:  # direct shot will not be able to shoot pass higher height terrain midway
                    if self.gamemapheight.getheight(self.base_pos) > self.targetheight + 20:
                        self.kill()
                self.pos = self.base_pos * viewmode
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.base_pos = self.basetarget
                self.pos = self.base_pos * viewmode
                self.rect.center = self.pos

            self.dmg -= 0.05  # dmg and penetration power drop the longer arrow travel
            self.penetrate -= 0.002
            if self.dmg < 1:
                self.dmg = 1
            if self.penetrate < 0:
                self.penetrate = 0

            for subunit in pygame.sprite.spritecollide(self, unitlist, 0):
                if subunit != self.shooter:  # and subunit.base_pos.distance_to(self.base_pos) < subunit.imageheight:
                    if self.arcshot is False:  # direct shot
                        self.register_hit(subunit)
                        self.kill()
                    else:
                        self.passwho = subunit
                    break

        else:  # reach base_target
            self.register_hit(self.passwho)  # register hit whatever subunit the sprite land at
            self.kill()  # remove sprite
