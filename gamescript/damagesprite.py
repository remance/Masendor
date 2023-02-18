import math
import os
import random
from pathlib import Path

import pygame
import pygame.freetype
from gamescript.common import utility

direction_angle = {"r_side": math.radians(90), "l_side": math.radians(270), "back": math.radians(180),
                   "front": math.radians(0), "r_sidedown": math.radians(135), "l_sidedown": math.radians(225),
                   "r_sideup": math.radians(45), "l_sideup": math.radians(315)}


class DamageSprite(pygame.sprite.Sprite):
    empty_method = utility.empty_method
    clean_object = utility.clean_object

    bullet_sprite_pool = None
    bullet_weapon_sprite_pool = None
    effect_sprite_pool = None
    effect_animation_pool = None
    screen_scale = (1, 1)
    sound_effect_pool = None
    height_map = None

    set_rotate = utility.set_rotate

    # Import from common.damagesprite
    cal_melee_hit = empty_method
    cal_range_hit = empty_method
    find_random_direction = empty_method
    hit_register = empty_method
    play_animation = empty_method

    script_dir = os.path.split(os.path.abspath(__file__))[0]
    for entry in os.scandir(Path(script_dir + "/common/damagesprite/")):  # load and replace modules from common.unit
        if entry.is_file():
            if ".py" in entry.name:
                file_name = entry.name[:-3]
            elif ".pyc" in entry.name:
                file_name = entry.name[:-4]
            exec(f"from gamescript.common.damagesprite import " + file_name)
            exec(f"" + file_name + " = " + file_name + "." + file_name)

    def __init__(self, attacker, weapon, dmg, penetrate, weapon_stat,
                 attack_type, base_target, accuracy=None, arc_shot=False, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False,  mpact_effect=None):
        self._layer = 10000001
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.attacker = attacker  # subunit that perform the attack
        self.battle = self.attacker.battle
        self.weapon = weapon  # weapon that use to perform the attack
        self.accuracy = accuracy
        self.height = self.attacker.height
        self.attack_type = attack_type
        self.impact_effect = None
        self.arc_shot = arc_shot

        self.height_ignore = height_ignore
        self.degrade_when_travel = degrade_when_travel
        self.degrade_when_hit = degrade_when_hit
        self.random_direction = random_direction
        self.random_move = random_move

        self.aoe = False  # TODO add condition
        self.deal_dmg = True

        self.scale_size = 1
        self.animation_timer = 0
        self.duration = 0
        self.timer = 0
        self.show_frame = 0
        self.current_animation = {}
        self.repeat_animation = False
        self.sprite_direction = ""
        self.attacker_sprite_direction = self.attacker.sprite_direction
        self.already_hit = []  # list of subunit already got hit by sprite for sprite with no duration

        self.dmg = {key: random.uniform(value[0], value[1]) for key, value in dmg.items()}
        self.penetrate = penetrate
        self.impact = weapon_stat["Impact"]

        self.pass_subunit = None  # subunit that damage sprite passing through, receive damage if movement stop

        self.base_target = base_target

        if self.attack_type == "charge":  # charge attack use subunit hitbox as damage sprite with no its own image
            self.base_pos = self.attacker.base_pos  # always move along with attacker
            self.angle = self.attacker.angle
            self.rect = self.attacker.hitbox.rect

            self.battle.battle_camera.remove(self)

        else:
            if self.attack_type == "range":
                self.repeat_animation = True
                self.base_pos = pygame.Vector2(self.attacker.front_pos)
                self.angle = self.set_rotate(self.base_target)

                self.speed = weapon_stat["Travel Speed"]  # bullet travel speed

                if weapon_stat["Damage Sprite"] != "self":
                    self.image = self.bullet_sprite_pool[weapon_stat["Damage Sprite"]]["base"]
                else:  # use weapon image itself as bullet image
                    image_name = "base_main"
                    if weapon == 1:
                        image_name = "base_sub"
                    self.image = self.bullet_weapon_sprite_pool[weapon_stat["Name"]][
                        attacker.weapon_version[attacker.equipped_weapon][weapon]][image_name]

            elif isinstance(self.attack_type, (list, tuple, dict)):
                self.sprite_direction = self.attacker.sprite_direction
                self.scale_size = self.attack_type[7]

                animation_name = "".join(self.attack_type[1].split("_"))[-1]
                if animation_name.isdigit():
                    animation_name = "".join([string + "_" for string in self.attack_type[1].split("_")[:-1]])[:-1]
                else:
                    animation_name = self.attack_type[1]

                self.current_animation = self.effect_animation_pool[weapon_stat["Damage Sprite"]][self.attacker.team][animation_name]

                self.image = self.current_animation[self.show_frame]

                self.base_pos = self.attacker.base_pos
                self.angle = self.set_rotate(self.base_target)
                self.base_pos = base_target

            self.adjust_sprite()

            self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                      self.base_pos[1] * self.screen_scale[1]) * 5
            self.rect = self.image.get_rect(center=self.pos)

        if self.duration:
            self.repeat_animation = True

        self.full_distance = self.base_pos.distance_to(self.base_target)
        self.distance_progress = 0
        self.last_distance_progress = 0

    def adjust_sprite(self):
        if self.scale_size > 1:
            self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.scale_size,
                                                                   self.image.get_height() * self.scale_size))

        self.image = pygame.transform.rotate(self.image, self.angle)

        # if self.attack_type != "range" and "l_" in self.attacker_sprite_direction:
        #     self.image = pygame.transform.flip(self.image, True, False)

        self.base_image = self.image.copy()

    def update(self, subunit_list, dt):
        done = False
        just_start = False
        pass_subunit = None

        self.timer += dt
        if self.timer > 1:  # reset timer and list of subunit already hit
            self.timer -= 1
            if self.duration or self.attack_type == "charge":  # only clear for sprite with duration or charge
                self.already_hit = []  # sprite can deal dmg to same subunit only once every 1 second

        if self.current_animation:  # play animation if any
            done, just_start = self.play_animation(0.05, dt, False)
            if just_start:
                self.adjust_sprite()

        # Check for collision with subunit and deal damage
        if self.deal_dmg:  # sprite can still deal damage
            for this_subunit in subunit_list:  # collide check
                if this_subunit.team != self.attacker.team and this_subunit.game_id not in self.already_hit and \
                        this_subunit.hitbox.rect.colliderect(self.rect):
                    if self.full_distance:  # range attack
                        if self.arc_shot:  # arc shot does not hit during travel
                            pass_subunit = this_subunit
                        else:
                            self.hit_register(this_subunit)
                            self.already_hit.append(this_subunit.game_id)
                            if self.penetrate <= 0:
                                self.deal_dmg = False
                                self.clean_object()
                                return
                    else:
                        self.hit_register(this_subunit)
                        self.already_hit.append(this_subunit.game_id)
                        if self.penetrate <= 0:
                            self.deal_dmg = False
                            break

        if self.distance_progress >= 100:  # attack reach target pos
            if self.arc_shot and pass_subunit is not None:  # arc shot hit last pass when land
                self.hit_register(pass_subunit)
            self.clean_object()  # remove sprite
            return

        if self.full_distance:  # damage sprite that can move like range attack or spell
            self.pass_subunit = None  # reset before every movement update and after collide check
            move = self.base_target - self.base_pos
            require_move_length = move.length()

            if require_move_length:  # sprite move
                move.normalize_ip()
                move = move * self.speed * dt
                self.distance_progress += move.length() / self.full_distance * 100

                if move.length() <= require_move_length:
                    self.base_pos += move
                    if self.arc_shot is False and self.height_ignore is False and \
                            self.height_map.get_height(self.base_pos) > self.height + 20:
                        self.clean_object()  # direct shot will not be able to shoot pass higher height terrain midway
                        return
                    self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                              self.base_pos[1] * self.screen_scale[1]) * 5
                    self.rect.center = self.pos

                    if self.random_move is False and (
                            self.base_pos[0] <= 0 or self.base_pos[0] >= self.battle.map_corner[0] or
                            self.base_pos[1] <= 0 or self.base_pos[1] >= self.battle.map_corner[1]):  # pass outside of map
                        self.clean_object()
                        return

                    if self.degrade_when_travel:  # dmg and penetration power drop the longer damage sprite travel
                        for element in self.dmg:
                            if self.dmg[element] > 1:
                                self.dmg[element] -= 0.1
                        if self.penetrate > 1:
                            self.penetrate -= 0.1
                        else:  # no more penetrate power to move on
                            self.clean_object()  # remove sprite
                            return
                else:  # reach target
                    self.base_pos = self.base_target
                    self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                              self.base_pos[1] * self.screen_scale[1]) * 5
                    self.rect.center = self.pos

        else:  # attack that does not travel
            if self.attack_type == "charge":
                if self.attacker.charging is False:
                    self.clean_object()
                    return
            elif done and self.duration == 0:
                self.clean_object()
                return

        if just_start:
            self.rect = self.image.get_rect(center=self.pos)
