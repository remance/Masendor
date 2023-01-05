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
            for _ in range(self.shot_per_shoot[self.equipped_weapon][weapon]):
                damagesprite.DamageSprite(self, weapon, self.weapon_dmg[weapon],
                                          self.weapon_penetrate[self.equipped_weapon][weapon],
                                          self.equipped_weapon_data[weapon],
                                          self.shoot_range[weapon], self.zoom, attack_type,
                                          specific_attack_pos=attack_pos)  # Shoot ammo
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
                                  self.shoot_range[weapon], self.zoom, attack_type)

    self.stamina -= self.weapon_weight[self.equipped_weapon][weapon]
