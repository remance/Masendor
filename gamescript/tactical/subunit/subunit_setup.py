import math
import random
import statistics
import numpy as np

import pygame


def add_weapon_stat(self):
    """Combine weapon stat, tactical genre uses average stat of all weapon instead of individually so some stat will be
    changed to only one instead of dict of all weapons"""
    weapon_reload = 0
    base_range = []
    arrow_speed = []
    self.melee_dmg = self.melee_dmg[0][0]
    self.melee_penetrate = self.melee_penetrate[0][0]
    self.weapon_speed = self.weapon_speed[0][0]
    self.range_dmg = self.range_dmg[0][0]
    self.range_penetrate = self.range_penetrate[0][0]
    self.magazine_mod = self.magazine_left[0][0]
    self.magazine_left = 0  # use combined magazine for all weapon
    self.magazine_size = self.magazine_size[0][0]
    self.base_range = self.base_range[0][0]
    for set_index, weapon_set in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                                            (self.secondary_main_weapon, self.secondary_sub_weapon))):
        for index, weapon in enumerate(weapon_set):
            if self.weapon_data.weapon_list[weapon[0]]["Range"] == 0:  # melee weapon if range 0
                self.melee_dmg[0] += self.weapon_data.weapon_list[weapon[0]]["Minimum Damage"] * \
                                     self.weapon_data.quality[weapon[1]] / (index + 1)
                self.melee_dmg[1] += self.weapon_data.weapon_list[weapon[0]]["Maximum Damage"] * \
                                     self.weapon_data.quality[weapon[1]] / (index + 1)

                self.melee_penetrate += self.weapon_data.weapon_list[weapon[0]]["Armour Penetration"] * \
                                        self.weapon_data.quality[weapon[1]] / (index + 1)
                self.weapon_speed += self.weapon_data.weapon_list[weapon[0]]["Speed"] / (index + 1)
            else:
                self.range_dmg[0] += self.weapon_data.weapon_list[weapon[0]]["Minimum Damage"] * \
                                     self.weapon_data.quality[weapon[1]]
                self.range_dmg[1] += self.weapon_data.weapon_list[weapon[0]]["Maximum Damage"] * \
                                     self.weapon_data.quality[weapon[1]]

                self.range_penetrate += self.weapon_data.weapon_list[weapon[0]]["Armour Penetration"] * \
                                        self.weapon_data.quality[weapon[1]] / (index + 1)
                self.magazine_left += self.weapon_data.weapon_list[weapon[0]]["Ammunition"]
                self.magazine_size += self.weapon_data.weapon_list[weapon[0]]["Magazine"]
                weapon_reload += self.weapon_data.weapon_list[weapon[0]]["Speed"] * (index + 1)
                base_range.append(self.weapon_data.weapon_list[weapon[0]]["Range"] * self.weapon_data.quality[weapon[1]])
                arrow_speed.append(self.weapon_data.weapon_list[weapon[0]]["Travel Speed"])  # travel speed of range melee_attack
            self.base_melee_def += self.weapon_data.weapon_list[weapon[0]]["Defense"] / (index + 1)
            self.base_range_def += self.weapon_data.weapon_list[weapon[0]]["Defense"] / (index + 1)
            self.skill += self.weapon_data.weapon_list[weapon[0]]["Skill"]
            self.weapon_skill[set_index][index] = self.weapon_data.weapon_list[weapon[0]]["Skill"][0]  # take only first skill
            self.trait += self.weapon_data.weapon_list[weapon[0]]["Trait"]
            self.weight += self.weapon_data.weapon_list[weapon[0]]["Weight"]

        self.weapon_speed = int(self.weapon_speed)
        if self.melee_penetrate < 0:
            self.melee_penetrate = 0  # melee melee_penetrate cannot be lower than 0
        if self.range_penetrate < 0:
            self.range_penetrate = 0

        if arrow_speed == []:
            self.arrow_speed = 0
        else:
            self.arrow_speed = statistics.mean(arrow_speed)
        if base_range == []:
            self.base_range = 0
        else:
            self.base_range = statistics.mean(base_range)
        self.base_reload = weapon_reload + ((50 - self.base_reload) * weapon_reload / 100)  # final reload speed from weapon and skill


def add_mount_stat(self):
    """Combine mount stat"""
    self.base_charge_def = 25  # charge defence only 25 for cav
    self.base_speed = (
            self.mount["Speed"] + self.mount_grade["Speed Bonus"])  # use mount base speed instead
    self.troop_health += (self.mount["Health Bonus"] * self.mount_grade["Health Effect"]) + \
                         self.mount_armour["Health"]  # Add mount health to the troop health
    self.base_charge += (self.mount["Charge Bonus"] +
                         self.mount_grade["Charge Bonus"])  # Add charge power of mount to troop
    self.base_morale += self.mount_grade["Morale Bonus"]
    self.base_discipline += self.mount_grade["Discipline Bonus"]
    self.stamina += self.mount["Stamina Bonus"]
    self.trait += self.mount["Trait"]  # Apply mount trait to subunit
    self.subunit_type = 2  # If subunit has a mount, count as cav for command buff
    self.feature_mod = "Cavalry"  # Use cavalry type for terrain bonus


def add_trait(self):
    """Add trait to base stat"""
    for trait in self.trait.values():  # add trait modifier to base stat
        self.base_melee_attack *= trait['Melee Attack Effect']
        self.base_melee_def *= trait['Melee Defence Effect']
        self.base_range_def *= trait['Ranged Defence Effect']
        self.base_armour += trait['Armour Bonus']
        self.base_speed *= trait['Speed Effect']
        self.base_accuracy *= trait['Accuracy Effect']
        self.base_range *= trait['Range Effect']
        self.base_reload *= trait['Reload Effect']
        self.base_charge *= trait['Charge Effect']
        self.base_charge_def += trait['Charge Defence Bonus']
        self.base_hp_regen += trait['HP Regeneration Bonus']
        self.base_stamina_regen += trait['Stamina Regeneration Bonus']
        self.base_morale += trait['Morale Bonus']
        self.base_discipline += trait['Discipline Bonus']
        self.crit_effect += trait['Critical Bonus']
        self.elem_res[0] += (trait['Fire Resistance'] / 100)  # percentage, 1 mean perfect resistance, 0 mean none
        self.elem_res[1] += (trait['Water Resistance'] / 100)
        self.elem_res[2] += (trait['Air Resistance'] / 100)
        self.elem_res[3] += (trait['Earth Resistance'] / 100)
        self.magic_res += (trait['Magic Resistance'] / 100)
        self.heat_res += (trait['Heat Resistance'] / 100)
        self.cold_res += (trait['Cold Resistance'] / 100)
        self.elem_res[4] += (trait['Poison Resistance'] / 100)
        self.mental += trait['Mental Bonus']
        if 0 not in trait['Enemy Status']:
            for effect in trait['Enemy Status']:
                self.base_inflict_status[effect] = trait['Buff Range']
        # self.base_elem_melee =
        # self.base_elem_range =

    if 3 in self.trait:  # Varied training
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

    # Change trait variable
    if 16 in self.trait:
        self.arc_shot = True  # can shoot in arc
    if 17 in self.trait:
        self.agile_aim = True  # gain bonus accuracy when shoot while moving
    if 18 in self.trait:
        self.shoot_move = True  # can shoot and move at same time
    if 29 in self.trait:
        self.ignore_charge_def = True  # ignore charge defence completely
    if 30 in self.trait:
        self.ignore_def = True  # ignore defence completely
    if 34 in self.trait:
        self.full_def = True  # full effective defence for all side
    if 33 in self.trait:
        self.backstab = True  # bonus on rear melee_attack
    if 47 in self.trait:
        self.flanker = True  # bonus on flank melee_attack
    if 55 in self.trait:
        self.oblivious = True  # more penalty on flank/rear defend
    if 73 in self.trait:
        self.no_range_penal = True  # no range penalty
    if 74 in self.trait:
        self.long_range_acc = True  # less range penalty
    if 111 in self.trait:
        self.unbreakable = True  # always unbreakable
        self.temp_unbreakable = True
    if 149 in self.trait:  # Impetuous
        self.base_auth_penalty += 0.5
