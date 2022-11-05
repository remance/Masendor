"""This file contains all class and function that read subunit/leader related data
and save them into dict for ingame use """

import csv
import os
import re
from pathlib import Path

import numpy as np
from gamescript.common import utility

stat_convert = utility.stat_convert
load_images = utility.load_images
lore_csv_read = utility.lore_csv_read


class TroopData:
    def __init__(self, main_dir, weapon_icon_images, ruleset, ruleset_folder, language):
        """
        For keeping all data related to troop.
        :param main_dir: Game folder direction
        :param ruleset: Current ruleset of the game
        :param ruleset_folder: Folder name of the ruleset
        """
        self.weapon_icon = tuple(weapon_icon_images.values())

        # Troop stat dict
        self.troop_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "troop", "troop_preset.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = (
            "ID", "Grade", "Race", "Cost", "Upkeep", "Troop", "Troop Class", "Sprite ID")  # value int only
            list_column = ("Trait", "Skill",)  # value in list only
            tuple_column = ("Armour", "Primary Main Weapon", "Primary Sub Weapon", "Secondary Main Weapon",
                            "Secondary Sub Weapon", "Mount", "Role", "Ruleset")  # value in tuple only
            percent_column = ("Ammunition Modifier",)
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            percent_column = [index for index, item in enumerate(header) if item in percent_column]
            for row_index, row in enumerate(rd):
                if row_index > 0:  # skip convert header row
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, percent_column=percent_column, list_column=list_column,
                                           tuple_column=tuple_column, int_column=int_column)
                    self.troop_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Lore of the troop
        self.troop_lore = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "troop",
                               "troop_lore" + "_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.troop_lore)
            edit_file.close()

        # Troop sprite
        self.troop_sprite_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "troop", "troop_sprite.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row_index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if "," in i:
                        row[n] = i.split(",")
                self.troop_sprite_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Troop status effect dict
        self.status_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_status.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Max Stack", "Temperature Change", "Physical Resistance Bonus",
                          "Fire Resistance Bonus", "Water Resistance Bonus",
                          "Air Resistance Bonus", "Earth Resistance Bonus", "Magic Resistance Bonus",
                          "Heat Resistance Bonus", "Cold Resistance Bonus", "Poison Resistance Bonus"]  # value int only
            tuple_column = ["Special Effect", "Status Conflict", "Ruleset"]  # value in tuple only
            mod_column = ["Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect",
                          "Speed Effect", "Accuracy Effect", "Reload Effect",
                          "Charge Effect"]  # need to be calculated to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column,
                                               int_column=int_column, true_empty=True)
                    self.status_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.status_lore = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_status_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.status_lore)
        edit_file.close()

        # Troop special status effect dict
        self.special_effect_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_special_effect.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID"]  # value int only
            tuple_column = ["Status"]  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if index != 0:  # Skip first row header
                        row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column, true_empty=True)
                self.special_effect_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Race dict
        self.race_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_race.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("Strength", "Dexterity", "Agility", "Constitution", "Intelligence", "Wisdom",
                          "Physical Resistance", "Fire Resistance", "Water Resistance", " Air Resistance",
                          "Earth Resistance", "Poison Resistance", "Magic Resistance", "Size")  # value int only
            list_column = ("Trait",)  # value in list only
            tuple_column = ("Ruleset", "Special Hair Part", "Special Body Part")  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                               int_column=int_column, true_empty=True)
                    self.race_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Troop grade dict
        self.grade_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_grade.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID",)  # value int only
            list_column = ("Trait",)  # value in list only
            mod_column = ("Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect",
                          "Speed Effect", "Accuracy Effect", "Reload Effect", "Charge Effect")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if index != 0:
                        row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                           int_column=int_column, true_empty=True)
                self.grade_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Troop skill dict
        self.skill_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_skill.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Troop Type", "Type", "Area of Effect", "Cost", "Charge Skill")  # value int only
            list_column = ("Action",)
            tuple_column = ("Status", "Restriction", "Condition", "Enemy Status", "Ruleset")  # value in tuple only
            mod_column = ("Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect", "Speed Effect",
                          "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Critical Effect", "Damage Effect")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                               tuple_column=tuple_column, int_column=int_column, true_empty=True)
                    self.skill_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.skill_lore = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_skill_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.skill_lore)
        edit_file.close()

        # Troop trait dict
        self.trait_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_trait.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Buff Range", "Race", "Cost", "Element")  # value int only
            tuple_column = ("Status", "Special Effect", "Enemy Status", "Ruleset")  # value in tuple only
            percent_column = ("Buff Modifier",)
            mod_column = ("Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect",
                          "Speed Effect", "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Siege Effect", "Supply Effect", "Upkeep Effect")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            percent_column = [index for index, item in enumerate(header) if item in percent_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]

                if any(rule in ("0", str(ruleset), "Ruleset") for rule in this_ruleset):
                    for n, i in enumerate(row):
                        if index != 0:
                            row = stat_convert(row, n, i, percent_column=percent_column, mod_column=mod_column,
                                               tuple_column=tuple_column, int_column=int_column, true_empty=True)
                    self.trait_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.trait_lore = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_trait_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.trait_lore)
        edit_file.close()

        # Troop role dict
        self.role = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_class_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.role[row[0]] = row[1:]
        edit_file.close()

        # Equipment grade dict
        self.equipment_grade_list = {}
        with open(os.path.join(main_dir, "data", "troop", "equipment_grade.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID",)  # value int only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            for index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if index != 0:
                        row = stat_convert(row, n, i, int_column=int_column)
                self.equipment_grade_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Weapon dict
        self.weapon_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_weapon.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Strength Bonus Scale", "Dexterity Bonus Scale", "Physical Damage",
                          "Fire Damage", "Water Damage", "Air Damage", "Earth Damage", "Poison Damage", "Magic Damage",
                          "Armour Penetration", "Defence", "Weight", "Speed", "Ammunition", "Magazine", "Shot Number",
                          "Range", "Travel Speed", "Learning Difficulty", "Mastery Difficulty", "Learning Difficulty",
                          "Cost", "ImageID", "Speed", "Hand")  # value int only
            list_column = ("Skill", "Trait", "Properties")  # value in list only
            tuple_column = ("Bullet", "Ruleset")  # value in tuple only
            percent_column = ("Damage Balance",)
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            percent_column = [index for index, item in enumerate(header) if item in percent_column]
            for row_index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, percent_column=percent_column, list_column=list_column,
                                               tuple_column=tuple_column, int_column=int_column, true_empty=True)
                    self.weapon_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.weapon_lore = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_weapon_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.weapon_lore)
        edit_file.close()

        # Armour dict
        self.armour_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_armour.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Cost")  # value int only
            list_column = ("Trait",)  # value in list only
            tuple_column = ("Ruleset",)  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row_index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                               int_column=int_column, true_empty=True)
                    self.armour_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.armour_lore = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_armour_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.armour_lore)
        edit_file.close()

        # Mount dict
        self.mount_list = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_preset.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Cost")  # value int only
            list_column = ("Trait",)  # value in list only
            tuple_column = ("Ruleset",)  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row_index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset) and row_index > 0:  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, tuple_column=tuple_column, list_column=list_column,
                                           int_column=int_column, true_empty=True)
                    self.mount_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.mount_lore = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_preset_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.mount_lore)
        edit_file.close()

        # Mount grade dict
        self.mount_grade_list = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_grade.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID",)  # value int only
            list_column = ("Trait",)  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            for index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if index != 0:
                        row = stat_convert(row, n, i, list_column=list_column, int_column=int_column, true_empty=True)
                self.mount_grade_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Mount armour dict
        self.mount_armour_list = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_armour.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Cost")  # value int only
            tuple_column = ("Ruleset")  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            self.mount_armour_list_header = {k: v for v, k in enumerate(header[1:])}
            for row_index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column,
                                               true_empty=True)
                        self.mount_armour_list[row[0]] = {header[index + 1]: stuff for index, stuff in
                                                          enumerate(row[1:])}
        edit_file.close()

        self.mount_armour_lore = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_armour_lore_" + language + ".csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            for index, row in enumerate(rd):
                if row[0] in self.mount_armour_list:  # keep only active mount armour in ruleset
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                    self.mount_armour_lore[row[0]] = [stuff for index, stuff in enumerate(row[1:])]
        edit_file.close()

        # Unit formation dict
        self.default_unit_formation_list = {}
        part_folder = Path(os.path.join(main_dir, "data", "troop", "formation"))
        subdirectories = [os.sep.join(os.path.normpath(x).split(os.sep)[-1:]) for x in
                          part_folder.iterdir() if x.is_dir() is False]
        for folder in subdirectories:
            formation_name = folder.replace(".csv", "")
            self.default_unit_formation_list[formation_name] = []
            with open(os.path.join(main_dir, "data", "troop", "formation", folder), encoding="utf-8",
                      mode="r") as edit_file:
                rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
                rd = [row for row in rd]
                for index, row in enumerate(rd):
                    if any(re.search("[a-zA-Z]", i) is not None for i in
                           row) is False:  # row does not contain any text, not header
                        row = [int(item) if item != "" else 100 for item in
                               row]  # replace empty item with high number for low priority
                        self.default_unit_formation_list[formation_name].append(row)
            self.default_unit_formation_list[formation_name] = np.array(
                self.default_unit_formation_list[formation_name])
        edit_file.close()
        self.unit_formation_list = {}  # list of unit formation after change size, get added later when change genre and ruleset


class LeaderData:
    def __init__(self, main_dir, images, ruleset, ruleset_folder, language):
        """
        For keeping all data related to leader.
        :param main_dir: Game folder direction
        :param images: Portrait images of leaders
        :param ruleset_folder: Folder name of the ruleset
        """
        self.images = images
        self.leader_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", str(ruleset_folder), "leader", "leader.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Race", "Strength", "Dexterity", "Agility", "Constitution", "Intelligence",
                          "Wisdom", "Charisma", "Melee Speciality", "Range Speciality", "Cavalry Speciality",
                          "Social Class", "Faction", "Sprite ID")  # value int only
            list_column = ("Skill", "Trait", "Formation")
            tuple_column = ("Primary Main Weapon", "Primary Sub Weapon", "Secondary Main Weapon",
                            "Secondary Sub Weapon", "Armour", "Mount")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column, true_empty=True)
                self.leader_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Add common leader to the leader list with game_id 10000+
        with open(os.path.join(main_dir, "data", "ruleset", str(ruleset_folder), "leader", "common_leader.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column, true_empty=True)
                self.leader_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.skill_list = {}
        with open(os.path.join(main_dir, "data", "leader", "leader_skill.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("Troop Type", "Type", "Range", "Area of Effect", "Element", "Cost")  # value int only
            list_column = ("Action",)
            tuple_column = ("Status", "Restriction", "Condition", "Enemy Status", "Ruleset")  # value in tuple only
            mod_column = ("Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect", "Speed Effect",
                          "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Critical Effect", "Damage Effect")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                               tuple_column=tuple_column, int_column=int_column, true_empty=True)
                    self.skill_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        self.skill_lore = {}
        with open(os.path.join(main_dir, "data", "leader", "leader_skill_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            for index, row in enumerate(rd):
                if row[0] in self.skill_list:  # keep only active skill in ruleset
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                    self.skill_lore[row[0]] = [stuff for index, stuff in enumerate(row[1:])]
        edit_file.close()

        self.commander_skill_list = {}
        with open(os.path.join(main_dir, "data", "leader", "commander_skill.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("Troop Type", "Type", "Area of Effect", "Element", "Cost")  # value int only
            list_column = ("Action", "Replace")
            tuple_column = ("Status", "Restriction", "Condition", "Enemy Status", "Ruleset")  # value in tuple only
            mod_column = ("Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect", "Speed Effect",
                          "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Critical Effect", "Damage Effect")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                if "," in row[-1]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-1].split(",")]
                else:
                    this_ruleset = [row[-1]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                               tuple_column=tuple_column, int_column=int_column, true_empty=True)
                    self.commander_skill_list[row[0]] = {header[index + 1]: stuff for index, stuff in
                                                         enumerate(row[1:])}
        edit_file.close()

        # Lore of the leader dict
        self.leader_lore = {}
        for leader_file in ("leader_lore", "common_leader_lore"):  # merge leader and common leader lore together
            with open(os.path.join(main_dir, "data", "ruleset", str(ruleset_folder), "leader",
                                   leader_file + "_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
                lore_csv_read(edit_file, self.leader_lore)
                edit_file.close()

        # Leader sprite
        self.leader_sprite_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "leader", "leader_sprite.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row_index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if "," in i:
                        row[n] = i.split(",")
                self.leader_sprite_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        self.common_leader_sprite_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "leader", "common_leader_sprite.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row_index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if "," in i:
                        row[n] = i.split(",")
                self.common_leader_sprite_list[row[0]] = {header[index + 1]: stuff for index, stuff in
                                                          enumerate(row[1:])}
            edit_file.close()

        # Leader class dict
        self.leader_class = {}
        with open(os.path.join(main_dir, "data", "leader", "leader_class.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
                        row[n] = int(i)
                self.leader_class[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()


class FactionData:
    images = []

    def __init__(self, main_dir, ruleset_folder, screen_scale, language):
        """
        For keeping all data related to leader.
        :param main_dir: Game folder direction
        :param ruleset_folder: Folder name of the ruleset
        :param screen_scale: scale of screen resolution
        """
        self.faction_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "faction", "faction.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    if n in (2, 3):
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.faction_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        self.faction_lore = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "faction",
                               "faction_lore_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            lore_csv_read(edit_file, self.faction_lore)
            edit_file.close()

        images_old = load_images(main_dir, screen_scale, ("ruleset", ruleset_folder, "faction", "coa"),
                                 load_order=False)  # coa_list images list
        self.coa_list = []
        for image in images_old:
            self.coa_list.append(images_old[image])
