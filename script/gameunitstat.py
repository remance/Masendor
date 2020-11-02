import csv
import re

from RTS import mainmenu

main_dir = mainmenu.main_dir

class Weaponstat():
    def __init__(self, img, ruleset):
        """Armour has dmg, penetration and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.weaponlist = {}
        with open(main_dir + "\data\war" + '\\unit_weapon.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if n == 5:
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.weaponlist[row[0]] = row[1:]
        unitfile.close()
        self.quality = (25, 50, 75, 100, 125, 150, 175)


class Armourstat():
    def __init__(self, img, ruleset):
        """Armour has base defence and quality 0 = Broken, 1 = Very Poor, 2 = Poor, 3 = Standard, 4 = Good, 5 = Superb, 6 = Perfect"""
        self.imgs = img
        self.armourlist = {}
        with open(main_dir + "\data\war" + '\\unit_armour.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if n == 5:
                            if "," in i:
                                row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                            elif i.isdigit():
                                row[n] = [int(i)]
                        elif i.isdigit():
                            row[n] = int(i)
                    self.armourlist[row[0]] = row[1:]
        unitfile.close()
        self.quality = (25, 50, 75, 100, 125, 150, 175)


class Unitstat():
    def __init__(self, ruleset, rulesetfolder):
        """Unit stat data read"""
        self.unitlist = {}  ## Unit stat list
        with open(main_dir + "\data\\ruleset" + rulesetfolder + "\war" + '\\unit_preset.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)  ## No need to make it float
                    if n in (5, 6, 12, 22, 23):
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.unitlist[row[0]] = row[1:]
            unitfile.close()
        self.unitlore = {}  ## Unit lore list
        with open(main_dir + "\data\\ruleset" + rulesetfolder + "\war" + '\\unit_lore.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                self.unitlore[row[0]] = row[1:]
            unitfile.close()
        self.statuslist = {}
        with open(main_dir + "\data\war" + '\\unit_status.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            run = 0
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if run != 0:  # Skip first row header
                            if n in (5, 6, 7, 8, 9, 10, 11, 12):
                                if i == "":
                                    row[n] = 1.0
                                else:
                                    row[n] = float(i) / 100  ## Need to make it float for percentage cal
                            elif n in (2, 3):
                                if "," in i:
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                                elif i.isdigit():
                                    row[n] = [int(i)]
                                else:
                                    row[n] = []
                            elif (i.isdigit() or ("-" in i and re.search('[a-zA-Z]', i) is None)) and n not in (1, 20):
                                row[n] = int(i)
                    self.statuslist[row[0]] = row[1:]
                run += 1
        unitfile.close()
        ## Race List
        self.racelist = {}
        with open(main_dir + "\data\war" + '\\unit_race.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[-2] in ("0", "Ruleset") or str(ruleset) == row[-2]:
                    for n, i in enumerate(row):
                        if i.isdigit(): row[n] = int(i)  ## No need to be float
                        # if n == 12:
                        #     if "," in i:
                        #         row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        #     elif i.isdigit():
                        #         row[n] = [int(i)]
                    self.racelist[row[0]] = row[1:]
        unitfile.close()
        self.gradelist = {}  ##Unit grade list
        with open(main_dir + "\data\war" + '\\unit_grade.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)  ## No need to be float
                    if n == 12:
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.gradelist[row[0]] = row[1:]
        unitfile.close()
        self.abilitylist = {}  ## Unit skill list
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
        """Unit property list"""
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
                                    row[n] = float(i) / 100  ## Need to be float
                            elif n in (19, 32, 33):
                                if "," in i:
                                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                                elif i.isdigit():
                                    row[n] = [int(i)]
                                else:
                                    row[n] = []
                            elif (i.isdigit() or ("-" in i and re.search('[a-zA-Z]', i) is None)) and n not in (1, 34, 35):
                                row[n] = int(i)
                    self.traitlist[row[0]] = row[1:]
                    run += 1
        unitfile.close()
        """unit role list"""
        self.role = {}
        with open(main_dir + "\data\war" + '\\unit_type.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = float(i)
                self.role[row[0]] = row[1:]
        unitfile.close()
        """unit mount list"""
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

