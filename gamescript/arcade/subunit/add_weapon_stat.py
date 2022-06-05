
def add_weapon_stat(self):
    """Combine weapon stat"""
    for set_index, weapon_set in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                                            (self.secondary_main_weapon, self.secondary_sub_weapon))):
        for index, weapon in enumerate(weapon_set):
            self.weapon_speed = self.weapon_data.weapon_list[weapon[0]]["Speed"]
            if self.weapon_data.weapon_list[weapon[0]]["Magazine"] == 0:  # melee weapon if no magazine to load ammo
                self.melee_dmg[set_index][index][0] = self.weapon_data.weapon_list[weapon[0]]["Minimum Damage"] * \
                                           self.weapon_data.quality[weapon[1]]
                self.melee_dmg[set_index][index][1] = self.weapon_data.weapon_list[weapon[0]]["Maximum Damage"] * \
                                           self.weapon_data.quality[weapon[1]]

                self.melee_penetrate[set_index][index] = self.weapon_data.weapon_list[weapon[0]]["Armour Penetration"] * \
                                              self.weapon_data.quality[weapon[1]]
            else:
                self.range_dmg[set_index][index][0] = self.weapon_data.weapon_list[weapon[0]]["Minimum Damage"] * \
                                           self.weapon_data.quality[weapon[1]]
                self.range_dmg[set_index][index][1] = self.weapon_data.weapon_list[weapon[0]]["Maximum Damage"] * \
                                           self.weapon_data.quality[weapon[1]]

                self.range_penetrate[set_index][index] = self.weapon_data.weapon_list[weapon[0]]["Armour Penetration"] * \
                                              self.weapon_data.quality[weapon[1]]
                self.magazine_left[set_index][index] *= self.weapon_data.weapon_list[weapon[0]]["Ammunition"]
                self.magazine_size[set_index][index] = self.weapon_data.weapon_list[weapon[0]][
                    "Magazine"]  # can shoot how many times before have to reload
                self.base_range[set_index][index] = self.weapon_data.weapon_list[weapon[0]]["Range"] * self.weapon_data.quality[weapon[1]]
                self.arrow_speed[set_index][index] = self.weapon_data.weapon_list[weapon[0]]["Travel Speed"]  # travel speed of range melee_attack

            self.weight += self.weapon_data.weapon_list[weapon[0]]["Weight"]
            self.weapon_skill[set_index][index] = self.weapon_data.weapon_list[weapon[0]]["Skill"][0]  # take only first skill
