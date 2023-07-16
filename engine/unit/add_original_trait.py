from random import randint


def add_original_trait(self):
    """Add troop preset, race, mount, grade, and armour trait to original stat"""
    melee_attack_bonus = 0
    melee_def_bonus = 0
    range_def_bonus = 0
    accuracy_bonus = 0
    reload_bonus = 0
    speed_bonus = 0
    charge_bonus = 0
    discipline_bonus = 0
    charge_def_bonus = 0
    sight_bonus = 0
    hidden_bonus = 0
    crit_bonus = 0
    hp_regen_bonus = 0
    stamina_regen_bonus = 0

    for trait in self.trait["Original"].values():
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
        discipline_bonus += trait["Discipline Bonus"]
        crit_bonus += trait["Critical Bonus"]

        for element in self.original_element_resistance:
            self.original_element_resistance[element] += trait[element + " Resistance Bonus"]
        self.original_heat_resistance += trait["Heat Resistance Bonus"]
        self.original_cold_resistance += trait["Cold Resistance Bonus"]

        for effect in trait["Special Effect"]:  # trait from sources other than weapon activate permanent special status
            self.special_effect[self.troop_data.special_effect_list[effect]["Name"]][0][0] = True

    random_stat = (95, 105)
    if self.check_special_effect("Varied Training"):  # Varied training more random stat
        random_stat = (70, 120)
        self.original_discipline += randint(-20, 0)
    self.original_melee_attack *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_melee_def *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_range_def *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_melee_dodge *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_range_dodge *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_speed *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_accuracy *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_reload *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_charge *= (randint(random_stat[0], random_stat[1]) / 100)
    self.original_charge_def *= (randint(random_stat[0], random_stat[1]) / 100)

    self.original_melee_attack += melee_attack_bonus
    self.original_melee_def += melee_def_bonus
    self.original_range_def += range_def_bonus
    self.original_melee_dodge += melee_def_bonus
    self.original_range_dodge += range_def_bonus
    self.original_speed += speed_bonus
    self.original_accuracy += accuracy_bonus
    self.original_reload += reload_bonus
    self.original_charge += charge_bonus
    self.original_charge_def += charge_def_bonus
    self.original_hp_regen += hp_regen_bonus
    self.original_stamina_regen += stamina_regen_bonus
    self.original_discipline += discipline_bonus
    self.original_crit_effect += crit_bonus
    self.original_sight += sight_bonus
    self.original_hidden += hidden_bonus
