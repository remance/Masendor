import math
import random

import pygame
import pygame.freetype
from gamescript.common import animation
from pygame.transform import scale


class DamageSprite(pygame.sprite.Sprite):
    bullet_sprite_pool = None
    bullet_weapon_sprite_pool = None
    screen_scale = (1, 1)
    height_map = None

    play_animation = animation.play_animation

    def __init__(self, attacker, weapon, dmg, penetrate, weapon_stat, attack_range, max_range, view_mode,
                 attack_type):
        self._layer = 50
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.attacker = attacker  # subunit that perform the attack
        self.weapon = weapon  # weapon that use to perform the attack
        self.arc_shot = False  # direct shot will no go pass collided unit
        self.height = self.attacker.height
        self.accuracy = self.attacker.accuracy
        self.attack_type = attack_type

        self.aoe = False  # TODO add condition

        self.current_frame = 0

        self.dmg = {key: random.uniform(value[0], value[1]) for key, value in dmg.items()}
        self.penetrate = penetrate

        self.pass_subunit = None  # subunit that damage sprite passing through, receive damage if movement stop

        if self.attack_type == "range":
            self.speed = weapon_stat["Travel Speed"]  # bullet travel speed
            if weapon_stat["Bullet"][0] != "self":
                self.image = self.bullet_sprite_pool[weapon_stat["Bullet"][0]]["side"]["base"]  # use side and base sprite by default for now
            else:  # use weapon image itself as bullet image
                direction = attacker.sprite_direction
                if "r_" in direction or "l_" in direction:
                    direction = attacker.sprite_direction[2:]
                self.image = self.bullet_weapon_sprite_pool[weapon_stat["Name"]][attacker.weapon_version[attacker.equipped_weapon][weapon]][direction]["base"]
            if attacker.special_effect_check("Arc Shot", weapon=0) and self.attacker.unit.shoot_mode != 2:
                self.arc_shot = True  # arc shot will go pass unit to land at final base_target
            if (self.attacker.walk or self.attacker.run) and True in self.attacker.special_effect["Agile Aim"] is False:
                self.accuracy -= 10  # accuracy penalty for shoot while moving

            random_pos1 = random.randint(0, 1)  # for left or right random
            random_pos2 = random.randint(0, 1)  # for up or down random

            # Calculate hit_chance and final base_target where damage sprite will land
            # The further hit_chance from 0 the further damage sprite will land from base_target
            sight_penalty = 1
            if attack_range > self.attacker.sight:  # penalty for range attack if shoot beyond troop can see
                sight_penalty = self.attacker.sight / attack_range
            hit_chance = self.accuracy * sight_penalty * (100 - ((attack_range * 100 / max_range) / 2)) / 100
            if hit_chance == 0:
                hit_chance = 1
            if True in self.attacker.special_effect["No Range Penalty"]:
                hit_chance = self.accuracy
            elif True in self.attacker.special_effect["Long Range Accurate"]:
                hit_chance = self.accuracy * (
                            100 - ((attack_range * 100 / max_range) / 4)) / 100  # range penalty half
            how_long = attack_range / self.speed  # shooting distance divide damage sprite speed to find travel time
            target_now = self.attacker.attack_pos
            if self.attacker.attack_target is not None:
                if len(self.attacker.attack_target.alive_subunit_list) > 0:
                    target_hit = self.attacker.find_melee_target(self.attacker.attack_target.alive_subunit_list)
                    target_now = target_hit.base_pos  # base_target is at the enemy position

                    # Predicatively find position the enemy will be at based on movement speed and sprite travel time
                    if (target_hit.walk or target_hit.run) and how_long > 0.5:  # target walking
                        target_move = target_hit.base_target - self.attacker.attack_target.base_pos  # target movement distance
                        target_now = target_hit.base_pos
                        if target_move.length() > 1:
                            target_move.normalize_ip()
                            move_speed = target_hit.unit.walk_speed
                            if target_hit.run:
                                move_speed = target_hit.unit.run_speed
                            target_now = target_hit.base_pos + (
                                    (target_move * (move_speed * how_long)) / 11)
                            if True in self.attacker.special_effect["Agile Aim"] is False:
                                hit_chance -= 15

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
                self.base_target = pygame.Vector2(target_now[0] * hit_chance1 / 100,
                                                  target_now[1] * hit_chance2 / 100)
            else:  # perfect hit, slightly (randomly) land near base_target
                self.base_target = target_now * random.uniform(0.999, 1.001)

        elif self.attack_type == "melee":  # TODO change later
            self.base_target = self.attacker.base_pos

        self.target_height = self.height_map.get_height(self.base_target)  # get the height at base_target

        # Rotate damage sprite sprite
        radians = math.atan2(self.base_target[1] - self.attacker.unit.base_pos[1],
                             self.base_target[0] - self.attacker.unit.base_pos[0])
        self.angle = math.degrees(radians)

        if -180 <= self.angle < 0:  # upper left and upper right
            self.angle = -self.angle - 90
        elif 0 <= self.angle <= 90:  # lower right -"
            self.angle = -(self.angle + 90)
        elif 90 < self.angle <= 180:  # lower left +
            self.angle = 270 - self.angle

        self.image = pygame.transform.rotate(self.image, self.angle)

        self.base_pos = pygame.Vector2(self.attacker.base_pos[0], self.attacker.base_pos[1])
        self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * view_mode
        self.rect = self.image.get_rect(midbottom=self.pos)

    def range_dmg_cal(self, attacker, target, target_side, side_percent=(1, 0.3, 0.3, 0)):
        """Calculate range attack hit chance and defence chance, side_percent is more punishing than melee attack"""
        attacker_luck = random.randint(-20, 20)  # luck of the attacker subunit
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
        self.attacker.loss_cal(target, attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, element_effect)

    def hit_register(self, subunit=None):
        """Calculate hit and damage"""
        if subunit is not None:
            angle_check = abs(self.angle - subunit.angle)  # calculate which side damage sprite hit the subunit
            if angle_check >= 135:  # front
                hit_side = 0
            elif angle_check >= 45:  # side
                hit_side = 1
            else:  # rear
                hit_side = 2
            # calculate damage
            if self.attack_type == "range":
                self.range_dmg_cal(self.attacker, subunit, hit_side)
            elif self.attack_type == "melee":  # use attacker hit register instead
                self.attacker.hit_register(self.weapon, subunit, 0, hit_side, self.attacker.battle.troop_data.status_list)

    def update(self, unit_list, dt, view_mode):
        move = self.base_target - self.base_pos
        move_length = move.length()

        self.pass_subunit = None  # reset every movement update
        for subunit in pygame.sprite.spritecollide(self, unit_list, 0):
            if subunit != self.attacker and subunit.dmg_rect.colliderect(self.rect):
                if self.attack_type == "range":
                    if self.arc_shot is False:  # direct shot
                        self.hit_register(subunit)
                        self.kill()
                    else:
                        self.pass_subunit = subunit
                    break
                elif self.attack_type == "melee" and subunit.team != self.attacker.team:  # no friendly attack for melee
                    self.hit_register(subunit)
                    self.kill()
                    if self.aoe is False:
                        break

        if move_length > 0:  # sprite move
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
                    self.dmg[element] -= 0.05  # dmg and penetration power drop the longer damage sprite travel
            if self.penetrate > 1:
                self.penetrate -= 0.002

        else:  # reach base_target
            self.hit_register(self.pass_subunit)  # register hit whatever subunit the sprite land at
            self.kill()  # remove sprite
