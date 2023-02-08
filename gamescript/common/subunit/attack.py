import math
import random

import pygame
from gamescript import damagesprite
from gamescript.common import utility

convert_degree_to_360 = utility.convert_degree_to_360


def attack(self, attack_type):
    weapon = int(self.current_action["name"][-1])
    base_target = None
    if "pos" in self.current_action:  # manual attack position
        base_target = self.current_action["pos"]
    elif self.attack_target is not None:
        base_target = self.attack_target.base_pos
    elif self.attack_pos is not None:
        base_target = self.attack_pos
    if attack_type == "range":
        if base_target is not None:
            equipped_weapon_data = self.equipped_weapon_data[weapon]
            if "arc shot" in self.current_action:
                arc_shot = self.current_action["arc shot"]
            else:  # check if the attack require arc shot and can use it, for player manual attack
                arc_shot = False
                clip = self.check_line_of_sight(base_target)
                if clip and self.check_special_effect("Arc Shot", weapon=weapon):
                    arc_shot = True
            max_range = self.shoot_range[weapon]

            accuracy = self.accuracy
            sight_penalty = 1

            if self.move:
                accuracy -= 10  # accuracy penalty for shoot while moving
            if arc_shot:  # arc shot incur accuracy penalty:
                accuracy -= 10

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
            if arc_shot:  # higher travel distance mean more effect from wind, arc shot suffer more from wind
                angel_dif += angel_dif * attack_range / 50
            else:
                angel_dif += angel_dif * attack_range / 100
            accuracy -= round(angel_dif)

            if self.attack_target is not None:
                if self.attack_target.alive_subunit_list:
                    target_hit = self.find_attack_target(
                        self.attack_target.alive_subunit_list)  # find the closest subunit in enemy unit
                    how_long = attack_range / self.speed  # shooting distance divide damage sprite speed to find travel time

                    # Predicatively find position the enemy will be at based on movement speed and sprite travel time
                    if target_hit.move and how_long > 0.5:  # target walking
                        target_move = target_hit.base_target - target_hit.base_pos  # target movement distance
                        if target_move.length() > 1:
                            target_move.normalize_ip()
                            base_target = target_hit.base_pos + (
                                    (target_move * (
                                                target_hit.move_speed * how_long)) / 11)  # recal target base on enemy move target
                            if self.check_special_effect("Agile Aim") is False:
                                accuracy -= 15

            if self.check_special_effect("Cone Shot"):
                accuracy /= 2

            if accuracy < 0:
                accuracy = 0

            for _ in range(self.shot_per_shoot[self.equipped_weapon][weapon]):  # Shoot ammo
                # Calculate accuracy and final base_target where damage sprite will land
                # The further accuracy from 0 the further damage sprite will land from base_target
                if accuracy < 100:
                    accuracy = random.randint(int(accuracy), 100)  # random hit chance using accuracy as minimum value
                if random.randint(0, 100) > accuracy:  # miss, not land exactly at base_target
                    if random.randint(0, 1) == 0:  # target deviation as to percentage from base_target
                        hit_chance1 = 100 + (accuracy / 50)
                    else:
                        hit_chance1 = 100 - (accuracy / 50)
                    if random.randint(0, 1) == 0:
                        hit_chance2 = 100 + (accuracy / 50)
                    else:
                        hit_chance2 = 100 - (accuracy / 50)
                    base_target = pygame.Vector2(base_target[0] * hit_chance1 / 100,
                                                 base_target[1] * hit_chance2 / 100)

                if arc_shot is False:  # direct shot just shoot base on direction of target at max range
                    base_target = pygame.Vector2(self.base_pos[0] - (max_range *
                                                                     math.sin(math.radians(base_angle))),
                                                 self.base_pos[1] - (max_range *
                                                                     math.cos(math.radians(base_angle))))

                damagesprite.DamageSprite(self, weapon, self.weapon_dmg[weapon],
                                          self.weapon_penetrate[self.equipped_weapon][weapon], equipped_weapon_data,
                                          attack_type, base_target, accuracy=accuracy, arc_shot=arc_shot)

            if equipped_weapon_data["Sound Effect"] in self.sound_effect_pool:
                self.battle.add_sound_effect_queue(equipped_weapon_data["Sound Effect"], self.base_pos,
                                                   equipped_weapon_data["Sound Distance"],
                                                   equipped_weapon_data["Shake Power"])

            self.ammo_now[self.equipped_weapon][weapon] -= 1  # use 1 ammo per shot
            if self.ammo_now[self.equipped_weapon][weapon] == 0 and \
                    self.magazine_count[self.equipped_weapon][weapon] == 0:
                self.ammo_now[self.equipped_weapon].pop(weapon)  # remove weapon with no ammo
                self.magazine_count[self.equipped_weapon].pop(weapon)
                if not self.ammo_now[self.equipped_weapon]:  # remove entire set if no ammo at all
                    self.ammo_now.pop(self.equipped_weapon)
                    self.magazine_count.pop(self.equipped_weapon)
                    self.range_weapon_set.remove(self.equipped_weapon)
    else:
        equipped_weapon_data = self.equipped_weapon_data[weapon]
        weapon_range = equipped_weapon_data["Range"]
        if self.front_pos.distance_to(base_target) > weapon_range:
            base_angle = self.set_rotate(base_target)
            base_target = pygame.Vector2(self.front_pos[0] - (weapon_range *
                                                              math.sin(math.radians(base_angle))),
                                         self.front_pos[1] - (weapon_range *
                                                              math.cos(math.radians(base_angle))))
        damagesprite.DamageSprite(self, weapon, self.weapon_dmg[weapon],
                                  self.weapon_penetrate[self.equipped_weapon][weapon],
                                  self.equipped_weapon_data[weapon], attack_type, base_target)

        self.weapon_cooldown[weapon] = 0  # melee weapon use cooldown for attack

    self.stamina -= self.weapon_weight[self.equipped_weapon][weapon]
