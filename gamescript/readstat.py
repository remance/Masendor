import csv
import re
import os

"""This file contains all class and function that read subunit/leader related data and save them into dict for ingame use"""

def stat_convert(row, n, i, mod_column=[], list_column=[], int_column=[]):
    if mod_column != [] and n in mod_column:
        if i == "":
            row[n] = 1.0
        else:
            row[n] = float(i) / 100  # Need to be float for percentage cal

    elif list_column != [] and n in list_column:
        if "," in i:
            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
        elif i.isdigit():
            row[n] = [int(i)]

    elif int_column != [] and n in int_column:
        if i != "" and re.search("[a-zA-Z]", i) is None:
            row[n] = int(i)
        elif i == "":
            row[n] = 0
    else:
        if i == "":
            row[n] = 0
        elif i.isdigit() or (("-" in i or "." in i) and re.search("[a-zA-Z]", i) is None) or i == "inf":
            row[n] = float(i)
    return row

class Weaponstat:
    def __init__(self, main_dir, img, ruleset):
        """Weapon has dmg, penetration and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.weapon_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_weapon.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost", "ImageID", "Speed"]  # value int only
            list_column = ["Trait", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            self.weapon_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                    self.weapon_list[row[0]] = row[1:]
        unitfile.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75)  # Quality modifer to weapon stat


class Armourstat:
    def __init__(self, main_dir, img, ruleset):
        """Armour has base defence and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.armour_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_armour.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost"]  # value int only
            list_column = ["Trait", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            self.armour_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                    self.armour_list[row[0]] = row[1:]
        unitfile.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75)  # Quality modifer to armour stat


class Unitstat:
    def __init__(self, main_dir, ruleset, rulesetfolder):
        """Unit stat data read"""
        # v Unit stat dict
        self.troop_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", rulesetfolder, "troop", "troop_preset.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Type", "Grade", "Race", "Cost", "Upkeep", "Troop", "Troop Class", "Size"]  # value int only
            list_column = ["Trait", "Skill", "Armour", "Melee Weapon", "Ranged Weapon", "Mount", "Role", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            self.troop_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                self.troop_list[row[0]] = row[1:]
            unitfile.close()
        # ^ End subunit stat list

        # v Lore of the subunit dict
        self.troop_lore = {}
        with open(os.path.join(main_dir, "data", "ruleset", rulesetfolder, "troop", "troop_lore.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.troop_lore[row[0]] = row[1:]
            unitfile.close()
        # ^ End subunit lore

        # v Unit status effect dict
        self.status_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_status.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID", "Temperature Change"]  # value int only
            list_column = ["Special Effect", "Status Conflict", "Ruleset"]  # value in list only
            mod_column = ["Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect", "Armour Effect",
                          "Speed Effect", "Accuracy Effect", "Reload Effect", "Charge Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            self.status_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if run != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column, int_column=int_column)
                    self.status_list[row[0]] = row[1:]
                run += 1
        unitfile.close()
        # ^ End status effect

        # v Race dict
        self.race_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_race.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if i.isdigit() or ("." in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
                            row[n] = float(i)
                    self.race_list[row[0]] = row[1:]
        unitfile.close()
        # ^ End race

        # v Unit grade dict
        self.grade_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_grade.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID"]  # value int only
            list_column = ["Trait"]  # value in list only
            mod_column = ["Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect",
                          "Speed Effect", "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            self.grade_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                for n, i in enumerate(row):
                    if run != 0:
                        row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column, int_column=int_column)
                self.grade_list[row[0]] = row[1:]
                run += 1
        unitfile.close()
        # ^ End subunit grade

        # v Unit skill dict
        self.skill_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_skill.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID", "Type", "Area of Effect", "Element", "Cost"]  # value int only
            list_column = ["Status", "Restriction", "Condition", "Enemy Status", "Ruleset"]  # value in list only
            mod_column = ["Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect", "Speed Effect",
                          "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Critical Effect", "Damage Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            self.skill_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if run != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column, int_column=int_column)
                    self.skill_list[row[0]] = row[1:]
                    run += 1
        unitfile.close()
        # ^ End subunit skill

        # v Unit trait dict
        self.trait_list = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_trait.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID", "Buff Range", "Race", "Cost"]  # value int only
            list_column = ["Status", "Special Effect", "Enemy Status", "Ruleset"]  # value in list only
            mod_column = ["Buff Modifier", "Melee Attack Effect", "Melee Defence Effect", "Ranged Defence Effect",
                          "Speed Effect", "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Siege Effect", "Supply Effect", "Upkeep Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            self.trait_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]

                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if run != 0:
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column, int_column=int_column)
                    self.trait_list[row[0]] = row[1:]
                    run += 1
        unitfile.close()
        # ^ End subunit trait

        # v Unit role dict
        self.role = {}
        with open(os.path.join(main_dir, "data", "troop", "troop_class.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.role[row[0]] = row[1:]
        unitfile.close()
        # ^ End subunit role

        # v Unit mount dict
        self.mount_list = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_preset.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost"]  # value int only
            list_column = ["Trait", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            self.mount_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                if "," in row[-2]:  # ruleset list, make str with "," into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                    self.mount_list[row[0]] = row[1:]
        unitfile.close()
        # ^ End subunit mount dict

        # v Mount grade dict
        self.mount_grade_list = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_grade.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0  # for avoiding header
            int_column = ["ID"]  # value int only
            list_column = ["Trait"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            self.mount_grade_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                for n, i in enumerate(row):
                    if run != 0:
                        row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                self.mount_grade_list[row[0]] = row[1:]
                run += 1
        unitfile.close()
        # ^ End mount grade

        # v Mount armour dict
        self.mount_armour_list = {}
        with open(os.path.join(main_dir, "data", "troop", "mount_armour.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost"]  # value int only
            list_column = ["Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            self.mount_armour_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                if "," in row[-2]:  # ruleset list, make str with "," into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                    self.mount_armour_list[row[0]] = row[1:]
        unitfile.close()
        # ^ End mount armour


class Leaderstat:
    def __init__(self, main_dir, img, imgorder, option):
        self.imgs = img
        self.imgorder = imgorder
        self.leader_list = {}
        with open(os.path.join(main_dir, "data", "ruleset", str(option), "leader", "leader.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Race", "Melee Command", "Range Command", "Cavalry Command", "Combat", "Social Class",
                          "Forcedimageid", "Faction"]  # value int only
            list_column = ["Melee Weapon","Ranged Weapon","Armour", "Mount","Skill","Trait"]
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            for row in rd:
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                self.leader_list[row[0]] = row[1:]
        unitfile.close()

        # v Add common leader to the leader list with gameid + 10000
        with open(os.path.join(main_dir, "data", "ruleset", str(option), "leader", "common_leader.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Race", "Melee Command", "Range Command", "Cavalry Command", "Combat", "Social Class", "Forcedimageid",
                          "Faction"]  # value int only
            list_column = ["Melee Weapon", "Ranged Weapon", "Armour", "Mount", "Skill", "Trait"]
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            self.leader_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                self.leader_list[row[0]] = row[1:]
        unitfile.close()
        # ^ End common leader

        # v Lore of the leader dict
        self.leader_lore = {}
        with open(os.path.join(main_dir, "data", "ruleset", str(option), "leader", "leader_lore.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.leader_lore[row[0]] = row[1:]
            unitfile.close()
        # ^ End leader lore

        # v Leader class dict
        self.leader_class = {}
        with open(os.path.join(main_dir, "data", "leader", "leader_class.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            self.leader_class_list_header = {k: v for v, k in enumerate(header[1:])}
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.leader_class[row[0]] = row[1:]
        unitfile.close()
        # ^ End leader class
