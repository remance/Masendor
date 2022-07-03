def swap_weapon(self):
    """Change weapon, adjust stat, trait and skill"""
    self.weapon_cooldown[0] = 0  # reset reload time
    self.weapon_cooldown[1] = 0

    # Reset base stat first
    self.base_melee_attack = self.original_melee_attack
    self.base_melee_def = self.original_melee_def
    self.base_range_def = self.original_range_def
    self.heat_resistance = self.original_heat_resistance
    self.cold_resistance = self.original_cold_resistance
    self.skill = self.original_skill
    self.trait["Weapon"] = {0: (), 1: ()}
    for index, weapon_set in enumerate(((self.primary_main_weapon, self.primary_sub_weapon), (self.secondary_main_weapon, self.secondary_sub_weapon))):
        for weapon_index, weapon in enumerate(weapon_set):
            weapon_stat = self.weapon_data.weapon_list[weapon[0]]
            if index == self.equipped_weapon:
                self.base_melee_def += weapon_stat["Defense"] * self.weapon_data.quality[weapon[1]]
                self.base_range_def += weapon_stat["Defense"] * self.weapon_data.quality[weapon[1]]
                self.trait["Weapon"][weapon_index] = weapon_stat["Trait"]
                skill = self.weapon_skill[weapon_set][weapon]
                if skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] != 0 and
                                   self.troop_data.skill_list[skill]["Troop Type"] != self.subunit_type + 1):
                    self.weapon_skill[weapon_set][weapon] = 0  # remove unmatch class skill
                else:
                    self.skill.append(skill)

    self.process_trait_skill()

    self.action_list = {key: value for key, value in self.generic_action_data.items() if
                        key in self.weapon_name[self.equipped_weapon]}

