import csv

import pygame.freetype


class Factiondata():
    images = []
    main_dir = None

    def __init__(self, option):
        """Unit stat data read"""
        self.faction_list = {}
        with open(self.main_dir + "/data" + "/ruleset" + option + "/faction" + "/faction.csv", encoding="utf-8", mode = "r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    if n in (2,3):
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                        elif i.isdigit():
                            row[n] = [int(i)]
                self.faction_list[row[0]] = row[1:]
            unitfile.close()


class Faction(pygame.sprite.Sprite):
    faction_list = None

    def __init__(self, factionid):
        self.gameid = factionid
        self.name = self.faction_list[self.gameid][0]
        self.image = self.faction_list.images[factionid]
