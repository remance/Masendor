import csv
import re

class Weaponstat():
    def __init__(self, main_dir, img, ruleset):
        """Weapon has dmg, penetration and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.weaponlist = {}
        with open(main_dir + "\data\war" + '\\unit_weapon.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if n == 5: # Properties must be in list
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.weaponlist[row[0]] = row[1:]
        unitfile.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75) # Quality modifer to weapon stat


class Armourstat():
    def __init__(self, main_dir, img, ruleset):
        """Armour has base defence and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.armourlist = {}
        with open(main_dir + "\data\war" + '\\unit_armour.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if n == 5: # Properties must be in list
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.armourlist[row[0]] = row[1:]
        unitfile.close()
        self.quality = (0.25, 0.50, 0.75, 1, 1.25, 1.50, 1.75)  # Quality modifer to armour stat


class Unitstat():
    def __init__(self, main_dir, ruleset, rulesetfolder):
        """Unit stat data read"""
        #v Unit stat dict
        self.unitlist = {}
        with open(main_dir + "\data\\ruleset" + rulesetfolder + "\war" + '\\unit_preset.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)  # No need to make it float
                    if n in (5, 6, 12, 22, 23):
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.unitlist[row[0]] = row[1:]
            unitfile.close()
        #^ End unit stat list
        #v Lore of the unit dict
        self.unitlore = {}
        with open(main_dir + "\data\\ruleset" + rulesetfolder + "\war" + '\\unit_lore.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.unitlore[row[0]] = row[1:]
            unitfile.close()
        #^ End lore
        #v Unit status effect dict
        self.statuslist = {}
        with open(main_dir + "\data\war" + '\\unit_status.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                if "," in row[-2]: # make str with , into list
                    thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(',')]
                else:
                    thisruleset = [row[-2]]
                if any(rule in ("0", str(ruleset)) for rule in thisruleset): # only grab effect that existed in the ruleset
                    for n, i in enumerate(row):
                        if run != 0:  # Skip first row header
                            if n in (5, 6, 7, 8, 9, 10, 11, 12):
                                if i == "": # empty stat become 1.0 so it mean nothing when calculate into unit
                                    row[n] = 1.0
                                else:
                                    row[n] = float(i) / 100  # Need to make it float / 100 for percentage cal 50 become 0.5
                            elif n in (2, 3): # special effect and status conflict list
                                if "," in i:
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                                elif i.isdigit():
                                    row[n] = [int(i)]
                                else:
                                    row[n] = []
                            elif (i.isdigit() or ("-" in i and re.search('[a-zA-Z]', i) is None)) and n not in (1, 20): # negative number
                                row[n] = float(i)
                    self.statuslist[row[0]] = row[1:]
                run += 1
        unitfile.close()
        #^ End status effect
        #v Race dict
        self.racelist = {}
        with open(main_dir + "\data\war" + '\\unit_race.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if i.isdigit(): row[n] = int(i)  # No need to be float
                        # if n == 12:
                        #     if "," in i:
                        #         row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        #     elif i.isdigit():
                        #         row[n] = [int(i)]
                    self.racelist[row[0]] = row[1:]
        unitfile.close()
        #^ End race
        #v Unit grade dict
        self.gradelist = {}
        with open(main_dir + "\data\war" + '\\unit_grade.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)  # No need to be float
                    if n == 12:
                        if "," in i: # Properties to unit in list
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.gradelist[row[0]] = row[1:]
        unitfile.close()
        #^ End unit grade
        #v Unit skill dict
        self.abilitylist = {}
        with open(main_dir + "\data\war" + '\\unit_ability.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
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
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                                elif i.isdigit():
                                    row[n] = [int(i)]
                            elif n in (0, 2, 3, 4, 5, 8, 9, 10, 19, 20, 21, 22, 23, 26, 27, 29, 30):
                                if i == "":
                                    pass
                                elif "." in i and re.search('[a-zA-Z]', i) is None:
                                    row[n] = float(i)
                                else:
                                    row[n] = int(i)
                    run += 1
                    self.abilitylist[row[0]] = row[1:]
        unitfile.close()
        #^ End unit skill
        #v Unit property dict
        self.traitlist = {}
        with open(main_dir + "\data\war" + '\\unit_property.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if run != 0:
                            if n in (3, 4, 5, 6, 8, 9, 10, 11, 12):
                                if i == "":
                                    row[n] = 1.0
                                else:
                                    row[n] = float(i) / 100  # Need to be float
                            elif n in (19, 32, 33):
                                if "," in i:
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                                elif i.isdigit():
                                    row[n] = [int(i)]
                                else:
                                    row[n] = []
                            elif (i.isdigit() or ("-" in i and re.search('[a-zA-Z]', i) is None)) and n not in (1, 34, 35):
                                row[n] = float(i)
                    self.traitlist[row[0]] = row[1:]
                    run += 1
        unitfile.close()
        #^ End unit property
        #v Unit role dict
        self.role = {}
        with open(main_dir + "\data\war" + '\\unit_type.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                self.role[row[0]] = row[1:]
        unitfile.close()
        #^ End unit role
        #v Unit mount dict
        self.mountlist = {}
        with open(main_dir + "\data\war" + '\\unit_mount.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if n == 6:
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.mountlist[row[0]] = row[1:]
        unitfile.close()
        #^ End unit mount dict

class Leaderstat():
    def __init__(self, main_dir, img, imgorder, option):
        self.imgs = img
        self.imgorder = imgorder
        self.leaderlist = {}
        with open(main_dir + "\data" + "\\ruleset" + str(option) + "\\leader" + "\\leader.csv", "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderlist[row[0]] = row[1:]
        unitfile.close()
        #v Add common leader to the leader list with gameid + 10000
        with open(main_dir + "\data" + "\\ruleset" + str(option) + "\\leader" + "\\common_leader.csv", "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderlist[row[0]] = row[1:]
        unitfile.close()
        #^ End common leader
        #v Leader class dict
        self.leaderclass = {}
        with open(main_dir + "\data\leader" + "\\leader_class.csv", "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit() or ("-" in i and re.search('[a-zA-Z]', i) is None):
                        row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderclass[row[0]] = row[1:]
        unitfile.close()

