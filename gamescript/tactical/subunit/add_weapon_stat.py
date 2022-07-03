import statistics


def add_weapon_stat(self):
    """Combine weapon stat, tactical genre uses average stat of all weapon instead of individually so some stat will be
    changed to only one instead of dict of all weapons
    FOR TACTICAL MODE ANY STAT WITH WEAPON IN VARIABLE NAME USE THE FIRST WEAPON IN THE FIRST SET AS MELEE
    AND USE SECOND WEAPON AS RANGE. THE OTHER STAT USE THE FIRST ITEM ONLY (E.G., MAGAZINE)"""
    for damage in self.original_weapon_dmg[0][0]:
        self.original_weapon_dmg[0][0][damage] = [0, 0]
        self.original_weapon_dmg[0][1][damage] = [0, 0]
        self.base_range[0][0] = [0]
        self.arrow_speed[0][0] = [0]
    for set_index, weapon_set in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                                            (self.secondary_main_weapon, self.secondary_sub_weapon))):
        for index, weapon in enumerate(weapon_set):
            weapon_index = set_index + index + 1  # weapon become less effective in secondary set and sub hand weapon
            weapon_stat = self.weapon_data.weapon_list[weapon[0]]
            if weapon_stat["Magazine"] == 0:  # weapon is melee weapon with no magazine to load ammo
                for damage in self.original_weapon_dmg[0][0]:
                    self.original_weapon_dmg[0][0][damage][0] += weapon_stat[damage + " Damage"] * weapon_stat["Damage Balance"] * self.weapon_data.quality[weapon[1]] / weapon_index
                    self.original_weapon_dmg[0][0][damage][1] += weapon_stat[damage + " Damage"] * self.weapon_data.quality[weapon[1]] / weapon_index

                self.weapon_penetrate[0][0] += weapon_stat["Armour Penetration"] * \
                                               self.weapon_data.quality[weapon[1]] / weapon_index
                self.original_weapon_speed[0][0] += weapon_stat["Cooldown"] / weapon_index
            else:
                for damage in self.original_weapon_dmg[0][1]:
                    self.original_weapon_dmg[0][1][damage][0] += weapon_stat[damage + " Damage"] * weapon_stat["Damage Balance"] * self.weapon_data.quality[weapon[1]] / weapon_index
                    self.original_weapon_dmg[0][1][damage][1] += weapon_stat[damage + " Damage"] * self.weapon_data.quality[weapon[1]] / weapon_index
                self.weapon_penetrate[0][1] += weapon_stat["Armour Penetration"] * \
                                               self.weapon_data.quality[weapon[1]] / weapon_index
                self.original_weapon_speed[0][1] += weapon_stat["Cooldown"]
                self.magazine_count[0][0] += weapon_stat["Ammunition"]
                self.magazine_size[0][0] += weapon_stat["Magazine"]
                self.base_range[0][0].append(weapon_stat["Range"] * self.weapon_data.quality[weapon[1]])
                self.arrow_speed[0][0].append(weapon_stat["Travel Speed"])  # travel speed of range melee_attack
            self.base_melee_def += weapon_stat["Defense"] / weapon_index
            self.base_range_def += weapon_stat["Defense"] / weapon_index
            self.skill += weapon_stat["Skill"]
            self.trait["Original"] += self.weapon_data.weapon_list[weapon[0]]["Trait"]
            self.weapon_skill[0][0].append(weapon_stat["Skill"])
            self.weight += weapon_stat["Weight"]

        self.original_weapon_speed[0][0] = int(self.original_weapon_speed[0][0])
        if self.weapon_penetrate[0][0] < 0:  # melee
            self.weapon_penetrate[0][0] = 0  # penetrate cannot be lower than 0
        if self.weapon_penetrate[0][1] < 0:  # range
            self.weapon_penetrate[0][1] = 0

    if len(self.arrow_speed[0][0]) > 1:
        self.arrow_speed[0][0] = statistics.mean(self.arrow_speed[0][0])
    else:
        self.arrow_speed[0][0] = 0
    if len(self.base_range[0][0]) > 1:
        self.base_range[0][0] = statistics.mean(self.base_range[0][0])
    else:
        self.base_range[0][0] = 0

