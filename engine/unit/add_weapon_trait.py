def add_weapon_trait(self):
    """Add trait to base stat"""
    melee_attack_bonus = 0
    melee_def_bonus = 0
    range_def_bonus = 0
    accuracy_bonus = 0
    reload_bonus = 0
    speed_bonus = 0
    charge_bonus = 0
    morale_bonus = 0
    discipline_bonus = 0
    charge_def_bonus = 0
    sight_bonus = 0
    hidden_bonus = 0
    crit_bonus = 0
    hp_regen_bonus = 0
    stamina_regen_bonus = 0

    for key in self.trait["Weapon"][self.equipped_weapon]:
        for trait in self.trait["Weapon"][self.equipped_weapon][key].values():
            melee_attack_bonus += trait["Melee Attack Bonus"]
            melee_def_bonus += trait["Melee Defence Bonus"]
            range_def_bonus += trait["Ranged Defence Bonus"]
            speed_bonus += trait["Speed Bonus"]
            accuracy_bonus += trait["Accuracy Bonus"]
            reload_bonus += trait["Reload Bonus"]
            charge_bonus += trait["Charge Bonus"]
            charge_def_bonus += trait["Charge Defence Bonus"]
            sight_bonus += trait["Sight Bonus"]
            hidden_bonus += trait["Hidden Bonus"]
            hp_regen_bonus += trait["HP Regeneration Bonus"]
            stamina_regen_bonus += trait["Stamina Regeneration Bonus"]
            morale_bonus += trait["Morale Bonus"]
            discipline_bonus += trait["Discipline Bonus"]
            crit_bonus += trait["Critical Bonus"]

            for element in self.base_element_resistance:
                self.base_element_resistance[element] += trait[element + " Resistance Bonus"]
            self.base_heat_resistance += trait["Heat Resistance Bonus"]
            self.base_cold_resistance += trait["Cold Resistance Bonus"]
            for effect in trait["Special Effect"]:  # active weapon special effect
                self.special_effect[self.troop_data.special_effect_list[effect]["Name"]][1][key] = True

    self.base_melee_attack += melee_attack_bonus
    self.base_melee_def += melee_def_bonus
    self.base_range_def += range_def_bonus
    self.base_speed += speed_bonus
    self.base_accuracy += accuracy_bonus
    self.base_reload += reload_bonus
    self.base_charge += charge_bonus
    self.base_charge_def += charge_def_bonus
    self.base_hp_regen += hp_regen_bonus
    self.base_stamina_regen += stamina_regen_bonus
    self.base_morale += morale_bonus
    self.base_discipline += discipline_bonus
    self.base_crit_effect += crit_bonus
    self.base_sight += sight_bonus
    self.base_hidden += hidden_bonus
