swap_weapon_command_action = {"name": "SwapGear"}


def swap_weapon(self, new_weapon_set):
    """Change weapon, adjust stat, trait and skill"""
    self.equipped_weapon = new_weapon_set
    self.equipped_weapon_str = str(new_weapon_set)
    if not self.command_action:  # play swap animation if nothing in queue
        self.command_action = swap_weapon_command_action
    self.weapon_cooldown[0] = 0  # reset weapon attack cooldown time
    self.weapon_cooldown[1] = 0

    self.weapon_skill = {}

    # Reset base stat first
    self.base_melee_attack = self.original_melee_attack
    self.base_melee_def = self.original_melee_def
    self.base_range_def = self.original_range_def
    self.base_speed = self.original_speed
    self.base_accuracy = self.original_accuracy
    self.base_sight = self.original_sight
    self.base_hidden = self.original_hidden
    self.base_reload = self.original_reload
    self.base_charge = self.original_charge
    self.base_charge_def = self.original_charge_def

    self.base_mana = self.original_mana
    self.base_morale = self.original_morale
    self.base_discipline = self.original_discipline
    self.base_hp_regen = self.original_hp_regen
    self.base_stamina_regen = self.original_stamina_regen
    self.base_morale_regen = self.original_morale_regen
    self.base_heat_resistance = self.original_heat_resistance
    self.base_cold_resistance = self.original_cold_resistance
    self.base_element_resistance = self.original_element_resistance.copy()
    self.base_mental = self.original_mental
    self.skill = self.original_skill.copy()

    self.equipped_weapon_data = self.weapon_data[self.equipped_weapon]

    self.melee_range = self.original_melee_range[self.equipped_weapon]
    self.melee_def_range = self.original_melee_def_range[self.equipped_weapon]
    self.max_melee_range = self.melee_range[0]
    if self.melee_range[1] > self.max_melee_range:
        self.max_melee_range = self.melee_range[1]
    self.charge_melee_range = self.max_melee_range * 10

    for weapon_index, weapon in enumerate(self.weapon_set[self.equipped_weapon]):
        weapon_stat = self.equipped_weapon_data[weapon_index]
        self.base_melee_def += weapon_stat["Defence"] * (1 + self.troop_data.equipment_grade_list[weapon[1]]["Stat Modifier"])
        self.base_range_def += weapon_stat["Defence"] * (1 + self.troop_data.equipment_grade_list[weapon[1]]["Stat Modifier"])
        if weapon_stat["Skill"]:
            self.skill.append(weapon_stat["Skill"][0])  # take only first skill
            self.weapon_skill[weapon_index] = weapon_stat["Skill"][0]

    self.process_trait_skill()

    self.action_list = []
    for item in self.equipped_weapon_data:
        self.action_list.append(
            {key: value for key, value in item.items() if key in ("Common", "Attack", "Properties")})

    self.equipped_power_weapon = self.power_weapon[self.equipped_weapon]
    self.equipped_block_weapon = self.block_weapon[self.equipped_weapon]
    self.equipped_charge_block_weapon = self.charge_block_weapon[self.equipped_weapon]
    self.equipped_timing_start_weapon = self.timing_start_weapon[self.equipped_weapon]
    self.equipped_timing_end_weapon = self.timing_end_weapon[self.equipped_weapon]
