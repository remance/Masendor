import csv
import re

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
        with open(main_dir + "\\data\\war" + "\\troop_weapon.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost", "ImageID", "Speed"]  # value int only
            list_column = ["Properties", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
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
        with open(main_dir + "\\data\\war" + "\\troop_armour.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost"]  # value int only
            list_column = ["Properties", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
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
        self.unit_list = {}
        with open(main_dir + "\\data\\ruleset" + rulesetfolder + "\\war" + "\\troop_preset.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "ImageID", "Grade", "Race", "Cost", "Upkeep", "Unit Type", "Size"]  # value int only
            list_column = ["Properties", "Abilities", "Armour", "Melee Weapon", "Range Weapon", "Mount", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            for row in rd:
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, int_column=int_column)
                self.unit_list[row[0]] = row[1:]
            unitfile.close()
        # ^ End subunit stat list

        # v Lore of the subunit dict
        self.unit_lore = {}
        with open(main_dir + "\\data\\ruleset" + rulesetfolder + "\\war" + "\\troop_lore.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.unit_lore[row[0]] = row[1:]
            unitfile.close()
        # ^ End subunit lore

        # v Unit status effect dict
        self.status_list = {}
        with open(main_dir + "\\data\\war" + "\\troop_status.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID", "Temperature Change"]  # value int only
            list_column = ["Special Effect", "Status Conflict", "Ruleset"]  # value in list only
            mod_column = ["Melee Attack Effect", "Melee Defense Effect", "Range Defense Effect", "Armour Effect",
                          "Speed Effect", "Accuracy Effect", "Reload Effect", "Charge Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
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
        with open(main_dir + "\\data\\war" + "\\troop_race.csv", encoding="utf-8", mode="r") as unitfile:
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
        with open(main_dir + "\\data\\war" + "\\troop_grade.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID"]  # value int only
            list_column = ["Properties"]  # value in list only
            mod_column = ["Melee Attack Effect", "Melee Defense Effect", "Range Defense Effect",
                          "Speed Effect", "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for row in rd:
                for n, i in enumerate(row):
                    if run != 0:
                        row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column, int_column=int_column)
                self.grade_list[row[0]] = row[1:]
                run += 1
        unitfile.close()
        # ^ End subunit grade

        # v Unit skill dict
        self.ability_list = {}
        with open(main_dir + "\\data\\war" + "\\troop_ability.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID", "Type", "Area of Effect", "Element", "Cost"]  # value int only
            list_column = ["Status", "Restriction", "Condition", "Enemy Status", "Ruleset"]  # value in list only
            mod_column = ["Melee Attack Effect", "Melee Defense Effect", "Range Defense Effect", "Speed Effect",
                          "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Critical Effect", "Damage Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if run != 0:  # Skip first row header
                            row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column, int_column=int_column)
                    self.ability_list[row[0]] = row[1:]
                    run += 1
        unitfile.close()
        # ^ End subunit skill

        # v Unit property dict
        self.trait_list = {}
        with open(main_dir + "\\data\\war" + "\\troop_property.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0
            int_column = ["ID", "Buff Range", "Race", "Cost"]  # value int only
            list_column = ["Status", "Abilities", "Special Effect", "Enemy Status", "Ruleset"]  # value in list only
            mod_column = ["Buff Modifier", "Melee Attack Effect", "Melee Defense Effect", "Range Defense Effect",
                          "Speed Effect", "Accuracy Effect", "Range Effect", "Reload Effect", "Charge Effect",
                          "Siege Effect", "Supply Effect", "Upkeep Effect"]  # need to be calculate to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
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
        # ^ End subunit property

        # v Unit role dict
        self.role = {}
        with open(main_dir + "\\data\\war" + "\\troop_type.csv", encoding="utf-8", mode="r") as unitfile:
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
        with open(main_dir + "\\data\\war" + "\\mount_preset.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost"]  # value int only
            list_column = ["Properties", "Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
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
        with open(main_dir + "\\data\\war" + "\\mount_grade.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            run = 0  # for avoiding header
            int_column = ["ID"]  # value int only
            list_column = ["Properties"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
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
        with open(main_dir + "\\data\\war" + "\\mount_armour.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Cost"]  # value int only
            list_column = ["Ruleset"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
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
        with open(main_dir + "\\data\\ruleset" + str(option) + "\\leader" + "\\leader.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Melee Command", "Range Command", "Cavalry Command", "Combat", "Social Class",
                          "Forcedimageid", "Faction"]  # value int only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            for row in rd:
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, int_column=int_column)
                self.leader_list[row[0]] = row[1:]
        unitfile.close()

        # v Add common leader to the leader list with gameid + 10000
        with open(main_dir + "\\data\\ruleset" + str(option) + "\\leader" + "\\common_leader.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            int_column = ["ID", "Melee Command", "Range Command", "Cavalry Command", "Combat", "Social Class", "Forcedimageid",
                          "Faction"]  # value int only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            for row in rd:
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, int_column=int_column)
                self.leader_list[row[0]] = row[1:]
        unitfile.close()
        # ^ End common leader

        # v Lore of the leader dict
        self.leader_lore = {}
        with open(main_dir + "\\data\\ruleset" + str(option) + "\\leader" + "\\leader_lore.csv", encoding="utf-8", mode="r") as unitfile:
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
        with open(main_dir + "\\data\\leader" + "\\leader_class.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.leader_class[row[0]] = row[1:]
        unitfile.close()
        # ^ End leader class
