import pygame
import random
import math

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
    if attack_type == "range" and base_target is not None:
        equipped_weapon_data = self.equipped_weapon_data[weapon]
        arc_shot = self.current_action["arc shot"]
        max_range = self.shoot_range[weapon]

        accuracy = self.accuracy

        if (self.walk or self.run) and arc_shot is False:
            accuracy -= 10  # accuracy penalty for shoot while moving
        if arc_shot:  # arc shot incur accuracy penalty:
            accuracy -= 10

        # Wind affect accuracy, higher different in direction cause more accuracy loss
        base_angle = self.set_rotate(base_target)
        base_angle = convert_degree_to_360(base_angle)
        angel_dif = (abs(base_angle - self.battle.current_weather.wind_direction) / 100) * self.battle.current_weather.wind_strength
        accuracy -= round(angel_dif)

        if accuracy < 0:
            accuracy = 0

        sight_penalty = 1

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

        if self.attack_target is not None:
            if len(self.attack_target.alive_subunit_list) > 0:
                target_hit = self.find_attack_target(
                    self.attack_target.alive_subunit_list)  # find the closest subunit in enemy unit
                base_target = target_hit.base_pos  # base_target is at the enemy position
                how_long = attack_range / self.speed  # shooting distance divide damage sprite speed to find travel time

                # Predicatively find position the enemy will be at based on movement speed and sprite travel time
                if (target_hit.walk or target_hit.run) and how_long > 0.5:  # target walking
                    target_move = target_hit.base_target - target_hit.base_pos  # target movement distance
                    if target_move.length() > 1:
                        target_move.normalize_ip()
                        move_speed = target_hit.unit.walk_speed
                        if target_hit.run:
                            move_speed = target_hit.unit.run_speed
                        base_target = target_hit.base_pos + (
                                (target_move * (move_speed * how_long)) / 11)
                        if self.check_special_effect("Agile Aim") is False:
                            accuracy -= 15

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
                    hit_chance2 = 100 + (accuracy / 50)
                base_target = pygame.Vector2(base_target[0] * hit_chance1 / 100,
                                             base_target[1] * hit_chance2 / 100)

            if arc_shot is False:  # direct shot just shoot base on direction of target at max range
                base_target = pygame.Vector2(self.base_pos[0] - (max_range *
                                                                  math.sin(math.radians(self.angle))),
                                             self.base_pos[1] - (max_range *
                                                                  math.cos(math.radians(self.angle))))

            damagesprite.DamageSprite(self, weapon, self.weapon_dmg[weapon],
                                      self.weapon_penetrate[self.equipped_weapon][weapon],
                                      equipped_weapon_data, self.camera_zoom, attack_type,
                                      base_target, accuracy=accuracy, arc_shot=arc_shot)

        if equipped_weapon_data["Sound Effect"] in self.sound_effect_pool:
            distance = self.base_pos.distance_to(self.battle.true_camera_pos)
            if distance < 1:
                distance = 1
            sound_distance = equipped_weapon_data["Sound Distance"] / distance
            if sound_distance < 0:
                sound_distance = 0
            elif sound_distance > 1:
                sound_distance = 1
            effect_volume = sound_distance * (self.camera_zoom / self.max_camera_zoom) * \
                            self.battle.play_effect_volume

            # print(effect_volume, equipped_weapon_data["Sound Distance"], self.battle.play_effect_volume,
            #       sound_distance, self.base_pos, self.battle.true_camera_pos, self.camera_zoom)
            if effect_volume > 0:
                if effect_volume > 1:
                    effect_volume = 1
                sound_effect = pygame.mixer.Sound(self.sound_effect_pool[equipped_weapon_data["Sound Effect"]])
                sound_effect.set_volume(effect_volume)
                sound_effect.play()
        self.ammo_now[self.equipped_weapon][weapon] -= 1  # use 1 ammo per shot
        if self.ammo_now[self.equipped_weapon][weapon] == 0 and \
                self.magazine_count[self.equipped_weapon][weapon] == 0:
            self.ammo_now[self.equipped_weapon].pop(weapon)  # remove weapon with no ammo
            self.magazine_count[self.equipped_weapon].pop(weapon)
            if len(self.ammo_now[self.equipped_weapon]) == 0:  # remove entire set if no ammo at all
                self.ammo_now.pop(self.equipped_weapon)
                self.magazine_count.pop(self.equipped_weapon)
    else:  # TODO maybe use target with range like range attack
        damagesprite.DamageSprite(self, weapon, self.weapon_dmg[weapon],
                                  self.weapon_penetrate[self.equipped_weapon][weapon],
                                  self.equipped_weapon_data[weapon],
                                  self.camera_zoom, attack_type)
        self.weapon_cooldown[weapon] -= self.weapon_speed[weapon]

    self.stamina -= self.weapon_weight[self.equipped_weapon][weapon]
