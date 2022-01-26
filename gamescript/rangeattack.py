import math
import random

import pygame
import pygame.freetype
from gamescript.tactical.subunit import fight
from pygame.transform import scale


class RangeArrow(pygame.sprite.Sprite):
    angle: float
    images = []
    screen_scale = (1, 1)
    height_map = None

    def __init__(self, shooter, shoot_range, max_range, view_mode, hit_cal=True):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image_original = self.image.copy()
        self.shooter = shooter  # subunit that shoot arrow
        self.speed = self.shooter.arrow_speed  # arrow speed
        self.arcshot = False  # direct shot will no go pass collided unit
        if self.shooter.arc_shot and self.shooter.unit.shoot_mode != 2:
            self.arcshot = True  # arc shot will go pass unit to land at final base_target
        self.height = self.shooter.height
        self.accuracy = self.shooter.accuracy
        self.dmg = random.randint(self.shooter.range_dmg[0], self.shooter.range_dmg[1])
        self.penetrate = self.shooter.range_penetrate
        if self.shooter.state in (12, 13) and self.shooter.agile_aim is False:
            self.accuracy -= 10  # accuracy penalty for shoot while moving
        self.pass_who = None  # check which unit arrow passing through
        self.side = None  # side that arrow collided last
        if hit_cal:
            random_pos1 = random.randint(0, 1)  # for left or right random
            random_pos2 = random.randint(0, 1)  # for up or down random

            # v Calculate hit_chance and final base_target where arrow will land
            hit_chance = self.accuracy * (
                    100 - ((
                                       shoot_range * 100 / max_range) / 2)) / 100  # the further hit_chance from 0 the further arrow will land from base_target
            if hit_chance == 0:
                hit_chance = 1
            if self.shooter.no_range_penal:  # 73 no range penalty
                hit_chance = self.accuracy
            elif self.shooter.long_range_acc:  # 74 long rance accuracy
                hit_chance = self.accuracy * (100 - ((shoot_range * 100 / max_range) / 4)) / 100  # range penalty half

            how_long = shoot_range / self.speed  # shooting distance divide arrow speed to find travel time
            target_now = self.shooter.attack_pos
            if self.shooter.attack_target is not None:
                hit_list = self.shooter.attack_target.subunit_sprite
                if len(hit_list) > 0:
                    target_hit = self.shooter.find_close_target(hit_list)
                    target_now = target_hit.base_pos  # base_target is at the enemy position

                    # v base_target moving, predicatively find position the enemy will be at based on movement speed and arrow travel time
                    if target_hit.state in (1, 3, 5, 7) and how_long > 0.5:  # base_target walking
                        target_move = target_hit.base_target - self.shooter.attack_target.base_pos  # calculate base_target movement distance
                        if target_move.length() > 1:
                            target_move.normalize_ip()
                            target_now = target_hit.base_pos + (
                                    (target_move * (target_hit.unit.walk_speed * how_long)) / 11)
                            if self.shooter.agile_aim is False:
                                hit_chance -= 10
                        else:  # movement too short, simply hit the current position
                            target_now = target_hit.base_pos

                    # base_target running, use run speed to calculate
                    elif target_hit.state in (2, 4, 6, 8, 96, 98, 99) and how_long > 0.5:  # base_target running
                        target_move = target_hit.base_target - target_hit.base_pos
                        if target_move.length() > 1:
                            target_move.normalize_ip()
                            target_now = target_hit.base_pos + (
                                    (target_move * (target_hit.unit.runs_peed * how_long)) / 11)
                            if self.shooter.agile_aim is False:
                                hit_chance -= 20
                        else:
                            target_now = target_hit.base_pos
                    # ^ End base_target moving

            hit_chance = random.randint(int(hit_chance), 100)  # random hit chance
            if random.randint(0, 100) > hit_chance:  # miss, not land exactly at base_target
                if random_pos1 == 0:  # hit_chance convert to percentage from base_target
                    hit_chance1 = 100 + (hit_chance / 50)
                else:
                    hit_chance1 = 100 - (hit_chance / 50)
                if random_pos2 == 0:
                    hit_chance2 = 100 + (hit_chance / 50)
                else:
                    hit_chance2 = 100 + (hit_chance / 50)
                self.base_target = pygame.Vector2(target_now[0] * hit_chance1 / 100, target_now[1] * hit_chance2 / 100)
            else:  # perfect hit, slightly (randomly) land near base_target
                self.base_target = target_now * random.uniform(0.999, 1.001)

        self.target_height = self.height_map.get_height(self.base_target)  # get the height at base_target

        # ^ End calculate hit_chance and base_target

        # v Rotate arrow sprite
        radians = math.atan2(self.base_target[1] - self.shooter.unit.base_pos[1],
                             self.base_target[0] - self.shooter.unit.base_pos[0])
        self.angle = math.degrees(radians)

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
        self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * view_mode
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.target = self.base_target * view_mode

    def range_dmg_cal(self, who, target, target_side, side_percent=(1, 0.3, 0.3, 0)):
        """Calculate hit_chance and defence chance, side_percent is more punishing than melee melee_attack"""
        who_luck = random.randint(-20, 20)  # luck of the attacker subunit
        target_luck = random.randint(-20, 20)  # luck of the defender subunit

        target_percent = side_percent[target_side]  # side penalty
        if target.full_def or target.temp_full_def:
            target_percent = 1  # no side penalty for all round defend
        who_hit = float(self.accuracy) + who_luck  # calculate hit chance
        if who_hit < 0:
            who_hit = 0  # hit_chance cannot be negative

        target_def = float(target.range_def * target_percent) + target_luck  # calculate defence
        if target_def < 0:
            target_def = 0  # defence cannot be negative

        who_dmg, who_morale_dmg, who_leader_dmg = fight.complex_dmg_cal(who, target, who_hit, target_def, self)
        target.unit_health -= who_dmg
        target.base_morale -= who_morale_dmg

        # v Add red corner to indicate melee_dmg
        if target.red_border is False:
            target.block.blit(target.unit_ui_images["ui_squad_combat.png"], target.corner_image_rect)
            target.red_border = True
        # ^ End red corner

        if who.elem_range not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
            target.elem_count[who.elem_range - 1] += round(who_dmg * (100 - target.elem_res[who.elem_range - 1] / 100))

        if target.leader is not None and target.leader.health > 0 and random.randint(0, 10) > 5:  # melee_dmg on leader
            target.leader.health -= who_leader_dmg

    def register_hit(self, subunit=None):
        """Calculate melee_dmg when arrow reach base_target"""
        if subunit is not None:
            angle_check = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
            if angle_check >= 135:  # front
                self.side = 0
            elif angle_check >= 45:  # side
                self.side = 1
            else:  # rear
                self.side = 2

            self.range_dmg_cal(self.shooter, subunit, self.side)  # calculate melee_dmg

    def update(self, unit_list, dt, view_mode):
        move = self.base_target - self.base_pos
        move_length = move.length()

        # v Sprite move
        if move_length > 0:
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.base_pos += move
                if self.arcshot is False:  # direct shot will not be able to shoot pass higher height terrain midway
                    if self.height_map.get_height(self.base_pos) > self.target_height + 20:
                        self.kill()
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * view_mode
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.base_pos = self.base_target
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * view_mode
                self.rect.center = self.pos

            self.dmg -= 0.05  # melee_dmg and penetration power drop the longer arrow travel
            self.penetrate -= 0.002
            if self.dmg < 1:
                self.dmg = 1
            if self.penetrate < 0:
                self.penetrate = 0

            for subunit in pygame.sprite.spritecollide(self, unit_list, 0):
                if subunit != self.shooter:  # and subunit.base_pos.distance_to(self.base_pos) < subunit.image_height:
                    if self.arcshot is False:  # direct shot
                        self.register_hit(subunit)
                        self.kill()
                    else:
                        self.pass_who = subunit
                    break

        else:  # reach base_target
            self.register_hit(self.pass_who)  # register hit whatever subunit the sprite land at
            self.kill()  # remove sprite
