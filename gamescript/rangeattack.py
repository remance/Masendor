import math
import random

import pygame
import pygame.freetype
from gamescript.common import animation
from pygame.transform import scale


class RangeAttack(pygame.sprite.Sprite):
    images = []
    screen_scale = (1, 1)
    height_map = None

    play_animation = animation.play_animation

    def __init__(self, shooter, weapon, dmg, penetrate, speed, shoot_range, max_range, view_mode, hit_cal=True):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image_original = self.image.copy()
        self.shooter = shooter  # subunit that perform the attack
        self.weapon = weapon  # weapon that use to perform the attack
        self.speed = speed  # travel speed
        self.arc_shot = False  # direct shot will no go pass collided unit
        if shooter.special_effect_check("Arc Shot", weapon=0) and self.shooter.unit.shoot_mode != 2:
            self.arc_shot = True  # arc shot will go pass unit to land at final base_target
        self.height = self.shooter.height
        self.accuracy = self.shooter.accuracy
        self.dmg = {key: random.uniform(value[0], value[1]) for key, value in dmg.items()}
        self.penetrate = penetrate
        if self.shooter.state in (12, 13) and True in self.shooter.special_effect["Agile Aim"] is False:
            self.accuracy -= 10  # accuracy penalty for shoot while moving
        self.pass_subunit = None  # check which subunit arrow passing through
        self.side = None  # side that arrow collided last
        if hit_cal:
            random_pos1 = random.randint(0, 1)  # for left or right random
            random_pos2 = random.randint(0, 1)  # for up or down random

            # v Calculate hit_chance and final base_target where arrow will land
            # The further hit_chance from 0 the further arrow will land from base_target
            hit_chance = self.accuracy * (100 - ((shoot_range * 100 / max_range) / 2)) / 100
            if hit_chance == 0:
                hit_chance = 1
            if True in self.shooter.special_effect["No Range Penalty"]:
                hit_chance = self.accuracy
            elif True in self.shooter.special_effect["Long Range Accurate"]:
                hit_chance = self.accuracy * (100 - ((shoot_range * 100 / max_range) / 4)) / 100  # range penalty half
            how_long = shoot_range / self.speed  # shooting distance divide arrow speed to find travel time
            target_now = self.shooter.attack_pos
            if self.shooter.attack_target is not None:
                if len(self.shooter.attack_target.alive_subunit_list) > 0:
                    target_hit = self.shooter.find_melee_target(self.shooter.attack_target.alive_subunit_list)
                    target_now = target_hit.base_pos  # base_target is at the enemy position

                    # Base_target walking, predicatively find position the enemy will be at based on movement speed and arrow travel time
                    if (target_hit.walk or target_hit.run) and how_long > 0.5:  # base_target walking
                        target_move = target_hit.base_target - self.shooter.attack_target.base_pos  # calculate base_target movement distance
                        if target_move.length() > 1:
                            target_move.normalize_ip()
                            move_speed = target_hit.unit.walk_speed
                            if target_hit.run:
                                move_speed = target_hit.unit.run_speed
                            target_now = target_hit.base_pos + (
                                    (target_move * (move_speed * how_long)) / 11)
                            if True in self.shooter.special_effect["Agile Aim"] is False:
                                hit_chance -= 15
                        else:  # movement too short, simply hit the current position
                            target_now = target_hit.base_pos

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

    def range_dmg_cal(self, attacker, target, target_side, side_percent=(1, 0.3, 0.3, 0)):
        """Calculate hit_chance and defence chance, side_percent is more punishing than melee melee_attack"""
        attacker_luck = random.randint(-40, 20)  # luck of the attacker subunit
        target_luck = random.randint(-20, 20)  # luck of the defender subunit

        target_percent = side_percent[target_side]  # side penalty
        if target.special_effect_check("All Side Full Defence"):
            target_percent = 1  # no side penalty for all round defend
        attacker_hit = float(self.accuracy) + attacker_luck  # calculate hit chance
        if attacker_hit < 0:
            attacker_hit = 0  # hit_chance cannot be negative

        target_def = float(target.range_def * target_percent) + target_luck  # calculate defence
        if target_def < 0:
            target_def = 0  # defence cannot be negative

        attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, element_effect = attacker.dmg_cal(target, attacker_hit, target_def, self.weapon, self)
        target.subunit_health -= attacker_dmg
        target.base_morale -= attacker_morale_dmg

        if target.red_border is False:  # add red corner to indicate melee_dmg
            target.block.blit(target.unit_ui_images["ui_squad_combat"], target.corner_image_rect)
            target.red_border = True

        for key, value in element_effect.items():
            target.element_status_check[key] += round(attacker_dmg * value * (100 - target.element_resistance[key] / 100))

        if target.leader is not None and target.leader.health > 0 and random.randint(0, 10) > 5:  # dmg on leader
            target.leader.health -= attacker_leader_dmg

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
                if self.arc_shot is False:  # direct shot will not be able to shoot pass higher height terrain midway
                    if self.height_map.get_height(self.base_pos) > self.target_height + 20:
                        self.kill()
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * view_mode
                self.rect.center = list(int(v) for v in self.pos)
            else:
                self.base_pos = self.base_target
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * view_mode
                self.rect.center = self.pos

            for element in self.dmg:
                if self.dmg[element] > 1:
                    self.dmg[element] -= 0.05  # dmg and penetration power drop the longer arrow travel
            if self.penetrate > 1:
                self.penetrate -= 0.002

            for subunit in pygame.sprite.spritecollide(self, unit_list, 0):
                if subunit != self.shooter:  # and subunit.base_pos.distance_to(self.base_pos) < subunit.image_height:
                    if self.arc_shot is False:  # direct shot
                        self.register_hit(subunit)
                        self.kill()
                    else:
                        self.pass_subunit = subunit
                    break

        else:  # reach base_target
            self.register_hit(self.pass_subunit)  # register hit whatever subunit the sprite land at
            self.kill()  # remove sprite
