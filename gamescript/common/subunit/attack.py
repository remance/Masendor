import pygame

from gamescript import damagesprite


def attack(self, attack_type):
    weapon = int(self.current_action["name"][-1])
    attack_pos = None
    if "pos" in self.current_action:  # manual attack position
        attack_pos = self.current_action["pos"]
    elif self.attack_pos is not None:
        attack_pos = self.attack_pos
    if attack_type == "range":
        if attack_pos is not None or self.attack_target is not None:
            equipped_weapon_data = self.equipped_weapon_data[weapon]
            for _ in range(self.shot_per_shoot[self.equipped_weapon][weapon]):  # Shoot ammo
                damagesprite.DamageSprite(self, weapon, self.weapon_dmg[weapon],
                                          self.weapon_penetrate[self.equipped_weapon][weapon],
                                          equipped_weapon_data, self.shoot_range[weapon], self.camera_zoom, attack_type,
                                          specific_attack_pos=attack_pos, arc_shot=self.current_action["arc shot"])
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

                print(effect_volume, equipped_weapon_data["Sound Distance"], self.battle.play_effect_volume,
                      sound_distance, self.base_pos, self.battle.true_camera_pos, self.camera_zoom)
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
    else:
        damagesprite.DamageSprite(self, weapon, self.weapon_dmg[weapon],
                                  self.weapon_penetrate[self.equipped_weapon][weapon],
                                  self.equipped_weapon_data[weapon],
                                  self.shoot_range[weapon], self.camera_zoom, attack_type)

    self.stamina -= self.weapon_weight[self.equipped_weapon][weapon]
