from abc import ABC, abstractmethod
from math import cos, sin, radians
from random import choice, uniform

from pygame import sprite, mixer, Vector2

from engine.effect import adjust_sprite, cal_dmg, cal_charge_hit, cal_effect_hit, cal_melee_hit, cal_range_hit, \
    find_random_direction, hit_register, play_animation
from engine.utility import clean_object, set_rotate


class Effect(sprite.Sprite):
    clean_object = clean_object
    set_rotate = set_rotate

    effect_sprite_pool = None
    effect_animation_pool = None
    effect_list = None
    sound_effect_pool = {}
    battle = None
    screen_scale = (1, 1)

    bullet_sprite_pool = None
    bullet_weapon_sprite_pool = None
    height_map = None

    adjust_sprite = adjust_sprite.adjust_sprite
    cal_charge_hit = cal_charge_hit.cal_charge_hit
    cal_dmg = cal_dmg.cal_dmg
    cal_effect_hit = cal_effect_hit.cal_effect_hit
    cal_melee_hit = cal_melee_hit.cal_melee_hit
    cal_range_hit = cal_range_hit.cal_range_hit
    find_random_direction = find_random_direction.find_random_direction
    hit_register = hit_register.hit_register
    play_animation = play_animation.play_animation

    def __init__(self, attacker, base_pos, target, effect_type, sprite_name, angle=0, layer=10000000,
                 make_sound=True):
        """Effect sprite that does not affect unit in any way"""
        self._layer = layer
        sprite.Sprite.__init__(self, self.containers)

        self.show_frame = 0
        self.frame_timer = 0
        self.timer = 0
        self.repeat_animation = False

        self.attacker = attacker

        self.base_pos = Vector2(base_pos)
        self.pos = Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * 5
        self.base_target = target
        self.angle = angle

        self.sound_effect_name = None
        self.sound_timer = 0
        self.sound_duration = 0
        self.scale_size = 1

        if make_sound:
            if effect_type in self.sound_effect_pool:
                self.travel_sound_distance = self.effect_list[effect_type]["Sound Distance"]
                self.travel_shake_power = self.effect_list[effect_type]["Shake Power"]
                self.sound_effect_name = choice(self.sound_effect_pool[effect_type])
                self.sound_duration = mixer.Sound(self.sound_effect_name).get_length()
                self.sound_timer = 0  # start playing right away when first update

        self.current_animation = {}
        if effect_type:  # effect can have no sprite like charge
            if "Base Main" in sprite_name:  # range weapon that use weapon sprite as effect
                weapon = int(sprite_name[-1])
                if self.attacker.weapon_version[self.attacker.equipped_weapon][weapon] in \
                        self.bullet_weapon_sprite_pool[effect_type]:
                    self.image = self.bullet_weapon_sprite_pool[effect_type][
                        self.attacker.weapon_version[self.attacker.equipped_weapon][weapon]]["Bullet"]
                else:
                    self.image = self.bullet_weapon_sprite_pool[effect_type]["common"]["Bullet"]

            else:
                effect_name = "".join(sprite_name.split("_"))[-1]
                if effect_name[-1].isdigit():
                    effect_name = sprite_name[:-2]
                else:
                    effect_name = sprite_name
                if "(team)" in effect_type:
                    self.current_animation = self.effect_animation_pool[effect_type][self.attacker.team][effect_name]
                else:
                    self.current_animation = self.effect_animation_pool[effect_type][effect_name]

                self.image = self.current_animation[self.show_frame]
                if len(self.current_animation) == 1:  # one frame mean no animation
                    self.current_animation = {}

            self.adjust_sprite()

    def update(self, unit_list, dt):
        if self.current_animation:
            done, just_start = self.play_animation(0.1, dt)

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.sound_effect_name and self.sound_timer >= self.sound_duration and \
                self.travel_sound_distance > self.battle.true_camera_pos.distance_to(self.base_pos):
            # play sound, check for distance here to avoid timer reset when not on screen
            self.battle.add_sound_effect_queue(self.sound_effect_name, self.base_pos,
                                               self.travel_sound_distance,
                                               self.travel_shake_power)
            self.sound_timer = 0

        if done:  # no duration, kill effect when animation end
            self.clean_object()
            return


class DamageEffect(ABC, Effect, sprite.Sprite):

    @abstractmethod  # DamageEffect should not be initiated on its own
    def __init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 effect_type, sprite_name, angle, accuracy=None, arc_shot=False, height_ignore=False,
                 degrade_when_travel=True, degrade_when_hit=True, random_direction=False, random_move=False,
                 reach_effect=None, height_type=1, make_sound=True):
        """Damage or effect sprite that can affect or damage unit"""
        Effect.__init__(self, attacker, base_pos, base_target, effect_type, sprite_name, angle,
                        layer=10000000 + height_type, make_sound=make_sound)

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

        self.duration = 0
        self.sound_effect_name = None
        self.stamina_dmg_bonus = 0
        self.sprite_direction = ""
        self.attacker_sprite_direction = self.attacker.sprite_direction
        self.already_hit = {}  # dict of unit already got hit with time by sprite for sprite with no duration

        self.dmg = dmg
        self.deal_dmg = False
        if self.dmg:  # has damage to deal
            self.deal_dmg = True

        self.penetrate = penetrate
        self.knock_power = impact

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
            EffectDamageEffect(self, self.reach_effect, dmg, effect_stat["Armour Penetration"],
                               effect_stat["Impact"],
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
                EffectDamageEffect(self, self.stat["End Effect"], dmg, effect_stat["Armour Penetration"],
                                   effect_stat["Impact"], effect_stat, "effect", self.base_pos, self.base_pos,
                                   reach_effect=effect_stat["After Reach Effect"])
        self.clean_object()


class MeleeDamageEffect(DamageEffect):
    def __init__(self, attacker, angle, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 accuracy=None, reach_effect=None):
        """Melee damage sprite"""
        effect_type = stat["Damage Sprite"]
        sprite_name = attack_type[1].capitalize()

        DamageEffect.__init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                              effect_type, sprite_name, angle, accuracy=accuracy, reach_effect=reach_effect)

    def update(self, unit_list, dt):
        """Melee damage effect does not travel"""
        done = False

        if self.current_animation:  # play animation if any
            done, just_start = self.play_animation(0.05, dt, False)

        hit_list = sprite.spritecollide(self, self.attacker.enemy_list, False)
        if hit_list:
            for unit in hit_list:  # collide check
                self.hit_register(unit.attacker)
                if self.penetrate <= 0:
                    break  # use break for melee to last until animation done

        if done:
            self.reach_target()
            return


class RangeDamageEffect(DamageEffect):
    def __init__(self, attacker, angle, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 accuracy=None, arc_shot=False, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, reach_effect=None):
        """Range damage sprite"""
        if stat["Damage Sprite"] != "self":
            effect_type = stat["Damage Sprite"]
            sprite_name = "Base"
        else:  # use weapon image itself as bullet image
            effect_type = stat["Name"]
            sprite_name = "Base Main" + str(weapon)
        sound_name = effect_type

        DamageEffect.__init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, Vector2(base_pos),
                              base_target, effect_type, sprite_name, angle, accuracy=accuracy, arc_shot=arc_shot,
                              height_ignore=height_ignore, degrade_when_travel=degrade_when_travel,
                              degrade_when_hit=degrade_when_hit, random_direction=random_direction,
                              random_move=random_move, reach_effect=reach_effect, make_sound=False)
        self.repeat_animation = True

        self.speed = stat["Travel Speed"]  # bullet travel speed
        if sound_name in self.sound_effect_pool:
            self.travel_sound_distance = stat["Bullet Sound Distance"]
            self.travel_shake_power = stat["Bullet Shake Power"]
            self.sound_effect_name = choice(self.sound_effect_pool[sound_name])
            self.sound_duration = mixer.Sound(self.sound_effect_name).get_length() * 1000 / self.speed
            self.sound_timer = self.sound_duration
            self.travel_sound_distance_check = self.travel_sound_distance * 2

    def update(self, unit_list, dt):
        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        if self.duration > 0:
            self.duration -= dt

        if self.current_animation:  # play animation if any
            self.play_animation(0.05, dt, False)

        for key in tuple(self.already_hit.keys()):
            self.already_hit[key] -= dt
            if self.already_hit[key] <= 0:
                self.already_hit.pop(key)

        hit_list = sprite.spritecollide(self, self.attacker.enemy_list, False)
        if hit_list and ((self.arc_shot and self.distance_progress >= 100) or not self.arc_shot):
            for unit in hit_list:  # collide check
                this_unit = unit.attacker
                if this_unit.alive and this_unit not in self.already_hit:
                    self.hit_register(this_unit)
                    if not self.arc_shot:
                        self.already_hit[this_unit] = 1
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

                self.pos = Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * 5
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
                self.pos = Vector2(self.base_pos[0] * self.screen_scale[0], self.base_pos[1] * self.screen_scale[1]) * 5
                self.rect.center = self.pos


class ChargeDamageEffect(Effect):
    def __init__(self, attacker):
        """Charge damage sprite, also served as hitbox for unit"""
        Effect.__init__(self, attacker, attacker.base_pos, None, None, None, layer=1, make_sound=False)
        self.aoe = 0
        self.image = self.attacker.hitbox_image
        self.image_charge = False
        self.attack_type = "charge"
        self.already_hit = {}
        self.base_pos = self.attacker.base_pos  # always move along with attacker
        self.rect = self.image.get_rect(center=self.base_pos)

    def update(self, unit_list, dt):
        self.angle = self.attacker.angle
        for key in tuple(self.already_hit.keys()):
            self.already_hit[key] -= dt
            if self.already_hit[key] <= 0:
                self.already_hit.pop(key)

        if self.attacker.momentum == 1:
            if not self.image_charge:
                self.image_charge = True
                self.image = self.attacker.hitbox_image_charge
            hit_list = sprite.spritecollide(self, self.attacker.enemy_list, False)
            if hit_list:
                for unit in hit_list:  # collide check
                    this_unit = unit.attacker
                    hit_angle = self.set_rotate(this_unit.base_pos)
                    if this_unit.alive and abs(hit_angle - self.angle) <= 45 and \
                            this_unit not in self.already_hit:
                        # Charge damage only hit those at front of charger
                        self.hit_register(this_unit)
                        self.already_hit[this_unit] = 1
        else:  # no longer charging check hitbox image change back to normal
            if self.image_charge:
                self.image_charge = False
                self.image = self.attacker.hitbox_image


class EffectDamageEffect(DamageEffect):
    def __init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                 angle=0, accuracy=None, arc_shot=False, height_ignore=False, degrade_when_travel=True,
                 degrade_when_hit=True, random_direction=False, random_move=False, reach_effect=None):
        """Effect damage sprite such as explosion or smoke"""
        DamageEffect.__init__(self, attacker, weapon, dmg, penetrate, impact, stat, attack_type, base_pos, base_target,
                              weapon, weapon, angle, arc_shot=arc_shot, height_ignore=height_ignore,
                              degrade_when_travel=degrade_when_travel,
                              degrade_when_hit=degrade_when_hit, random_direction=random_direction,
                              random_move=random_move, accuracy=accuracy, reach_effect=reach_effect,
                              height_type=stat["Height Type"], make_sound=False)

        if weapon in self.sound_effect_pool:
            self.travel_sound_distance = stat["Sound Distance"]
            self.travel_shake_power = stat["Shake Power"]
            self.sound_effect_name = choice(self.sound_effect_pool[weapon])
            self.sound_duration = mixer.Sound(self.sound_effect_name).get_length()
            self.sound_timer = self.sound_duration
            self.travel_sound_distance_check = self.travel_sound_distance * 2
            if self.sound_duration > 2:
                self.sound_timer = self.sound_duration / 0.5

        self.duration = self.stat["Duration"]
        self.wind_disperse = self.stat["Wind Dispersion"]

    def update(self, unit_list, dt):
        done = True

        if self.sound_effect_name and self.sound_timer < self.sound_duration:
            self.sound_timer += dt

        self.timer += dt
        for key in tuple(self.already_hit.keys()):
            self.already_hit[key] -= dt
            if self.already_hit[key] <= 0:
                self.already_hit.pop(key)

        if self.timer > 1:  # reset timer
            if self.wind_disperse:
                self.speed = self.battle.current_weather.wind_strength
                self.base_target = Vector2(
                    self.base_pos[0] + (self.speed * sin(radians(self.battle.current_weather.wind_direction))),
                    self.base_pos[1] - (self.speed * cos(radians(self.battle.current_weather.wind_direction))))
                self.full_distance = self.base_pos.distance_to(self.base_target)
                self.duration -= self.speed
            if self.duration > 0:  # only clear for sprite with duration or charge
                self.duration -= self.timer
            self.timer -= 1

        if self.current_animation:  # play animation if any
            done, just_start = self.play_animation(0.05, dt, False)

        if not self.aoe:
            hit_list = sprite.spritecollide(self, unit_list, False)
        for this_unit in unit_list:
            if this_unit not in self.already_hit and \
                    ((not self.aoe and this_unit.hitbox in hit_list) or
                     (self.aoe and this_unit.base_pos.distance_to(self.base_pos) <= self.aoe)):
                this_unit.apply_effect(self.weapon, self.stat, this_unit.status_effect, this_unit.status_duration)
                if self.stat["Status"]:
                    for status in self.stat["Status"]:
                        this_unit.apply_effect(status, this_unit.status_list[status],
                                               this_unit.status_effect, this_unit.status_duration)
                if self.dmg:
                    self.hit_register(this_unit)
                self.already_hit[this_unit] = 1

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

                    self.pos = Vector2(self.base_pos[0] * self.screen_scale[0],
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
                    self.pos = Vector2(self.base_pos[0] * self.screen_scale[0],
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
