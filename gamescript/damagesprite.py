import os
from math import cos, sin, radians
from pathlib import Path
from random import choice, uniform

import pygame
import pygame.freetype

from gamescript.common import utility

direction_angle = {"r_side": radians(90), "l_side": radians(270), "back": radians(180),
                   "front": radians(0), "r_sidedown": radians(135), "l_sidedown": radians(225),
                   "r_sideup": radians(45), "l_sideup": radians(315)}


class DamageSprite(pygame.sprite.Sprite):
    empty_method = utility.empty_method
    clean_object = utility.clean_object

    bullet_sprite_pool = None
    bullet_weapon_sprite_pool = None
    effect_sprite_pool = None
    effect_animation_pool = None
    effect_list = None
    screen_scale = (1, 1)
    sound_effect_pool = None
    height_map = None
    battle = None

    set_rotate = utility.set_rotate

    # Import from common.damagesprite
    adjust_sprite = empty_method
    cal_dmg = empty_method
    cal_effect_hit = empty_method
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

    def __init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 accuracy=None, arc_shot=False, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, reach_effect=None, height_type=1):
        """Damage or effect sprite that can affect subunit"""
        self._layer = 10000000 + height_type
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.attacker = attacker  # subunit that perform the attack
        self.weapon = weapon  # weapon that use to perform the attack
        self.accuracy = accuracy
        self.height = self.attacker.height
        self.attack_type = attack_type
        self.impact_effect = None
        self.arc_shot = arc_shot
        self.reach_effect = reach_effect

        self.height_ignore = height_ignore
        self.degrade_when_travel = degrade_when_travel
        self.degrade_when_hit = degrade_when_hit
        self.random_direction = random_direction
        self.random_move = random_move

        self.stat = stat

        self.aoe = 0
        if "Area Of Effect" in self.stat:
            self.aoe = self.stat["Area Of Effect"]

        self.scale_size = 1
        self.frame_timer = 0
        self.duration = 0
        self.timer = 0
        self.show_frame = 0
        self.current_animation = {}
        self.sound_effect_name = None
        self.sound_timer = 0
        self.sound_duration = 0
        self.stamina_dmg_bonus = 0
        self.repeat_animation = False
        self.sprite_direction = ""
        self.attacker_sprite_direction = self.attacker.sprite_direction
        self.already_hit = []  # list of subunit already got hit by sprite for sprite with no duration

        self.dmg = dmg
        self.deal_dmg = False
        if self.dmg:  # has damage to deal
            self.deal_dmg = True

        self.penetrate = penetrate
        self.knock_power = impact

        self.base_pos = base_pos
        self.base_target = base_target

        if self.duration:
            self.repeat_animation = True

        self.full_distance = self.base_pos.distance_to(self.base_target)
        self.distance_progress = 0
        self.last_distance_progress = 0

    def reach_target(self):
        self.deal_dmg = False
        if self.reach_effect:
            effect_stat = self.effect_list[self.reach_effect]
            dmg = {key.split(" ")[0]: value for key, value in effect_stat.items() if " Damage" in key}
            if sum(dmg.values()) <= 0:
                dmg = None
            else:
                dmg = {key.split(" ")[0]: uniform(value / 2, value) for key, value in dmg.items()}
            EffectDamageSprite(self, self.reach_effect, dmg, effect_stat["Armour Penetration"], effect_stat["Impact"],
                               effect_stat, "effect", self.base_pos, self.base_pos,
                               reach_effect=effect_stat["After Reach Effect"])

        if "End Effect" in self.stat:
            finish_effect = self.stat["End Effect"]
            if finish_effect:
                effect_stat = self.effect_list[finish_effect]
                dmg = {key.split(" ")[0]: value for key, value in effect_stat.items() if " Damage" in key}
                if sum(dmg.values()) <= 0:
                    dmg = None
                else:
                    dmg = {key.split(" ")[0]: uniform(value / 2, value) for key, value in dmg.items()}
                EffectDamageSprite(self, self.stat["End Effect"], dmg, effect_stat["Armour Penetration"],
                                   effect_stat["Impact"], effect_stat, "effect", self.base_pos, self.base_pos,
                                   reach_effect=effect_stat["After Reach Effect"])
        self.clean_object()


class MeleeDamageSprite(DamageSprite):
    def __init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 accuracy=None, reach_effect=None):
        """Melee damage sprite"""
        DamageSprite.__init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                              accuracy=accuracy, reach_effect=reach_effect)
        self.sprite_direction = self.attacker.sprite_direction

        animation_name = "".join(self.attack_type[1].split("_"))[-1]
        if animation_name.isdigit():
            animation_name = "".join([string + "_" for string in self.attack_type[1].split("_")[:-1]])[:-1]
        else:
            animation_name = self.attack_type[1]

        self.current_animation = self.effect_animation_pool[stat["Damage Sprite"]][self.attacker.team][animation_name]

        self.image = self.current_animation[self.show_frame]

        self.base_pos = base_pos  # for setting angle first
        self.angle = self.set_rotate(self.base_target)
        self.base_pos = base_target

        self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                  self.base_pos[1] * self.screen_scale[1]) * 5
        self.adjust_sprite()

    def update(self, subunit_list, dt):
        done = False

        if self.current_animation:  # play animation if any
            done, just_start = self.play_animation(0.05, dt, False)

        for subunit in self.attacker.near_enemy:  # collide check
            this_subunit = subunit[0]
            if this_subunit.alive and this_subunit.game_id not in self.already_hit and \
                    this_subunit.hitbox.rect.colliderect(self.rect):
                self.hit_register(this_subunit)
                self.already_hit.append(this_subunit.game_id)
            if self.penetrate <= 0:
                break  # use break for melee to last until animation done

        if done:
            self.reach_target()
            return


class RangeDamageSprite(DamageSprite):
    def __init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 accuracy=None, arc_shot=False, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, reach_effect=None):
        """Range damage sprite"""
        DamageSprite.__init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                              arc_shot=arc_shot, height_ignore=height_ignore, degrade_when_travel=degrade_when_travel,
                              degrade_when_hit=degrade_when_hit, random_direction=random_direction,
                              random_move=random_move, accuracy=accuracy, reach_effect=reach_effect)
        self.repeat_animation = True
        self.base_pos = pygame.Vector2(base_pos)
        self.angle = self.set_rotate(self.base_target)

        self.speed = stat["Travel Speed"]  # bullet travel speed

        if stat["Damage Sprite"] != "self":
            sprite_name = stat["Damage Sprite"]
            self.image = self.bullet_sprite_pool[sprite_name]["base"]
        else:  # use weapon image itself as bullet image
            sprite_name = stat["Name"]
            if attacker.weapon_version[attacker.equipped_weapon][weapon] in self.bullet_weapon_sprite_pool[sprite_name]:
                self.image = self.bullet_weapon_sprite_pool[sprite_name][
                    attacker.weapon_version[attacker.equipped_weapon][weapon]]["base_main"]
            else:
                self.image = self.bullet_weapon_sprite_pool[sprite_name]["common"]["base_main"]

        if sprite_name in self.sound_effect_pool:
            self.travel_sound_distance = stat["Bullet Sound Distance"]
            self.travel_shake_power = stat["Bullet Shake Power"]
            self.sound_effect_name = choice(self.sound_effect_pool[sprite_name])
            self.sound_duration = pygame.mixer.Sound(self.sound_effect_name).get_length() * 1000 / self.speed
            self.sound_timer = self.sound_duration / 1.5  # wait a bit before start playing
            self.travel_sound_distance_check = self.travel_sound_distance * 2
            if self.sound_duration > 2:
                self.sound_timer = self.sound_duration / 0.5

        self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                  self.base_pos[1] * self.screen_scale[1]) * 5
        self.adjust_sprite()

    def update(self, subunit_list, dt):
        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.duration > 0:
            self.timer += dt
            self.duration -= dt
            if self.timer > 1:  # reset timer and list of subunit already hit for attack with duration
                self.timer -= 1
                self.already_hit = []  # sprite can deal dmg to same subunit only once every 1 second

        if self.current_animation:  # play animation if any
            self.play_animation(0.05, dt, False)

        for subunit in self.attacker.near_enemy:  # collide check
            this_subunit = subunit[0]
            if this_subunit.alive and this_subunit.game_id not in self.already_hit and this_subunit.hitbox.rect.colliderect(
                    self.rect):
                if self.arc_shot:
                    if self.distance_progress >= 100:  # arc shot only hit when reach target
                        self.hit_register(this_subunit)
                        if self.penetrate <= 0:
                            self.reach_target()
                            return
                else:
                    self.hit_register(this_subunit)
                    self.already_hit.append(this_subunit.game_id)
                    if self.penetrate <= 0:
                        self.reach_target()
                        return

        if self.distance_progress >= 100:  # attack reach target pos
            self.reach_target()
            return

        move = self.base_target - self.base_pos
        require_move_length = move.length()

        if require_move_length:  # sprite move
            move.normalize_ip()
            move = move * self.speed * dt
            self.distance_progress += move.length() / self.full_distance * 100

            if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                    self.travel_sound_distance_check > self.battle.true_camera_pos.distance_to(self.base_pos):
                # play sound, check for distance here to avoid timer reset when not on screen
                self.battle.add_sound_effect_queue(self.sound_effect_name, self.base_pos,
                                                   self.travel_sound_distance,
                                                   self.travel_shake_power)
                self.sound_timer = 0

            if move.length() <= require_move_length:
                self.base_pos += move
                if not self.arc_shot and not self.height_ignore and \
                        self.height_map.get_height(self.base_pos) > self.height + 20:
                    self.reach_target()  # direct shot will not be able to shoot pass higher height terrain midway
                    return

                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                          self.base_pos[1] * self.screen_scale[1]) * 5
                self.rect.center = self.pos

                if not self.random_move and (
                        self.base_pos[0] <= 0 or self.base_pos[0] >= self.battle.map_corner[0] or
                        self.base_pos[1] <= 0 or self.base_pos[1] >= self.battle.map_corner[
                            1]):  # pass outside of map
                    self.reach_target()
                    return

                if self.degrade_when_travel:  # dmg and penetration power drop the longer damage sprite travel
                    for element in self.dmg:
                        if self.dmg[element] > 1:
                            self.dmg[element] -= 0.1
                    if self.penetrate > 1:
                        self.penetrate -= 0.1
                    else:  # no more penetrate power to move on
                        self.reach_target()  # remove sprite
                        return
            else:  # reach target
                self.base_pos = self.base_target
                self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                          self.base_pos[1] * self.screen_scale[1]) * 5
                self.rect.center = self.pos


class ChargeDamageSprite(DamageSprite):
    def __init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 accuracy=None, reach_effect=None):
        """Charge damage sprite"""
        DamageSprite.__init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                              accuracy=accuracy, reach_effect=reach_effect)
        self.base_pos = base_pos  # always move along with attacker
        self.angle = self.attacker.angle
        self.charge_power = 0
        if weapon:
            self.charge_power = self.attacker.weapon_data[self.attacker.equipped_weapon][weapon]["Charge"]

        self.rect = self.attacker.hitbox.rect

        self.battle.battle_camera.remove(self)  # no sprite to play since it use subunit sprite as damage sprite

    def change_weapon(self, dmg, penetrate, impact):
        self.dmg = dmg
        self.penetrate = penetrate
        self.knock_power = impact

    def update(self, subunit_list, dt):
        self.timer += dt
        if self.timer > 1:  # reset timer and list of subunit already hit
            self.timer -= 1
            self.already_hit = []  # sprite can deal dmg to same subunit only once every 1 second

        for subunit in self.attacker.near_enemy:  # collide check
            this_subunit = subunit[0]
            if this_subunit.alive and this_subunit.game_id not in self.already_hit and \
                    this_subunit.hitbox.rect.colliderect(self.rect):
                self.hit_register(this_subunit)
                self.already_hit.append(this_subunit.game_id)

        if not self.attacker.charging:  # remove sprite when attacker no longer charge
            self.attacker.charge_sprite = None
            self.clean_object()
            return


class EffectDamageSprite(DamageSprite):
    def __init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 accuracy=None, arc_shot=False, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, reach_effect=None):
        """Effect damage sprite"""
        DamageSprite.__init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                              arc_shot=arc_shot, height_ignore=height_ignore, degrade_when_travel=degrade_when_travel,
                              degrade_when_hit=degrade_when_hit, random_direction=random_direction,
                              random_move=random_move, accuracy=accuracy, reach_effect=reach_effect,
                              height_type=stat["Height Type"])

        self.base_pos = pygame.Vector2(base_pos)
        self.angle = 0

        self.duration = self.stat["Duration"]
        self.wind_disperse = self.stat["Wind Dispersion"]

        if weapon in self.sound_effect_pool:
            self.travel_sound_distance = stat["Sound Distance"]
            self.travel_shake_power = stat["Shake Power"]
            self.sound_effect_name = choice(self.sound_effect_pool[weapon])
            self.sound_duration = pygame.mixer.Sound(self.sound_effect_name).get_length()
            self.sound_timer = self.sound_duration / 1.5  # wait a bit before start playing
            self.travel_sound_distance_check = self.travel_sound_distance * 2
            if self.sound_duration > 2:
                self.sound_timer = self.sound_duration / 0.5

        if "(team)" in weapon:
            self.current_animation = self.effect_animation_pool[weapon][self.attacker.team][weapon]
        else:
            self.current_animation = self.effect_animation_pool[weapon][weapon]

        self.image = self.current_animation[self.show_frame]
        self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                  self.base_pos[1] * self.screen_scale[1]) * 5
        self.rect = self.image.get_rect(center=self.pos)

        self.adjust_sprite()

    def update(self, subunit_list, dt):
        done = True

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        self.timer += dt
        if self.timer > 1:  # reset timer
            if self.wind_disperse:
                self.speed = self.battle.current_weather.wind_strength
                self.base_target = pygame.Vector2(
                    self.base_pos[0] + (self.speed * sin(radians(self.battle.current_weather.wind_direction))),
                    self.base_pos[1] - (self.speed * cos(radians(self.battle.current_weather.wind_direction))))
                self.full_distance = self.base_pos.distance_to(self.base_target)
                self.duration -= self.speed
            if self.duration > 0:  # only clear for sprite with duration or charge
                self.duration -= self.timer
                self.already_hit = []  # sprite can deal dmg to same subunit only once every 1 second
            self.timer -= 1

        if self.current_animation:  # play animation if any
            done, just_start = self.play_animation(0.05, dt, False)

        for this_subunit in subunit_list:
            if this_subunit.game_id not in self.already_hit and \
                    ((self.aoe == 0 and this_subunit.hitbox.rect.colliderect(self.rect)) or
                     (self.aoe and this_subunit.base_pos.distance_to(self.base_pos) <= self.aoe)):
                this_subunit.apply_effect(self.weapon, self.stat,
                                          this_subunit.status_effect, this_subunit.status_duration)
                if self.stat["Status"]:
                    for status in self.stat["Status"]:
                        this_subunit.apply_effect(status, this_subunit.status_list[status],
                                                  this_subunit.status_effect, this_subunit.status_duration)
                if self.dmg:
                    self.hit_register(this_subunit)
                self.already_hit.append(this_subunit.game_id)

        if self.full_distance:  # damage sprite that can move
            move = self.base_target - self.base_pos
            require_move_length = move.length()

            if require_move_length:  # sprite move
                move.normalize_ip()
                move = move * self.speed * dt

                if move.length() <= require_move_length:
                    self.base_pos += move
                    if not self.arc_shot and not self.height_ignore and \
                            self.height_map.get_height(self.base_pos) > self.height + 20:
                        self.reach_target()  # direct shot will not be able to shoot pass higher height terrain midway
                        return

                    self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                              self.base_pos[1] * self.screen_scale[1]) * 5
                    self.rect.center = self.pos

                    if not self.random_move and (
                            self.base_pos[0] <= 0 or self.base_pos[0] >= self.battle.map_corner[0] or
                            self.base_pos[1] <= 0 or self.base_pos[1] >= self.battle.map_corner[
                                1]):  # pass outside of map
                        self.reach_target()
                        return

                    if self.degrade_when_travel and self.dmg:  # dmg and penetration power drop the longer damage sprite travel
                        for element in self.dmg:
                            if self.dmg[element] > 1:
                                self.dmg[element] -= 0.1
                        if self.penetrate > 1:
                            self.penetrate -= 0.1
                        else:  # no more penetrate power to move on
                            self.reach_target()  # remove sprite
                            return
                else:  # reach target
                    self.base_pos = self.base_target
                    self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                                              self.base_pos[1] * self.screen_scale[1]) * 5
                    self.rect.center = self.pos

        if done and self.duration <= 0:
            self.reach_target()
            return

        if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                self.travel_sound_distance_check > self.battle.true_camera_pos.distance_to(self.base_pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect_name, self.base_pos,
                                               self.travel_sound_distance,
                                               self.travel_shake_power)
            self.sound_timer = 0
