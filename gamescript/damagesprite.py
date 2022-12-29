import os
import random

import pygame
import pygame.freetype
from pathlib import Path

from gamescript.common import utility


class DamageSprite(pygame.sprite.Sprite):
    empty_method = utility.empty_method

    bullet_sprite_pool = None
    bullet_weapon_sprite_pool = None
    effect_sprite_pool = None
    effect_animation_pool = None
    screen_scale = (1, 1)
    height_map = None

    set_rotate = utility.set_rotate

    # Import from common.subunit
    find_random_direction = empty_method
    hit_register = empty_method
    play_animation = empty_method
    range_dmg_cal = empty_method
    sprite_scaling = empty_method

    script_dir = os.path.split(os.path.abspath(__file__))[0]
    for entry in os.scandir(Path(script_dir + "/common/damagesprite/")):  # load and replace modules from common.unit
        if entry.is_file():
            if ".py" in entry.name:
                file_name = entry.name[:-3]
            elif ".pyc" in entry.name:
                file_name = entry.name[:-4]
            exec(f"from gamescript.common.damagesprite import " + file_name)
            exec(f"" + file_name + " = " + file_name + "." + file_name)

    def __init__(self, attacker, weapon, dmg, penetrate, weapon_stat, max_range, camera_zoom,
                 attack_type, specific_attack_pos=None, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False):
        self._layer = 50
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.attacker = attacker  # subunit that perform the attack
        self.battle = self.attacker.battle
        self.weapon = weapon  # weapon that use to perform the attack
        self.arc_shot = False  # arc shot will only hit subunit when it reaches target
        self.height = self.attacker.height
        self.accuracy = self.attacker.accuracy
        self.attack_type = attack_type

        self.height_ignore = height_ignore
        self.degrade_when_travel = degrade_when_travel
        self.degrade_when_hit = degrade_when_hit
        self.random_direction = random_direction
        self.random_move = random_move

        self.aoe = False  # TODO add condition
        self.deal_dmg = True

        self.scale_size = 1
        self.animation_timer = 0
        self.show_frame = 0
        self.current_animation = {}
        self.repeat_animation = False
        self.sprite_direction = ""
        self.attacker_sprite_direction = self.attacker.sprite_direction

        self.dmg = {key: random.uniform(value[0], value[1]) for key, value in dmg.items()}
        self.penetrate = penetrate

        self.pass_subunit = None  # subunit that damage sprite passing through, receive damage if movement stop

        self.camera_zoom = camera_zoom

        if self.attack_type == "range":
            self.base_pos = pygame.Vector2(self.attacker.base_pos)

            self.speed = weapon_stat["Travel Speed"]  # bullet travel speed
            if weapon_stat["Damage Sprite"] != "self":
                self.image = self.bullet_sprite_pool[weapon_stat["Damage Sprite"]]["side"][
                    "base"]  # use side and base sprite by default for now
            else:  # use weapon image itself as bullet image
                direction = self.attacker_sprite_direction
                if "r_" in direction or "l_" in direction:
                    direction = self.attacker_sprite_direction[2:]
                image_name = "base_main"
                if weapon == 1:
                    image_name = "base_sub"
                self.image = self.bullet_weapon_sprite_pool[weapon_stat["Name"]][
                    attacker.weapon_version[attacker.equipped_weapon][weapon]][direction][image_name]
            if attacker.check_special_effect("Arc Shot", weapon=0) and self.attacker.unit.shoot_mode != 2:
                self.arc_shot = True  # arc shot will go pass unit to land at final base_target
            if (self.attacker.walk or self.attacker.run) and True in self.attacker.special_effect["Agile Aim"] is False:
                self.accuracy -= 10  # accuracy penalty for shoot while moving

            random_pos1 = random.randint(0, 1)  # for left or right random
            random_pos2 = random.randint(0, 1)  # for up or down random

            # Calculate hit_chance and final base_target where damage sprite will land
            # The further hit_chance from 0 the further damage sprite will land from base_target
            sight_penalty = 1

            if specific_attack_pos is not None:
                target_now = specific_attack_pos
            elif self.random_direction:
                target_now = self.find_random_direction()
            else:
                target_now = self.attacker.attack_target.base_pos
            attack_range = self.attacker.base_pos.distance_to(target_now)
            if True in self.attacker.special_effect["No Range Penalty"]:
                hit_chance = self.accuracy
            elif True in self.attacker.special_effect["Long Range Accurate"]:
                hit_chance = self.accuracy * (
                        100 - ((attack_range * 100 / max_range) / 4)) / 100  # range penalty half
            else:
                if attack_range > self.attacker.sight:  # penalty for range attack if shoot beyond troop can see
                    sight_penalty = self.attacker.sight / attack_range
                hit_chance = self.accuracy * sight_penalty * (100 - ((attack_range * 100 / max_range) / 2)) / 100

            if specific_attack_pos is None and self.attacker.attack_target is not None:
                if len(self.attacker.attack_target.alive_subunit_list) > 0:
                    target_hit = self.attacker.find_melee_target(
                        self.attacker.attack_target.alive_subunit_list)  # find the closest subunit in enemy unit
                    target_now = target_hit.base_pos  # base_target is at the enemy position
                    how_long = attack_range / self.speed  # shooting distance divide damage sprite speed to find travel time

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

            if hit_chance < 100:
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
            if self.arc_shot is False:  # direct shot move base_target furthest
                self.base_target += ((self.base_target - self.base_pos).length() * 1000)

            # Rotate damage sprite sprite
            self.angle = self.set_rotate(self.base_target)

        else:
            self.sprite_direction = self.attack_type[1]
            self.angle = self.attack_type[5]
            self.scale_size = self.attack_type[8]

            animation_name = "".join(self.attack_type[2].split("_"))[-1]
            if animation_name.isdigit():
                animation_name = "".join([string + "_" for string in self.attack_type[2].split("_")[:-1]])[:-1]
            else:
                animation_name = self.attack_type[2]

            self.current_animation = self.effect_animation_pool[weapon_stat["Damage Sprite"]][
                self.sprite_direction][animation_name]

            self.image = self.current_animation[self.show_frame]

            self.base_pos = pygame.Vector2(self.attacker.front_pos)  # TODO change to cal distance?
            self.base_target = self.base_pos

        self.target_height = self.height_map.get_height(self.base_target)  # get the height at base_target

        self.adjust_sprite()

        self.camera_scale = (11 - self.camera_zoom) / 4

        self.sprite_scaling()

    def adjust_sprite(self):
        if "l_" in self.attacker_sprite_direction:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.scale_size > 1:
            self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.scale_size,
                                                                   self.image.get_height() * self.scale_size))
        self.image_original = self.image.copy()

    def update(self, unit_list, dt, camera_scale):
        just_start = False

        if self.deal_dmg:  # sprite can still deal damage
            self.pass_subunit = None  # reset every movement update
            for subunit in pygame.sprite.spritecollide(self, unit_list, 0):  # collide check while travel
                if subunit != self.attacker and subunit.dmg_rect.colliderect(self.rect):
                    if self.attack_type == "range":
                        if self.arc_shot is False:  # direct shot
                            self.hit_register(subunit)
                            if self.aoe is False and self.penetrate <= 0:
                                self.kill()
                                break
                        else:
                            self.pass_subunit = subunit

                    elif self.attack_type == "melee" and subunit.team != self.attacker.team:  # no friendly attack for melee
                        self.hit_register(subunit)
                        if self.aoe is False:
                            self.deal_dmg = False
                            break

        move = self.base_target - self.base_pos
        move_length = move.length()
        if move_length > 0:  # sprite move
            move.normalize_ip()
            move = move * self.speed * dt
            if move.length() <= move_length:
                self.base_pos += move
                if self.arc_shot is False and self.height_ignore is False and \
                        self.height_map.get_height(self.base_pos) > self.height + 20:
                    self.kill()  # direct shot will not be able to shoot pass higher height terrain midway
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                          self.base_pos[1] * self.screen_scale[1]) * camera_scale
                self.rect.center = list(int(v) for v in self.pos)

                if self.random_move is False and (
                        self.base_pos[0] <= 0 or self.base_pos[0] >= self.battle.map_corner[0] or
                        self.base_pos[1] <= 0 or self.base_pos[1] >= self.battle.map_corner[1]):  # pass outside of map
                    self.kill()

                if self.degrade_when_travel:
                    for element in self.dmg:
                        if self.dmg[element] > 1:
                            self.dmg[element] -= 0.05  # dmg and penetration power drop the longer damage sprite travel
                    if self.penetrate > 1:
                        self.penetrate -= 0.002
                    else:  # no more penetrate power to move on
                        self.kill()  # remove sprite
            else:
                self.base_pos = self.base_target
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                          self.base_pos[1] * self.screen_scale[1]) * camera_scale
                self.rect.center = self.pos

        elif self.arc_shot:  # reach base_target with arc shot
            if self.deal_dmg:
                self.hit_register(self.pass_subunit)  # register hit whatever subunit the sprite land at
            self.kill()  # remove sprite

        if len(self.current_animation) > 0:
            done, just_start = self.play_animation(0.1, dt, False)
            if just_start:
                self.adjust_sprite()
            if done:
                self.kill()

        if self.camera_zoom != camera_scale:
            self.camera_zoom = camera_scale
            self.camera_scale = (11 - self.camera_zoom) / 4
            self.sprite_scaling()
        elif just_start:
            self.sprite_scaling()
