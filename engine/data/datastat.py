"""This file contains all class and function that read troop/leader related data
and save them into dict for in game use """

import csv
import os
import re
from pathlib import Path

import numpy as np

from engine import utility

fcv = utility.filename_convert_readable
stat_convert = utility.stat_convert
load_images = utility.load_images


class GameData:
    def __init__(self):
        from engine.game.game import Game
        self.main_dir = Game.main_dir
        self.data_dir = Game.data_dir
        self.module_dir = Game.module_dir
        self.font_dir = Game.font_dir
        self.localisation = Game.localisation
        self.screen_scale = Game.screen_scale


class TroopData(GameData):
    def __init__(self):
        """
        For keeping all data related to troop.
        """
        GameData.__init__(self)
        # Troop special status effect dict, not module related
        self.special_effect_list = {}
        with open(os.path.join(self.data_dir, "troop", "troop_special_effect.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ["ID"]  # value int only
            tuple_column = ["Status"]  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                self.special_effect_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Troop status effect dict
        self.status_list = {}
        with open(os.path.join(self.module_dir, "troop", "troop_status.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Max Stack", "Temperature Change", "Physical Resistance Bonus",
                          "Fire Resistance Bonus", "Water Resistance Bonus",
                          "Air Resistance Bonus", "Earth Resistance Bonus", "Magic Resistance Bonus",
                          "Heat Resistance Bonus", "Cold Resistance Bonus", "Poison Resistance Bonus")  # value int only
            tuple_column = ("Special Effect", "Status Conflict")  # value in tuple only
            mod_column = ("Melee Attack Modifier", "Melee Defence Modifier", "Ranged Defence Modifier",
                          "Speed Modifier", "Accuracy Modifier", "Melee Speed Modifier", "Reload Modifier",
                          "Charge Modifier")  # need to be calculated to percentage
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.status_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Add map and element effect status if exist in module
        require_effect_list = ("Wet", "Drench", "Cold", "Hot", "Heatstroke", "Sink", "Drown", "Swimming", "Muddy Leg",
                               "Decay", "Burn", "Severe Burning", "Shock", "Electrocution", "Stun", "Petrify",
                               "Poison", "Deadly Poison")
        for key, value in self.status_list.copy().items():
            if value["Name"] in require_effect_list:
                self.status_list[value["Name"]] = key

        # Race dict
        self.race_list = {}
        with open(os.path.join(self.module_dir, "troop", "troop_race.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("Strength", "Dexterity", "Agility", "Constitution", "Intelligence", "Wisdom",
                          "Physical Resistance", "Fire Resistance", "Water Resistance", " Air Resistance",
                          "Earth Resistance", "Poison Resistance", "Magic Resistance", "Size")  # value int only
            list_column = ("Trait",)  # value in list only
            tuple_column = ("Special Hair Part", "Special Body Part")  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.race_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Troop grade dict
        self.grade_list = {}
        with open(os.path.join(self.module_dir, "troop", "troop_grade.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID",)  # value int only
            list_column = ("Trait",)  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column,
                                       int_column=int_column)
                self.grade_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Troop skill dict
        self.skill_list = {}
        with open(os.path.join(self.module_dir, "troop", "troop_skill.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Troop Type", "Area of Effect", "Cost", "Charge Skill")  # value int only
            list_column = ("Action",)
            tuple_column = ("Status", "Enemy Status", "Effect Sprite", "AI Use Condition")  # value in tuple only
            mod_column = ("Melee Attack Modifier", "Melee Defence Modifier", "Ranged Defence Modifier", "Speed Modifier",
                          "Accuracy Modifier", "Range Modifier", "Melee Speed Modifier", "Reload Modifier", "Charge Modifier",
                          "Critical Modifier", "Damage Modifier", "Weapon Impact Modifier")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                       tuple_column=tuple_column, int_column=int_column)
                self.skill_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                self.skill_list[row[0]]["Shake Power"] = int(self.skill_list[row[0]]["Sound Distance"] / 10)
        edit_file.close()

        # Troop trait dict
        self.trait_list = {}
        with open(os.path.join(self.module_dir, "troop", "troop_trait.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Area of Effect", "Cost", "Upkeep", "Element", "Charge Defence Bonus",
                          "Morale Bonus", "Discipline Bonus", "Critical Bonus", "Sight Bonus",
                          "Hidden Bonus", "Physical Resistance Bonus",
                          "Fire Resistance Bonus", "Water Resistance Bonus", "Air Resistance Bonus",
                          "Earth Resistance Bonus", "Poison Resistance Bonus", "Magic Resistance Bonus",
                          "Heat Resistance Bonus", "Cold Resistance Bonus")  # value int only
            tuple_column = ("Status", "Special Effect", "Enemy Status")  # value in tuple only
            percent_column = ("Buff Modifier",)
            mod_column = ("Melee Attack Modifier", "Melee Defence Modifier", "Ranged Defence Modifier",
                          "Speed Modifier", "Accuracy Modifier", "Range Modifier", "Melee Speed Modifier",
                          "Reload Modifier", "Charge Modifier", "Siege Modifier", "Supply Modifier", "Upkeep Modifier")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            percent_column = [index for index, item in enumerate(header) if item in percent_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, percent_column=percent_column, mod_column=mod_column,
                                       tuple_column=tuple_column, int_column=int_column)
                self.trait_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Equipment grade dict
        self.equipment_grade_list = {}
        with open(os.path.join(self.module_dir, "troop", "equipment_grade.csv"),
                  encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID",)  # value int only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, int_column=int_column)
                self.equipment_grade_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Weapon dict
        self.weapon_list = {}
        for index, weapon_list in enumerate(("troop_weapon", "mount_weapon")):
            with open(os.path.join(self.module_dir, "troop",
                                   weapon_list + ".csv"), encoding="utf-8", mode="r") as edit_file:
                rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                int_column = ("Strength Bonus Scale", "Dexterity Bonus Scale", "Physical Damage",
                              "Fire Damage", "Water Damage", "Air Damage", "Earth Damage", "Poison Damage",
                              "Magic Damage",
                              "Armour Penetration", "Defence", "Weight", "Speed", "Ammunition", "Magazine",
                              "Shot Number",
                              "Range", "Travel Speed", "Learning Difficulty", "Mastery Difficulty",
                              "Learning Difficulty",
                              "Cost", "ImageID", "Speed", "Hand")  # value int only
                float_column = ("Cooldown",)
                list_column = ("Skill", "Trait", "Properties")  # value in list only
                tuple_column = ("Damage Sprite Effect",)  # value in tuple only
                percent_column = ("Damage Balance",)
                int_column = [index for index, item in enumerate(header) if item in int_column]
                list_column = [index for index, item in enumerate(header) if item in list_column]
                tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
                percent_column = [index for index, item in enumerate(header) if item in percent_column]
                float_column = [index for index, item in enumerate(header) if item in float_column]
                for row_index, row in enumerate(rd[1:]):
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, percent_column=percent_column, list_column=list_column,
                                           tuple_column=tuple_column, int_column=int_column, float_column=float_column)
                    self.weapon_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                    self.weapon_list[row[0]]["Shake Power"] = int(self.weapon_list[row[0]]["Sound Distance"] / 10)
                    self.weapon_list[row[0]]["Bullet Shake Power"] = int(
                        self.weapon_list[row[0]]["Bullet Sound Distance"] / 10)
            edit_file.close()

        # Armour dict
        self.armour_list = {}
        with open(os.path.join(self.module_dir, "troop", "troop_armour.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Cost")  # value int only
            list_column = ("Trait",)  # value in list only
            tuple_column = ()  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row_index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.armour_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Mount dict
        self.mount_list = {}
        with open(os.path.join(self.module_dir, "troop", "mount.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Cost")  # value int only
            list_column = ("Trait",)  # value in list only
            tuple_column = ()  # value in tuple only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row_index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, list_column=list_column,
                                       int_column=int_column)
                self.mount_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Mount grade dict
        self.mount_grade_list = {}
        with open(os.path.join(self.module_dir, "troop", "mount_grade.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID",)  # value int only
            list_column = ("Trait",)  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column,
                                       int_column=int_column)
                self.mount_grade_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Mount armour dict
        self.mount_armour_list = {}
        with open(os.path.join(self.module_dir, "troop", "mount_armour.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID", "Cost")  # value int only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            self.mount_armour_list_header = {k: v for v, k in enumerate(header[1:])}
            for row_index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                self.mount_armour_list[row[0]] = {header[index + 1]: stuff for index, stuff in
                                                  enumerate(row[1:])}
        edit_file.close()

        # Troop stat dict
        self.troop_list = {}
        with open(os.path.join(self.module_dir, "troop", "preset", "troop_preset.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("Grade", "Race", "Cost", "Upkeep", "Troop")  # value int only
            list_column = ("Trait", "Skill",)  # value in list only
            tuple_column = ("Armour", "Primary Main Weapon", "Primary Sub Weapon", "Secondary Main Weapon",
                            "Secondary Sub Weapon", "Mount", "Role", "Faction")  # value in tuple only
            percent_column = ("Ammunition Modifier",)
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            percent_column = [index for index, item in enumerate(header) if item in percent_column]
            for row_index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, percent_column=percent_column, list_column=list_column,
                                       tuple_column=tuple_column, int_column=int_column)
                self.troop_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

            # Add troop size to data
            for key in self.troop_list:
                self.troop_list[key]["Size"] = 1
                if self.troop_list[key]["Mount"]:
                    mount_race = self.mount_list[self.troop_list[key]["Mount"][0]]["Race"]
                    if mount_race != 0:
                        self.troop_list[key]["Size"] = self.race_list[mount_race]["Size"] / 10
                    else:
                        self.troop_list[key]["size"] = self.race_list[self.troop_list[key]["Race"]]["Size"] / 10

        self.troop_name_list = [value["Name"] for value in self.troop_list.values()]

        # Troop sprite
        self.troop_sprite_list = {}
        with open(os.path.join(self.module_dir, "troop", "preset", "troop_sprite.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            for row_index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    if "," in i:
                        row[n] = i.split(",")
                self.troop_sprite_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()

        # Troop formation dict
        self.default_formation_list = {}
        part_folder = Path(os.path.join(self.data_dir, "troop", "formation"))
        subdirectories = [os.sep.join(os.path.normpath(x).split(os.sep)[-1:]) for x in
                          part_folder.iterdir() if not x.is_dir()]
        for folder in subdirectories:
            formation_name = fcv(folder.replace(".csv", ""))
            self.default_formation_list[formation_name] = []
            with open(os.path.join(self.data_dir, "troop", "formation", folder), encoding="utf-8",
                      mode="r") as edit_file:
                rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))

                for row_index, row in enumerate(rd[1:]):
                    if any(re.search("[a-zA-Z]", i) is not None for i in
                           row) is False:  # row does not contain any text, not header
                        row = [int(item) if item != "" else 100 for item in
                               row]  # replace empty item with high number for low priority
                        self.default_formation_list[formation_name].append(row)
            self.default_formation_list[formation_name] = np.array(
                self.default_formation_list[formation_name])
        edit_file.close()

        # Effect that exist as its own sprite in battle
        self.effect_list = {}
        with open(os.path.join(self.module_dir, "troop", "effect.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ("Status Conflict", "Status", "Special Effect", "Properties")  # value in tuple only
            mod_column = ("Melee Attack Modifier", "Melee Defence Modifier", "Ranged Defence Modifier",
                          "Speed Modifier", "Accuracy Modifier", "Melee Speed Modifier", "Reload Modifier",
                          "Charge Modifier")  # need to be calculated to percentage
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column)
                self.effect_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()


class LeaderData(GameData):
    def __init__(self, images, troop_data):
        """
        For keeping all data related to leader.

        :param images: Portrait images of leaders
        :param troop_data: Troop data dict
        """
        GameData.__init__(self)
        self.images = images

        self.skill_list = {}
        for index, skill_list in enumerate(("leader_skill", "commander_skill")):
            with open(os.path.join(self.module_dir, "leader",
                                   skill_list + ".csv"), encoding="utf-8", mode="r") as edit_file:
                rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                int_column = ("Troop Type", "Range", "Area of Effect", "Cost", "Charge Skill")  # value int only
                list_column = ("Action",)
                tuple_column = ("Replace", "Status", "Enemy Status", "Effect Sprite", "AI Use Condition")
                mod_column = ("Melee Attack Modifier", "Melee Defence Modifier", "Ranged Defence Modifier", "Speed Modifier",
                              "Accuracy Modifier", "Range Modifier", "Melee Speed Modifier", "Reload Modifier", "Charge Modifier",
                              "Critical Modifier", "Damage Modifier", "Weapon Impact Modifier")
                int_column = [index for index, item in enumerate(header) if item in int_column]
                list_column = [index for index, item in enumerate(header) if item in list_column]
                tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
                mod_column = [index for index, item in enumerate(header) if item in mod_column]
                for row in rd[1:]:
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, mod_column=mod_column, list_column=list_column,
                                           tuple_column=tuple_column, int_column=int_column)
                    self.skill_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
                    self.skill_list[row[0]]["Shake Power"] = int(self.skill_list[row[0]]["Sound Distance"] / 10)
            edit_file.close()

        # Leader class dict
        self.leader_class = {}
        with open(os.path.join(self.module_dir, "leader", "leader_class.csv"),
                  encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
                        row[n] = int(i)
                self.leader_class[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Leader preset
        self.leader_list = {}
        with open(os.path.join(self.module_dir, "leader", "preset", "leader.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("Race", "Strength", "Dexterity", "Agility", "Constitution", "Intelligence",
                          "Wisdom", "Charisma", "Melee Speciality", "Range Speciality", "Cavalry Speciality",
                          "Social Class")  # value int only
            list_column = ("Skill", "Trait", "Formation")
            tuple_column = ("Primary Main Weapon", "Primary Sub Weapon", "Secondary Main Weapon",
                            "Secondary Sub Weapon", "Armour", "Mount", "Faction")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            list_column = [index for index, item in enumerate(header) if item in list_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.leader_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Add common leader to the leader list
        with open(
                os.path.join(self.module_dir, "leader", "preset", "common_leader.csv"),
                encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.leader_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        # Add leader race size to data
        for key in self.leader_list:
            self.leader_list[key]["Size"] = 1
            if self.leader_list[key]["Mount"]:
                mount_race = troop_data.mount_list[self.leader_list[key]["Mount"][0]]["Race"]
                if mount_race != 0:
                    self.leader_list[key]["Size"] = troop_data.race_list[mount_race]["Size"] / 10
                else:
                    self.leader_list[key]["size"] = troop_data.race_list[self.leader_list[key]["Race"]]["Size"] / 10

        # Leader sprite
        self.leader_sprite_list = {}
        with open(os.path.join(self.module_dir, "leader", "preset", "leader_sprite.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            for row_index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    if "," in i:
                        row[n] = i.split(",")
                self.leader_sprite_list[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
            edit_file.close()


class FactionData(GameData):
    images = []

    def __init__(self):
        """
        For keeping all data related to leader.
        """
        GameData.__init__(self)
        self.faction_list = {}
        with open(os.path.join(self.module_dir, "faction", "faction.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            for row in rd[1:]:
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

        self.faction_name_list = [value["Name"] for value in self.faction_list.values()]

        self.faction_unit_list = {}
        part_folder = Path(os.path.join(self.module_dir, "faction", "unit"))
        subdirectories = [os.sep.join(os.path.normpath(x).split(os.sep)[-1:]) for x in
                          part_folder.iterdir()]
        for folder in subdirectories:
            self.faction_unit_list[int(folder[-1])] = {}
            with open(os.path.join(self.module_dir, "faction", "unit", folder[-1],
                                   "unit.csv"), encoding="utf-8", mode="r") as edit_file:
                rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
                header = rd[0]
                for row in rd[1:]:
                    for n, i in enumerate(row):
                        if header[n] == "Troop":
                            if "," in i:
                                row[n] = i.split(",")
                            else:
                                row[n] = [i]
                            row[n] = {item.split(":")[0]:
                                          [int(item2) for item2 in item.split(":")[1].split("/")] for item in row[n]}
                    self.faction_unit_list[int(folder[-1])][row[0]] = {header[index + 1]: stuff for index, stuff in
                                                                       enumerate(row[1:])}
                    self.faction_unit_list[int(folder[-1])][row[0]]["Faction"] = int(folder[-1])  # add faction iD
                edit_file.close()

        images_old = load_images(self.module_dir, screen_scale=self.screen_scale,
                                 subfolder=("faction", "coa"))  # coa_list images list

        self.coa_list = []
        for image in images_old:
            self.coa_list.append(images_old[image])
