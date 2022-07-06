def add_weapon_trait(self):
    """Add trait to base stat"""
    for key in self.trait["Weapon"][self.equipped_weapon]:
        for trait in self.trait["Weapon"][self.equipped_weapon][key].values():
            self.base_melee_attack *= trait["Melee Attack Effect"]
            self.base_melee_def *= trait["Melee Defence Effect"]
            self.base_range_def *= trait["Ranged Defence Effect"]
            self.base_speed *= trait["Speed Effect"]
            self.base_accuracy *= trait["Accuracy Effect"]
            self.base_reload *= trait["Reload Effect"]
            self.base_charge *= trait["Charge Effect"]
            self.base_charge_def += trait["Charge Defence Bonus"]
            self.base_hp_regen += trait["HP Regeneration Bonus"]
            self.base_stamina_regen += trait["Stamina Regeneration Bonus"]
            self.base_morale += trait["Morale Bonus"]
            self.base_discipline += trait["Discipline Bonus"]
            self.crit_effect += trait["Critical Bonus"]
            for element in self.base_element_resistance:
                self.base_element_resistance[element] += trait[element + " Resistance Bonus"]
            self.base_heat_resistance += trait["Heat Resistance Bonus"]
            self.base_cold_resistance += trait["Cold Resistance Bonus"]
            self.base_mental += trait["Mental Bonus"]
            if 0 not in trait["Enemy Status"]:
                for effect in trait["Enemy Status"]:
                    self.base_inflict_status[effect] = trait["Buff Range"]
            for effect in trait["Special Effect"]:  # active weapon special effect
                self.special_effect[self.troop_data.special_effect_list[effect]["Name"]][1][key] = True


