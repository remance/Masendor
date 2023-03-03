from pygame import Vector2
from math import cos, sin, radians
from random import choice, uniform, randint

from gamescript import damagesprite, effectsprite
from gamescript.common import utility

convert_degree_to_360 = utility.convert_degree_to_360


def attack(self, attack_type):
    base_target = None
    if self.attack_subunit:
        base_target = self.attack_subunit.base_pos
    elif self.attack_pos:
        base_target = self.attack_pos

    if base_target:
        if "weapon" in self.current_action:
            weapon = self.current_action["weapon"]
            equipped_weapon_data = self.equipped_weapon_data[weapon]
        else:
            weapon = None
            equipped_weapon_data = None

        if attack_type == "range":
            max_range = self.shoot_range[weapon]

            accuracy = self.accuracy
            sight_penalty = 1
            if weapon in self.equipped_timing_weapon and \
                self.equipped_timing_start_weapon[weapon] < self.release_timer < self.equipped_timing_end_weapon[weapon]:
                # release in timing bonus time, get accuracy boost
                accuracy *= 1.5

            if self.move:
                accuracy -= 10  # accuracy penalty for shoot while moving

            attack_range = self.base_pos.distance_to(base_target)
            if self.check_special_effect("No Range Penalty"):
                pass
            elif self.check_special_effect("Long Range Accurate"):
                accuracy = accuracy * (
                        100 - ((attack_range * 100 / max_range) / 4)) / 100  # range penalty half
            else:
                if attack_range > self.sight:  # penalty for range attack if shoot beyond troop can see
                    sight_penalty = self.sight / attack_range
                accuracy = accuracy * sight_penalty * (100 - ((attack_range * 100 / max_range) / 2)) / 100

            base_angle = self.set_rotate(base_target)
            # Wind affect accuracy, higher different in direction cause more accuracy loss
            angel_dif = (abs(convert_degree_to_360(base_angle) -
                             self.battle.current_weather.wind_direction) / 100) * self.battle.current_weather.wind_strength

            angel_dif += angel_dif * attack_range / 100
            accuracy -= round(angel_dif)

            arc_shot = self.check_special_effect("Arc Shot", weapon=weapon)
            if not arc_shot:  # direct shot just move until it reach max range
                base_target = Vector2(self.base_pos[0] - (max_range * sin(radians(base_angle))),
                                      self.base_pos[1] - (max_range * cos(radians(base_angle))))

            if self.attack_subunit:
                how_long = attack_range / self.speed  # shooting distance divide damage sprite speed to find travel time

                # Predicatively find position the enemy will be at based on movement speed and sprite travel time
                if self.attack_subunit.move and how_long > 0.5:  # target walking
                    target_move = self.attack_subunit.base_target - self.attack_subunit.base_pos  # target movement distance
                    if target_move.length() > 1:  # recal target base on enemy move target
                        target_move.normalize_ip()
                        base_target = base_target + ((target_move * (self.attack_subunit.move_speed * how_long)) / 11)
                        if not self.check_special_effect("Agile Aim"):
                            accuracy -= 15

            if self.check_special_effect("Cone Shot"):
                accuracy /= 1.25

            if accuracy < 0:
                accuracy = 0

            for _ in range(self.shot_per_shoot[self.equipped_weapon][weapon]):  # Shoot ammo
                # Calculate accuracy and final base_target where damage sprite will land
                # The further accuracy from 0 the further damage sprite will land from base_target
                if accuracy < 100:
                    accuracy = randint(int(accuracy), 100)  # random hit chance using accuracy as minimum value
                # target deviation as to percentage from base_target
                base_target = Vector2(base_target[0] * (100 + choice((accuracy / 100, -accuracy / 100))) / 100,
                                      base_target[1] * (100 + choice((accuracy / 100, -accuracy / 100))) / 100)

                dmg = {key: uniform(value[0], value[1]) for key, value in self.weapon_dmg[weapon].items()}
                if self.release_timer > 1 and self.current_action["weapon"] in self.equipped_power_weapon:
                    # apply power hold buff
                    for key in self.dmg:
                        dmg[key] *= 1.5

                damagesprite.RangeDamageSprite(self, weapon, dmg, self.weapon_penetrate[self.equipped_weapon][weapon],
                                               equipped_weapon_data, attack_type, self.front_pos, base_target,
                                               accuracy=accuracy, arc_shot=arc_shot)

            self.ammo_now[self.equipped_weapon][weapon] -= 1  # use 1 ammo per shot

            if self.ammo_now[self.equipped_weapon][weapon] == 0 and \
                    self.magazine_count[self.equipped_weapon][weapon] == 0:
                self.ammo_now[self.equipped_weapon].pop(weapon)  # remove weapon with no ammo
                self.magazine_count[self.equipped_weapon].pop(weapon)
                if not self.ammo_now[self.equipped_weapon]:  # remove entire set if no ammo at all
                    self.ammo_now.pop(self.equipped_weapon)
                    self.magazine_count.pop(self.equipped_weapon)
                    self.range_weapon_set.remove(self.equipped_weapon)

            if equipped_weapon_data["Sound Effect"] in self.sound_effect_pool:  # add attack sound to playlist
                self.battle.add_sound_effect_queue(
                    choice(self.sound_effect_pool[equipped_weapon_data["Sound Effect"]]),
                    self.base_pos, equipped_weapon_data["Sound Distance"],
                    equipped_weapon_data["Shake Power"])

        elif attack_type == "charge":
            if weapon:
                dmg = {key: value[0] for key, value in self.weapon_dmg[weapon].items()}
                penetrate = self.weapon_penetrate[self.equipped_weapon][weapon]
                stat = equipped_weapon_data
            else:  # charge without using weapon (by running)
                dmg = self.body_weapon_damage
                penetrate = self.body_weapon_penetrate
                stat = self.body_weapon_stat
            if self.charge_sprite:  # charge sprite already existed
                self.charge_sprite.change_weapon(dmg, penetrate, stat)
            else:
                self.charge_sprite = damagesprite.ChargeDamageSprite(self, weapon, dmg, penetrate, stat,
                                                                     "charge", self.base_pos, self.base_pos,
                                                                     accuracy=self.melee_attack)

        else:  # melee attack
            accuracy = self.melee_attack
            if weapon in self.equipped_timing_weapon and \
                self.equipped_timing_start_weapon[weapon] < self.release_timer < self.equipped_timing_end_weapon[weapon]:
                # release in timing bonus time, get accuracy boost
                accuracy *= 1.5

            if self.front_pos.distance_to(base_target) > self.melee_range[weapon]:  # target exceed weapon range, use max
                base_angle = self.set_rotate(base_target)
                base_target = Vector2(self.front_pos[0] - (self.melee_range[weapon] * sin(radians(base_angle))),
                                      self.front_pos[1] - (self.melee_range[weapon] * cos(radians(base_angle))))

            dmg = {key: uniform(value[0], value[1]) for key, value in self.weapon_dmg[weapon].items()}
            if self.release_timer > 1 and self.current_action["weapon"] in self.equipped_power_weapon:
                # apply power hold buff
                for key in self.dmg:
                    dmg[key] *= 1.5

            damagesprite.MeleeDamageSprite(self, weapon, dmg, self.weapon_penetrate[self.equipped_weapon][weapon],
                                           equipped_weapon_data, attack_type, self.base_pos,
                                           base_target, accuracy=accuracy)

            self.weapon_cooldown[weapon] = 0  # melee weapon use cooldown for attack

            if equipped_weapon_data["Sound Effect"] in self.sound_effect_pool:  # add attack sound to playlist
                self.battle.add_sound_effect_queue(choice(self.sound_effect_pool[equipped_weapon_data["Sound Effect"]]),
                                                   self.base_pos, equipped_weapon_data["Sound Distance"],
                                                   equipped_weapon_data["Shake Power"])

        self.release_timer = 0  # reset release timer after attack

        if equipped_weapon_data:
            self.stamina -= self.weapon_weight[self.equipped_weapon][weapon]
            if equipped_weapon_data["After Attack Effect"]:
                effect_stat = self.effect_list[equipped_weapon_data["After Attack Effect"]]
                dmg = {key: effect_stat[key + " Damage"] for key in self.original_element_resistance if
                       key + " Damage" in effect_stat}
                if sum(dmg.values()) <= 0:
                    dmg = None
                else:
                    dmg = {key: (value / 2, value) for key, value in dmg.items()}

                # use end of sprite instead of front_pos so effect not show up inside troop body sprite
                base_target = Vector2(self.base_pos[0] - (self.attack_effect_spawn_distance * sin(radians(self.angle))),
                                      self.base_pos[1] - (self.attack_effect_spawn_distance * cos(radians(self.angle))))

                damagesprite.EffectDamageSprite(self, equipped_weapon_data["After Attack Effect"], dmg,
                                                effect_stat["Armour Penetration"], effect_stat, "effect",
                                                base_target, base_target,
                                                reach_effect=effect_stat["After Reach Effect"])
