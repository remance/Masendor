import random


def add_trait(self):
    """Add trait to base stat"""
    for trait in self.trait.values():  # add trait modifier to base stat
        self.base_melee_attack *= trait["Melee Attack Effect"]
        self.base_melee_def *= trait["Melee Defence Effect"]
        self.base_range_def *= trait["Ranged Defence Effect"]
        self.base_speed *= trait["Speed Effect"]
        self.base_accuracy *= trait["Accuracy Effect"]
        self.base_range *= trait["Range Effect"]
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
        self.heat_resistance += trait["Heat Resistance Bonus"]
        self.cold_resistance += trait["Cold Resistance Bonus"]
        self.mental += trait["Mental Bonus"]
        if 0 not in trait["Enemy Status"]:
            for effect in trait["Enemy Status"]:
                self.base_inflict_status[effect] = trait["Buff Range"]
        for effect in trait["Special Effect"]:  # trait from any source will activate temporary status
            self.special_status[effect][1] = True
        # self.base_elem_melee =
        # self.base_elem_range =

    if True in self.special_status["Varied Training"]:  # Varied training
        self.base_melee_attack *= (random.randint(70, 120) / 100)
        self.base_melee_def *= (random.randint(70, 120) / 100)
        self.base_range_def *= (random.randint(70, 120) / 100)
        self.base_speed *= (random.randint(70, 120) / 100)
        self.base_accuracy *= (random.randint(70, 120) / 100)
        self.base_reload *= (random.randint(70, 120) / 100)
        self.base_charge *= (random.randint(70, 120) / 100)
        self.base_charge_def *= (random.randint(70, 120) / 100)
        self.base_morale += random.randint(-15, 10)
        self.base_discipline += random.randint(-20, 0)
        self.mental += random.randint(-20, 10)

