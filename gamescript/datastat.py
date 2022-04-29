import csv
import os
import re

"""This file contains all class and function that read subunit/leader related data 
and save them into dict for ingame use """


def stat_convert(row, n, i, mod_column=(), list_column=(), tuple_column=(), int_column=(), float_column=()):
    """
    Convert string value to another type
    :param row: row that contains value
    :param n: index of value
    :param i: value
    :param mod_column: list of value header that should be in percentage as decimal value
    :param list_column: list of value header that should be in list type, in case it needs to be modified later
    :param tuple_column: list of value header that should be in tuple type, for value that is static
    :param int_column: list of value header that should be in int number type
    :param float_column: list of value header that should be in float number type
    :return: converted row
    """
    if n in mod_column:
        if i == "":
            row[n] = 1.0
        else:
            row[n] = float(i) / 100  # Need to be float for percentage cal

    elif n in list_column:
        if "," in i:
            if "." in i:
                row[n] = [float(item) if re.search("[a-zA-Z]", item) is None else str(item) for item in i.split(",")]
            else:
                row[n] = [int(item) if item.isdigit() else item for item in i.split(",")]
        elif i.isdigit():
            if "." in i:
                row[n] = [float(i)]
            else:
                row[n] = [int(i)]
        else:
            row[n] = [i]

    elif n in tuple_column:
        if "," in i:
            if "." in i:
                row[n] = tuple([float(item) if re.search("[a-zA-Z]", item) is None else str(item) for item in i.split(",")])
            else:
                row[n] = tuple([int(item) if item.isdigit() else item for item in i.split(",")])
        elif i.isdigit():
            if "." in i:
                row[n] = tuple([float(i)])
            else:
                row[n] = tuple([int(i)])
        else:
            row[n] = tuple([i])

    elif n in int_column:
        if i != "" and re.search("[a-zA-Z]", i) is None:
            row[n] = int(i)
        elif i == "":
            row[n] = 0
    elif n in float_column:
        if i != "" and re.search("[a-zA-Z]", i) is None:
            row[n] = float(i)
        elif i == "":
            row[n] = 0
    else:
        if i == "":
            row[n] = 0
        elif i.isdigit() or (("-" in i or "." in i) and re.search("[a-zA-Z]", i) is None) or i == "inf":
            row[n] = float(i)
    return row


class WeaponData:
    def __init__(self, main_dir, images, ruleset):
        """Weapon has melee_dmg, penetration and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.images = list(images.values())
        self.weapon_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_weapon.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Cost", "ImageID", "Speed", "Hand")  # value int only
            list_column = ("Skill", "Trait")  # value in list only
            tuple_column = ("Ruleset",)  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row_index, row in enumerate(rd):
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, list_column=list_column,
                                               tuple_column=tuple_column, int_column=int_column)
                    self.weapon_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75)  # Quality modifier to weapon stat


class ArmourData:
    def __init__(self, main_dir, images, ruleset):
        """Armour has base defence and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.images = images
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
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                               int_column=int_column)
                    self.armour_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75)  # Quality modifier to armour stat


class TroopData:
    def __init__(self, main_dir, ruleset, ruleset_folder):
        """Unit stat data read"""
        # v Troop stat dict
        self.troop_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "troop", "troop_preset.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Grade", "Race", "Cost", "Upkeep", "Troop", "Troop Class", "Size")  # value int only
            list_column = ("Trait", "Skill",)  # value in list only
            tuple_column = ("Armour", "Primary Main Weapon", "Primary Sub Weapon", "Secondary Main Weapon",
                            "Secondary Sub Weapon", "Mount", "Role", "Ruleset")  # value in tuple only
            mod_column = ("Ammunition Modifier",)
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for row_index, row in enumerate(rd):
                if row_index > 0:  # skip convert header row
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                           tuple_column=tuple_column, int_column=int_column)
                    self.troop_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Lore of the troop
        self.troop_lore = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "troop", "troop_lore.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.troop_lore[row[0]] = row[1:]
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
                self.troop_sprite_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Troop status effect dict
        self.status_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_status.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Temperature Change"]  # value int only
            tuple_column = ["Special Effect", "Status Conflict", "Ruleset"]  # value in tuple only
            mod_column = ["Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect", "Armour Effect",
                          "Speed Effect", "Accuracy Effect", "Reload Effect",
                          "Charge Effect"]  # need to be calculated to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column,
                                               int_column=int_column)
                    self.status_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Race dict
        self.race_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_race.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("Size", "Armour", "Speed")  # value int only
            list_column = ("Trait",)  # value in list only
            tuple_column = ("Ruleset",)  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd):
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                               int_column=int_column)
                    self.race_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
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
                          "Speed Effect", "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                for n, i in enumerate(row):
                    if index != 0:
                        row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                           int_column=int_column)
                self.grade_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Troop skill dict
        self.skill_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_skill.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Troop Type", "Type", "Area of Effect", "Element", "Cost")  # value int only
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
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        if index != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                               tuple_column=tuple_column, int_column=int_column)
                    self.skill_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Troop trait dict
        self.trait_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_trait.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Buff Range", "Race", "Cost", "Element")  # value int only
            tuple_column = ("Status", "Special Effect", "Enemy Status", "Ruleset")  # value in tuple only
            mod_column = ("Buff Modifier", "Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect",
                          "Speed Effect", "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Siege Effect", "Supply Effect", "Upkeep Effect")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd):
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]

                if any(rule in ("0", str(ruleset), "Ruleset") for rule in this_ruleset):
                    for n, i in enumerate(row):
                        if index != 0:
                            row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column,
                                               int_column=int_column)
                    self.trait_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Troop role dict
        self.role = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_class.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.role[row[0]] = row[1:]
        edit_file.close()

        # Troop mount dict
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
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset) and row_index > 0:  # only grab effect that existed in the ruleset and first row
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, tuple_column=tuple_column, list_column=list_column,
                                           int_column=int_column)
                    self.mount_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
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
                        row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                self.mount_grade_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
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
                if "," in row[-2]:  # make str with , into list
                    this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    this_ruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in
                       this_ruleset):  # only grab effect that existed in the ruleset and first row
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                        self.mount_armour_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()


class LeaderData:
    def __init__(self, main_dir, images, image_order, ruleset_folder):
        self.images = images
        self.image_order = image_order
        self.leader_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", str(ruleset_folder), "leader", "leader.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Race", "Melee Command", "Range Command", "Cavalry Command", "Combat", "Social Class",
                          "Forcedimageid", "Faction")  # value int only
            list_column = ("Skill", "Trait")
            tuple_column = ("Primary Main Weapon", "Primary Sub Weapon", "Secondary Main Weapon", "Secondary Sub Weapon",
                           "Armour", "Mount")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.leader_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Add common leader to the leader list with game_id + 10000
        with open(os.path.join(main_dir, "data", "ruleset", str(ruleset_folder), "leader", "common_leader.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ("ID", "Race", "Melee Command", "Range Command", "Cavalry Command", "Combat", "Social Class",
                          "Forcedimageid", "Faction")  # value int only
            list_column = ("Skill", "Trait")
            tuple_column = ("Primary Main Weapon", "Primary Sub Weapon", "Secondary Main Weapon",
                            "Secondary Sub Weapon", "Armour", "Mount")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.leader_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Lore of the leader dict
        self.leader_lore = {}
        with open(os.path.join(main_dir, "data", "ruleset", str(ruleset_folder), "leader", "leader_lore.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.leader_lore[row[0]] = row[1:]
            edit_file.close()

        # Leader sprite
        self.leader_sprite_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "leader", "leader_sprite.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row_index, row in enumerate(rd):
                self.leader_sprite_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        self.common_leader_sprite_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "leader", "common_leader_sprite.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row_index, row in enumerate(rd):
                self.common_leader_sprite_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Leader class dict
        self.leader_class = {}
        with open(os.path.join(main_dir, "data", "leader", "leader_class.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
                        row[n] = int(i)
                self.leader_class[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()


class FactionData:
    images = []
    main_dir = None

    def __init__(self, ruleset_folder):
        """Unit stat data read"""
        self.faction_list = {}
        with open(os.path.join(self.main_dir, "data", "ruleset", ruleset_folder, "faction", "faction.csv"), encoding="utf-8",
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
                self.faction_list[row[0]] = {header[index+1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()
        self.faction_name_list = [item["Name"] for item in self.faction_list.values()][1:]