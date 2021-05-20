import csv
import re
"""This file contains all class and function that read subunit/leader related data and save them into dict for ingame use"""

class Weaponstat():
    def __init__(self, main_dir, img, ruleset):
        """Weapon has dmg, penetration and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.weapon_list = {}
        with open(main_dir + "\data\war" + "\\unit_weapon.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if n == 5: # Properties must be in list
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.weapon_list[row[0]] = row[1:]
        unitfile.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75) # Quality modifer to weapon stat


class Armourstat():
    def __init__(self, main_dir, img, ruleset):
        """Armour has base defence and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.armour_list = {}
        with open(main_dir + "\data\war" + "\\unit_armour.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if n == 5: # Properties must be in list
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.armour_list[row[0]] = row[1:]
        unitfile.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75)  # Quality modifer to armour stat


class Unitstat():
    def __init__(self, main_dir, ruleset, rulesetfolder):
        """Unit stat data read"""
        #v Unit stat dict
        self.unit_list = {}
        with open(main_dir + "\data\\ruleset" + rulesetfolder + "\war" + "\\unit_preset.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if n in (5, 6, 12, 22, 23, 30): # property,ability,armour,melee weapon,range weapon,mount coloumns
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                        elif i.isdigit():
                            row[n] = [int(i)]
                    elif i.isdigit():
                        row[n] = int(i)  # No need to make it float
                self.unit_list[row[0]] = row[1:]
            unitfile.close()
        #^ End subunit stat list
        #v Lore of the subunit dict
        self.unit_lore = {}
        with open(main_dir + "\data\\ruleset" + rulesetfolder + "\war" + "\\unit_lore.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.unit_lore[row[0]] = row[1:]
            unitfile.close()
        #^ End subunit lore

        #v Unit status effect dict
        self.status_list = {}
        with open(main_dir + "\data\war" + "\\unit_status.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                if "," in row[-2]: # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset): # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if run != 0:  # Skip first row header
                            if n in (5, 6, 7, 8, 9, 10, 11, 12):
                                if i == "": # empty stat become 1.0 so it mean nothing when calculate into subunit
                                    row[n] = 1.0
                                else:
                                    row[n] = float(i) / 100  # Need to make it float / 100 for percentage cal 50 become 0.5
                            elif n in (2, 3): # special effect and status conflict list
                                if "," in i:
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                                elif i.isdigit():
                                    row[n] = [int(i)]
                                else:
                                    row[n] = []
                            elif (i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None)) and n != 1: # negative number for bonus
                                row[n] = float(i)
                    self.status_list[row[0]] = row[1:]
                run += 1
        unitfile.close()
        #^ End status effect

        #v Race dict
        self.race_list = {}
        with open(main_dir + "\data\war" + "\\unit_race.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if i.isdigit(): row[n] = int(i)  # No need to be float
                        # if n == 12:
                        #     if "," in i:
                        #         row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                        #     elif i.isdigit():
                        #         row[n] = [int(i)]
                    self.race_list[row[0]] = row[1:]
        unitfile.close()
        #^ End race

        #v Unit grade dict
        self.grade_list = {}
        with open(main_dir + "\data\war" + "\\unit_grade.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)  # No need to be float
                    if run != 0:
                        if n == 13:
                            if "," in i: # Properties to subunit in list
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif n in (8,9): # health and stamina modifier effect
                            row[n] = float(i) / 100
                self.grade_list[row[0]] = row[1:]
                run += 1
        unitfile.close()
        #^ End subunit grade

        #v Unit skill dict
        self.ability_list = {}
        with open(main_dir + "\data\war" + "\\unit_ability.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if run != 0:  # Skip first row header
                            if n in (11, 12, 13, 14, 15, 16, 17, 18, 24, 25):
                                if i == "":
                                    row[n] = 1.0
                                else:
                                    row[n] = float(i) / 100  # Need to be float for percentage cal

                            elif n in (6, 7, 28, 31):
                                """Convert all condition and status to list"""
                                if "," in i:
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                                elif i.isdigit():
                                    row[n] = [int(i)]

                            elif n in (0, 2, 3, 4, 5, 8, 9, 10, 19, 20, 21, 22, 23, 26, 27, 29, 30):
                                if i == "":
                                    pass
                                elif "." in i and re.search("[a-zA-Z]", i) is None:
                                    row[n] = float(i)
                                else:
                                    row[n] = int(i)
                    self.ability_list[row[0]] = row[1:]
                    run += 1
        unitfile.close()
        #^ End subunit skill

        #v Unit property dict
        self.trait_list = {}
        with open(main_dir + "\data\war" + "\\unit_property.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                if "," in row[-2]:  # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]

                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if run != 0:
                            if n in (3, 4, 5, 6, 8, 9, 10, 11, 12): #modifier effect
                                if i == "":
                                    row[n] = 1.0
                                else:
                                    row[n] = float(i) / 100  # Need to be float

                            elif n in (19, 33): # status and status to enemy
                                if "," in i:
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                                elif i.isdigit():
                                    row[n] = [int(i)]
                                else:
                                    row[n] = []
                            elif (i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None)) and n not in (1, 34, 35):
                                row[n] = float(i)

                    self.trait_list[row[0]] = row[1:]
                    run += 1
        unitfile.close()
        #^ End subunit property

        #v Unit role dict
        self.role = {}
        with open(main_dir + "\data\war" + "\\unit_type.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                self.role[row[0]] = row[1:]
        unitfile.close()
        #^ End subunit role

        #v Unit mount dict
        self.mount_list = {}
        with open(main_dir + "\data\war" + "\\mount_preset.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if "," in row[-2]:  # ruleset list, make str with "," into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):  # only grab effect that existed in the ruleset and frist row
                    for n, i in enumerate(row):
                        if n == 7: # properties list column
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.mount_list[row[0]] = row[1:]
        unitfile.close()
        #^ End subunit mount dict

        #v Mount grade dict
        self.mount_grade_list = {}
        with open(main_dir + "\data\war" + "\\mount_grade.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0 # for avoiding header
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)  # No need to be float
                    if run != 0:
                        if n == 8: # Properties list
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif n in (4,5): # health and stamina modifier effect
                            row[n] = float(i) / 100
                self.mount_grade_list[row[0]] = row[1:]
                run += 1
        unitfile.close()
        #^ End mount grade

        #v Mount armour dict
        self.mount_armour_list = {}
        with open(main_dir + "\data\war" + "\\mount_armour.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if "," in row[-2]:  # ruleset list, make str with "," into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset), "Ruleset") for rule in thisruleset):
                    for n, i in enumerate(row):
                        if i.isdigit(): row[n] = int(i)  # No need to be float
                    self.mount_armour_list[row[0]] = row[1:]
        unitfile.close()
        #^ End mount armour

class Leaderstat():
    def __init__(self, main_dir, img, imgorder, option):
        self.imgs = img
        self.imgorder = imgorder
        self.leader_list = {}
        with open(main_dir + "\data\\ruleset" + str(option) + "\\leader" + "\\leader.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                    # else: row[n] = [int(i)]
                self.leader_list[row[0]] = row[1:]
        unitfile.close()

        #v Add common leader to the leader list with gameid + 10000
        with open(main_dir + "\data\\ruleset" + str(option) + "\\leader" + "\\common_leader.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                    # else: row[n] = [int(i)]
                self.leader_list[row[0]] = row[1:]
        unitfile.close()
        #^ End common leader

        #v Lore of the leader dict
        self.leader_lore = {}
        with open(main_dir + "\data\\ruleset" + str(option) + "\\leader" + "\\leader_lore.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.leader_lore[row[0]] = row[1:]
            unitfile.close()
        #^ End leader lore

        #v Leader class dict
        self.leader_class = {}
        with open(main_dir + "\data\leader" + "\\leader_class.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None):
                        row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                    # else: row[n] = [int(i)]
                self.leader_class[row[0]] = row[1:]
        unitfile.close()
        #^ End leader class


