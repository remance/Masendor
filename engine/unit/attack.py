from math import cos, sin, radians
from random import choice, uniform, randint

from pygame import Vector2

from engine.effect.effect import MeleeDamageEffect, RangeDamageEffect, EffectDamageEffect
from engine.utility import convert_degree_to_360


def attack(self, attack_type):
    base_target = None
    if self.attack_pos:
        base_target = self.attack_pos
        self.attack_pos = None  # only one time pos attack
    elif self.nearest_enemy:
        base_target = self.nearest_enemy[0].base_pos

    if base_target:
        if "weapon" in self.current_action:
            weapon = self.current_action["weapon"]
            attack_weapon_data = self.equipped_weapon_data[weapon]
        else:
            weapon = None
            attack_weapon_data = None

        if attack_type == "range":
            max_range = self.shoot_range[weapon]

            accuracy = self.accuracy
            sight_penalty = 1
            if self.equipped_timing_start_weapon[weapon] and \
                    self.equipped_timing_start_weapon[weapon] < self.release_timer < self.equipped_timing_end_weapon[
                weapon]:
                # release in timing bonus time, get accuracy boost
                accuracy *= 1.5

            if self.move_speed:
                accuracy -= 10  # accuracy penalty for shoot while moving

            attack_range = self.base_pos.distance_to(base_target)

            if self.check_special_effect("No Range Penalty"):
                pass
            elif self.check_special_effect("Long Range Accurate"):
                accuracy = accuracy * (
                        100 - ((attack_range * 100 / max_range) / 4)) / 100  # range penalty half
            else:
                # if attack_range > self.sight:  # penalty for range attack if shoot beyond troop can see
                #     sight_penalty = self.sight / attack_range
                accuracy = accuracy * sight_penalty * (100 - ((attack_range * 100 / max_range) / 2)) / 100
                # accuracy = accuracy * sight_penalty * (100 - ((attack_range * 100 / max_range) / 2)) / 100

            base_angle = self.set_rotate(base_target)
            # Wind affect accuracy, higher different in direction cause more accuracy loss
            angel_dif = ((180 - abs(abs(convert_degree_to_360(base_angle) -
                                        self.battle.current_weather.wind_direction) - 180)) / 100) * \
                        self.battle.current_weather.wind_strength

            angel_dif += angel_dif * attack_range / 100
            accuracy -= round(angel_dif)

            arc_shot = self.check_special_effect("Arc Shot", weapon=weapon)

            if not arc_shot:  # direct shot just move until it reach max range
                base_target = Vector2(self.base_pos[0] - (max_range * sin(radians(base_angle))),
                                      self.base_pos[1] - (max_range * cos(radians(base_angle))))

            # if self.melee_target:  # check if unit moving, then find new target based on their speed and direction
            #     how_long = attack_range / attack_weapon_data["Travel Speed"]  # shooting distance divide bullet speed to find travel time
            #     # Predicatively find position the enemy will be at based on movement speed and sprite travel time
            #     if self.melee_target.move_speed and how_long > 0.5:  # target walking
            #         target_move = self.melee_target.base_target - self.melee_target.base_pos  # target movement distance
            #         if target_move.length() > 1:  # recalculate target base on enemy move target
            #             target_move.normalize_ip()
            #             base_target = base_target + ((target_move * (self.melee_target.move_speed * how_long)) / 11)
            #             if not self.check_special_effect("Agile Aim"):
            #                 accuracy -= 15

            if self.check_special_effect("Cone Shot"):
                accuracy /= 1.25

            if accuracy < 0:
                accuracy = 0

            for _ in range(self.shot_per_shoot[self.equipped_weapon][weapon]):  # Shoot ammo
                # Calculate inaccuracy and final base_target where damage sprite will land
                # The further inaccuracy from 0 the further damage sprite will land from base_target
                inaccuracy = 100 - accuracy
                if inaccuracy < 0:
                    inaccuracy = 0
                else:
                    inaccuracy = randint(0, int(inaccuracy))  # random hit chance
                # target deviation as to percentage from base_target
                base_target = Vector2(base_target[0] * (100 + choice((inaccuracy / 50, -inaccuracy / 50))) / 100,
                                      base_target[1] * (100 + choice((inaccuracy / 50, -inaccuracy / 50))) / 100)
                dmg = {key: uniform(value[0], value[1]) for key, value in self.weapon_dmg[weapon].items()}
                if self.release_timer > 1 and weapon in self.equipped_power_weapon:
                    # apply power hold buff
                    for key in self.dmg:
                        dmg[key] *= 1.5

                impact = self.weapon_impact[self.equipped_weapon][weapon] * self.weapon_impact_effect

                radians_angle = radians(360 - base_angle)
                start_pos = Vector2(self.base_pos[0] + (self.hitbox_front_distance * sin(radians_angle)),
                                    self.base_pos[1] - (self.hitbox_front_distance * cos(radians_angle)))

                RangeDamageEffect(self, base_angle, weapon, dmg, self.weapon_penetrate[self.equipped_weapon][weapon],
                                  impact, attack_weapon_data, attack_type, start_pos, base_target,
                                  accuracy=accuracy, arc_shot=arc_shot,
                                  reach_effect=attack_weapon_data[
                                      "After Reach Effect"])

            self.ammo_now[self.equipped_weapon][weapon] -= 1  # use 1 ammo per shot

            if self.ammo_now[self.equipped_weapon][weapon] == 0 and \
                    self.magazine_count[self.equipped_weapon][weapon] == 0:
                self.ammo_now[self.equipped_weapon].pop(weapon)  # remove weapon with no ammo
                self.magazine_count[self.equipped_weapon].pop(weapon)
                if not self.ammo_now[self.equipped_weapon]:  # remove entire set if no ammo at all
                    self.ammo_now.pop(self.equipped_weapon)
                    self.magazine_count.pop(self.equipped_weapon)
                    self.range_weapon_set.remove(self.equipped_weapon)

            if self.active_action_skill["range"]:  # check if any skill range action active
                for skill in self.active_action_skill["range"].copy():
                    self.skill_duration[skill] -= 1
                    if self.skill_duration[skill] <= 0:  # skill end
                        self.skill_duration.pop(skill)
                        self.skill_effect.pop(skill)
                        self.active_action_skill["range"].remove(skill)

            if attack_weapon_data["Sound Effect"] in self.sound_effect_pool:  # add attack sound to playlist
                self.battle.add_sound_effect_queue(
                    choice(self.sound_effect_pool[attack_weapon_data["Sound Effect"]]),
                    self.base_pos, attack_weapon_data["Sound Distance"],
                    attack_weapon_data["Shake Power"])

        else:  # melee attack
            accuracy = self.melee_attack
            if self.equipped_timing_start_weapon[weapon] and \
                    self.equipped_timing_start_weapon[weapon] < self.release_timer < self.equipped_timing_end_weapon[
                weapon]:
                # release in timing bonus time, get accuracy boost
                accuracy *= 1.5

            base_angle = self.set_rotate(base_target)

            if self.front_pos.distance_to(base_target) > self.melee_range[
                weapon]:  # target exceed weapon range, use max
                base_target = Vector2(self.front_pos[0] - (self.melee_range[weapon] * sin(radians(base_angle))),
                                      self.front_pos[1] - (self.melee_range[weapon] * cos(radians(base_angle))))

            dmg = {key: uniform(value[0], value[1]) for key, value in self.weapon_dmg[weapon].items()}
            if self.release_timer > 1 and weapon in self.equipped_power_weapon:
                # apply power hold buff
                for key in dmg:
                    dmg[key] *= 1.5

            impact = self.weapon_impact[self.equipped_weapon][weapon] * self.weapon_impact_effect

            MeleeDamageEffect(self, base_angle, weapon, dmg, self.weapon_penetrate[self.equipped_weapon][weapon],
                              impact, attack_weapon_data, attack_type, base_target,
                              base_target, accuracy=accuracy)

            if self.active_action_skill["melee"]:  # check if any skill melee action active
                for skill in self.active_action_skill["melee"].copy():
                    self.skill_duration[skill] -= 1
                    if self.skill_duration[skill] <= 0:  # skill end
                        self.skill_duration.pop(skill)
                        self.skill_effect.pop(skill)
                        self.active_action_skill["melee"].remove(skill)

            self.weapon_cooldown[weapon] = 0  # melee weapon use cooldown for attack

            if attack_weapon_data["Sound Effect"] in self.sound_effect_pool:  # add attack sound to playlist
                self.battle.add_sound_effect_queue(choice(self.sound_effect_pool[attack_weapon_data["Sound Effect"]]),
                                                   self.base_pos, attack_weapon_data["Sound Distance"],
                                                   attack_weapon_data["Shake Power"])

        self.release_timer = 0  # reset release timer after attack

        if attack_weapon_data:
            self.stamina -= self.weapon_weight[self.equipped_weapon][weapon]
            if attack_weapon_data["After Attack Effect"]:
                effect_stat = self.effect_list[attack_weapon_data["After Attack Effect"]]
                dmg = {key: effect_stat[key + " Damage"] for key in self.original_element_resistance if
                       key + " Damage" in effect_stat}
                if sum(dmg.values()) <= 0:
                    dmg = None
                else:
                    dmg = {key: (value / 2, value) for key, value in dmg.items()}

                # use end of sprite instead of front_pos so effect not show up inside troop body sprite
                base_target = Vector2(self.base_pos[0] - (self.attack_effect_spawn_distance * sin(radians(self.angle))),
                                      self.base_pos[1] - (self.attack_effect_spawn_distance * cos(radians(self.angle))))

                EffectDamageEffect(self, attack_weapon_data["After Attack Effect"], dmg,
                                   effect_stat["Armour Penetration"], effect_stat["Impact"], effect_stat, "effect",
                                   base_target, base_target, base_angle, reach_effect=effect_stat["After Reach Effect"])
