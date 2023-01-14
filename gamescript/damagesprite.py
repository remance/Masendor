import os
import random
import math

import pygame
import pygame.freetype
from pathlib import Path

from gamescript.common import utility

direction_angle = {"r_side": math.radians(90), "l_side": math.radians(270), "back": math.radians(180),
                   "front": math.radians(0), "r_sidedown": math.radians(135), "l_sidedown": math.radians(225),
                   "r_sideup": math.radians(45), "l_sideup": math.radians(315)}


class DamageSprite(pygame.sprite.Sprite):
    empty_method = utility.empty_method

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

    def __init__(self, attacker, weapon, dmg, penetrate, weapon_stat, camera_zoom,
                 attack_type, base_target, accuracy=None, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, arc_shot=False):
        self._layer = 50
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.attacker = attacker  # subunit that perform the attack
        self.battle = self.attacker.battle
        self.weapon = weapon  # weapon that use to perform the attack
        self.arc_shot = arc_shot  # arc shot will only hit subunit when it reaches target
        self.accuracy = accuracy
        self.height = self.attacker.height
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
            self.base_pos = pygame.Vector2(self.attacker.front_pos)

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

            self.base_target = base_target

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

            self.base_pos = pygame.Vector2(self.attacker.front_pos[0] + (weapon_stat["Range"] * math.sin(direction_angle[self.attacker_sprite_direction])),
                                           self.attacker.front_pos[1] - (weapon_stat["Range"] * math.cos(direction_angle[self.attacker_sprite_direction])))

            self.base_target = self.base_pos

        self.target_height = self.height_map.get_height(self.base_target)  # get the height at base_target

        self.adjust_sprite()

        self.camera_scale = (11 - self.camera_zoom) / 4

        self.sprite_scaling()

        hitbox_image = pygame.transform.scale(self.base_image,
                                              (min(1, int(self.base_image.get_width() / self.battle.max_camera_zoom)),
                                               min(1, int(self.base_image.get_height() / self.battle.max_camera_zoom))))

        self.hitbox_rect = hitbox_image.get_rect(center=self.base_pos)  # hitbox rect based on base pos

    def adjust_sprite(self):
        if self.scale_size > 1:
            self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.scale_size,
                                                                   self.image.get_height() * self.scale_size))

        self.image = pygame.transform.rotate(self.image, self.angle)

        if self.attack_type != "range" and "l_" in self.attacker_sprite_direction:
            self.image = pygame.transform.flip(self.image, True, False)

        self.base_image = self.image.copy()

    def update(self, unit_list, dt, camera_zoom):
        just_start = False

        self.pass_subunit = None  # reset every movement update

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
                self.hitbox_rect.center = self.base_pos
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                          self.base_pos[1] * self.screen_scale[1]) * camera_zoom
                self.rect.center = list(int(v) for v in self.pos)

                if self.random_move is False and (
                        self.base_pos[0] <= 0 or self.base_pos[0] >= self.battle.map_corner[0] or
                        self.base_pos[1] <= 0 or self.base_pos[1] >= self.battle.map_corner[1]):  # pass outside of map
                    self.kill()

                if self.degrade_when_travel:  # dmg and penetration power drop the longer damage sprite travel
                    for element in self.dmg:
                        if self.dmg[element] > 1:
                            self.dmg[element] -= 0.1
                    if self.penetrate > 1:
                        self.penetrate -= 0.2
                    else:  # no more penetrate power to move on
                        self.kill()  # remove sprite
            else:
                self.base_pos = self.base_target
                self.hitbox_rect.center = self.base_pos
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                          self.base_pos[1] * self.screen_scale[1]) * camera_zoom
                self.rect.center = self.pos

        if self.deal_dmg:  # sprite can still deal damage
            for subunit in pygame.sprite.spritecollide(self, unit_list, False):  # collide check while travel
                if subunit != self.attacker and subunit.hitbox_rect.colliderect(self.hitbox_rect):
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

                    if self.arc_shot is False:
                        print(subunit.base_pos, subunit.game_id, subunit.name, subunit.base_pos,
                              subunit.hitbox_rect, self.hitbox_rect, self.base_pos, self.penetrate)

        if move_length <= 0:
            if self.deal_dmg and self.arc_shot:  # arc shot hit enemy it pass last
                self.hit_register(self.pass_subunit)  # register hit whatever subunit the sprite land at
            self.kill()  # remove sprite

        if len(self.current_animation) > 0:
            done, just_start = self.play_animation(0.1, dt, False)
            if just_start:
                self.adjust_sprite()
            if done:
                self.kill()

        if self.camera_zoom != camera_zoom:
            self.camera_zoom = camera_zoom
            self.camera_scale = (11 - self.camera_zoom) / 4
            self.sprite_scaling()
        elif just_start:
            self.sprite_scaling()
