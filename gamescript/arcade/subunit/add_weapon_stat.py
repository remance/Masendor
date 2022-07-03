
def add_weapon_stat(self):
    self.melee_weapon_set = {0: 0, 1: 0}
    self.range_weapon_set = {0: 0, 1: 0}
    for set_index, weapon_set in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                                            (self.secondary_main_weapon, self.secondary_sub_weapon))):
        for index, weapon in enumerate(weapon_set):
            weapon_stat = self.weapon_data.weapon_list[weapon[0]]
            self.original_weapon_speed[set_index][index] = weapon_stat["Speed"]
            for damage in self.original_weapon_dmg:
                self.original_weapon_dmg[damage] = (
                weapon_stat[damage + " Damage"] * weapon_stat["Damage Balance"] * self.weapon_data.quality[weapon[1]],
                weapon_stat[damage + " Damage"] * self.weapon_data.quality[weapon[1]])
            self.weapon_penetrate[set_index][index] = weapon_stat["Armour Penetration"] * \
                                                      self.weapon_data.quality[weapon[1]]

            if weapon_stat["Magazine"] == 0:  # weapon is melee weapon with no magazine to load ammo
                self.melee_weapon_set[set_index] += set_index  # add weapon set to melee set
            else:
                self.magazine_count[set_index][index] *= weapon_stat["Ammunition"]
                self.magazine_size[set_index][index] = weapon_stat[
                    "Magazine"]  # can shoot how many times before have to reload
                self.base_range[set_index][index] = weapon_stat["Range"] * self.weapon_data.quality[weapon[1]]
                self.arrow_speed[set_index][index] = weapon_stat["Travel Speed"]  # travel speed of range melee_attack

                self.range_weapon_set[set_index] += set_index  # add weapon set to range set

            self.original_weapon_speed[set_index][index] = weapon_stat["Cooldown"]
            self.weight += weapon_stat["Weight"]
            self.weapon_skill[set_index][index] = weapon_stat["Skill"][0]  # take only first skill
    # Sort higher damage priority
    self.melee_weapon_set = dict(sorted(self.melee_weapon_set.items(), key=lambda x: x[1], reverse=True))
    self.range_weapon_set = dict(sorted(self.range_weapon_set.items(), key=lambda x: x[1], reverse=True))

    # Keep only set with damage
    self.melee_weapon_set = {key: value for key, value in self.melee_weapon_set.items() if value > 0}
    self.range_weapon_set = {key: value for key, value in self.range_weapon_set.items() if value > 0}

    # Convert to list
    self.melee_weapon_set = [key for key in self.melee_weapon_set]
    self.range_weapon_set = [key for key in self.range_weapon_set]
