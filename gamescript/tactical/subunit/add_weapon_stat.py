import statistics


def add_weapon_stat(self):
    """Combine weapon stat, tactical genre uses average stat of all weapon instead of individually so some stat will be
    changed to only one instead of dict of all weapons"""
    weapon_reload = 0
    base_range = []
    arrow_speed = []
    self.melee_dmg = self.melee_dmg[0][0]
    self.melee_penetrate = self.melee_penetrate[0][0]
    self.weapon_speed = self.weapon_speed[0][0]
    self.range_dmg = self.range_dmg[0][0]
    self.range_penetrate = self.range_penetrate[0][0]
    self.magazine_mod = self.magazine_left[0][0]
    self.magazine_left = 0  # use combined magazine for all weapon
    self.magazine_size = self.magazine_size[0][0]
    self.base_range = self.base_range[0][0]
    for set_index, weapon_set in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                                            (self.secondary_main_weapon, self.secondary_sub_weapon))):
        for index, weapon in enumerate(weapon_set):
            if self.weapon_data.weapon_list[weapon[0]]["Range"] == 0:  # melee weapon if range 0
                self.melee_dmg[0] += self.weapon_data.weapon_list[weapon[0]]["Minimum Damage"] * \
                                     self.weapon_data.quality[weapon[1]] / (index + 1)
                self.melee_dmg[1] += self.weapon_data.weapon_list[weapon[0]]["Maximum Damage"] * \
                                     self.weapon_data.quality[weapon[1]] / (index + 1)

                self.melee_penetrate += self.weapon_data.weapon_list[weapon[0]]["Armour Penetration"] * \
                                        self.weapon_data.quality[weapon[1]] / (index + 1)
                self.weapon_speed += self.weapon_data.weapon_list[weapon[0]]["Speed"] / (index + 1)
            else:
                self.range_dmg[0] += self.weapon_data.weapon_list[weapon[0]]["Minimum Damage"] * \
                                     self.weapon_data.quality[weapon[1]]
                self.range_dmg[1] += self.weapon_data.weapon_list[weapon[0]]["Maximum Damage"] * \
                                     self.weapon_data.quality[weapon[1]]

                self.range_penetrate += self.weapon_data.weapon_list[weapon[0]]["Armour Penetration"] * \
                                        self.weapon_data.quality[weapon[1]] / (index + 1)
                self.magazine_left += self.weapon_data.weapon_list[weapon[0]]["Ammunition"]
                self.magazine_size += self.weapon_data.weapon_list[weapon[0]]["Magazine"]
                weapon_reload += self.weapon_data.weapon_list[weapon[0]]["Speed"] * (index + 1)
                base_range.append(self.weapon_data.weapon_list[weapon[0]]["Range"] * self.weapon_data.quality[weapon[1]])
                arrow_speed.append(self.weapon_data.weapon_list[weapon[0]]["Travel Speed"])  # travel speed of range melee_attack
            self.base_melee_def += self.weapon_data.weapon_list[weapon[0]]["Defense"] / (index + 1)
            self.base_range_def += self.weapon_data.weapon_list[weapon[0]]["Defense"] / (index + 1)
            self.skill += self.weapon_data.weapon_list[weapon[0]]["Skill"]
            self.weapon_skill[set_index][index] = self.weapon_data.weapon_list[weapon[0]]["Skill"][0]  # take only first skill
            self.trait += self.weapon_data.weapon_list[weapon[0]]["Trait"]
            self.weight += self.weapon_data.weapon_list[weapon[0]]["Weight"]

        self.weapon_speed = int(self.weapon_speed)
        if self.melee_penetrate < 0:
            self.melee_penetrate = 0  # melee melee_penetrate cannot be lower than 0
        if self.range_penetrate < 0:
            self.range_penetrate = 0

        if not arrow_speed:
            self.arrow_speed = 0
        else:
            self.arrow_speed = statistics.mean(arrow_speed)
        if not base_range:
            self.base_range = 0
        else:
            self.base_range = statistics.mean(base_range)
        self.base_reload = weapon_reload + ((50 - self.base_reload) * weapon_reload / 100)  # final reload speed from weapon and skill
