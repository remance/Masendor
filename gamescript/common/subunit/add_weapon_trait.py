def add_weapon_trait(self):
    """Add trait to base stat"""
    melee_attack_modifier = 1
    melee_def_modifier = 1
    range_def_modifier = 1
    accuracy_modifier = 1
    reload_modifier = 1
    speed_modifier = 1
    charge_modifier = 1

    morale_bonus = 0
    discipline_bonus = 0
    charge_def_bonus = 0
    sight_bonus = 0
    hidden_bonus = 0
    crit_bonus = 0
    mental_bonus = 0
    hp_regen_bonus = 0
    stamina_regen_bonus = 0

    for key in self.trait["Weapon"][self.equipped_weapon]:
        for trait in self.trait["Weapon"][self.equipped_weapon][key].values():
            melee_attack_modifier += trait["Melee Attack Effect"]
            melee_def_modifier += trait["Melee Defence Effect"]
            range_def_modifier += trait["Ranged Defence Effect"]
            speed_modifier += trait["Speed Effect"]
            accuracy_modifier += trait["Accuracy Effect"]
            reload_modifier += trait["Reload Effect"]
            charge_modifier += trait["Charge Effect"]
            charge_def_bonus += trait["Charge Defence Bonus"]
            sight_bonus += trait["Sight Bonus"]
            hidden_bonus += trait["Hidden Bonus"]
            hp_regen_bonus += trait["HP Regeneration Bonus"]
            stamina_regen_bonus += trait["Stamina Regeneration Bonus"]
            morale_bonus += trait["Morale Bonus"]
            discipline_bonus += trait["Discipline Bonus"]
            mental_bonus += trait["Mental Bonus"]
            crit_bonus += trait["Critical Bonus"]

            for element in self.base_element_resistance:
                self.base_element_resistance[element] += trait[element + " Resistance Bonus"]
            self.base_heat_resistance += trait["Heat Resistance Bonus"]
            self.base_cold_resistance += trait["Cold Resistance Bonus"]
            if 0 not in trait["Enemy Status"]:
                for effect in trait["Enemy Status"]:
                    self.base_inflict_status[effect] = trait["Buff Range"]
            for effect in trait["Special Effect"]:  # active weapon special effect
                self.special_effect[self.troop_data.special_effect_list[effect]["Name"]][1][key] = True

    self.base_melee_attack *= melee_attack_modifier
    self.base_melee_def *= melee_def_modifier
    self.base_range_def *= range_def_modifier
    self.base_speed *= speed_modifier
    self.base_accuracy *= accuracy_modifier
    self.base_reload *= reload_modifier
    self.base_charge *= charge_modifier
    self.base_charge_def += charge_def_bonus
    self.base_hp_regen += hp_regen_bonus
    self.base_stamina_regen += stamina_regen_bonus
    self.base_morale += morale_bonus
    self.base_discipline += discipline_bonus
    self.base_crit_effect += crit_bonus
    self.base_mental += mental_bonus
    self.base_sight += sight_bonus
    self.base_hidden += hidden_bonus
