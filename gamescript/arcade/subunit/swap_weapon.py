def swap_weapon(self):
    """Change weapon, adjust stat, trait and skill"""
    self.base_melee_def = self.original_melee_def
    self.base_range_def = self.original_range_def
    self.trait = self.original_trait
    self.skill = self.original_skill
    for weapon_index, weapon in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                                           (self.secondary_main_weapon, self.secondary_sub_weapon))[self.equipped_weapon]):
        print(self.name, weapon)
        self.base_melee_def += self.weapon_data.weapon_list[weapon[0]]["Defense"]
        self.base_range_def += self.weapon_data.weapon_list[weapon[0]]["Defense"]
        self.skill += self.weapon_data.weapon_list[weapon[0]]["Skill"]
        self.trait += self.weapon_data.weapon_list[weapon[0]]["Trait"]
    self.process_trait_skill()

    self.action_list = {key: value for key, value in self.generic_action_data.items() if
                        key in self.weapon_name[self.equipped_weapon]}
