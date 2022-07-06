import random


def add_original_trait(self):
    """Add troop preset, race, mount, grade, and armour trait to original stat"""
    for trait in self.trait["Original"].values():
        self.original_melee_attack *= trait["Melee Attack Effect"]
        self.original_melee_def *= trait["Melee Defence Effect"]
        self.original_range_def *= trait["Ranged Defence Effect"]
        self.original_speed *= trait["Speed Effect"]
        self.original_accuracy *= trait["Accuracy Effect"]
        self.original_reload *= trait["Reload Effect"]
        self.original_charge *= trait["Charge Effect"]
        self.original_charge_def += trait["Charge Defence Bonus"]
        self.original_hp_regen += trait["HP Regeneration Bonus"]
        self.original_stamina_regen += trait["Stamina Regeneration Bonus"]
        self.original_morale += trait["Morale Bonus"]
        self.original_discipline += trait["Discipline Bonus"]
        self.crit_effect += trait["Critical Bonus"]
        for element in self.original_element_resistance:
            self.original_element_resistance[element] += trait[element + " Resistance Bonus"]
        self.original_heat_resistance += trait["Heat Resistance Bonus"]
        self.original_cold_resistance += trait["Cold Resistance Bonus"]
        self.original_mental += trait["Mental Bonus"]
        if 0 not in trait["Enemy Status"]:
            for effect in trait["Enemy Status"]:
                self.original_inflict_status[effect] = trait["Buff Range"]
        for effect in trait["Special Effect"]:  # trait from any source will activate temporary status
            self.special_effect[self.troop_data.special_effect_list[effect]["Name"]][0][0] = True

    if self.special_effect_check("Varied Training"):  # Varied training
        self.original_melee_attack *= (random.randint(70, 120) / 100)
        self.original_melee_def *= (random.randint(70, 120) / 100)
        self.original_range_def *= (random.randint(70, 120) / 100)
        self.original_speed *= (random.randint(70, 120) / 100)
        self.original_accuracy *= (random.randint(70, 120) / 100)
        self.original_reload *= (random.randint(70, 120) / 100)
        self.original_charge *= (random.randint(70, 120) / 100)
        self.original_charge_def *= (random.randint(70, 120) / 100)
        self.original_morale += random.randint(-15, 10)
        self.original_discipline += random.randint(-20, 0)
        self.original_mental += random.randint(-20, 10)

