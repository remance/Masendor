import csv
import os
from pathlib import Path

import pygame
from gamescript.common import utility

load_textures = utility.load_textures
stat_convert = utility.stat_convert

direction_list = ("front", "side", "back", "sideup", "sidedown")


class TroopAnimationData:
    def __init__(self, main_dir, race_list):
        """
        Containing data related to troop animation sprite
        :param main_dir: Game folder direction
        :param race_list: List of troop races
        """
        with open(os.path.join(main_dir, "data", "sprite", "generic", "skin_colour_rgb.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            self.skin_colour_list = {}
            int_column = ["red", "green", "blue"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, int_column=int_column)
                        key = row[0].split("/")[0]
                    self.skin_colour_list[key] = row[1:]
        edit_file.close()

        with open(os.path.join(main_dir, "data", "sprite", "generic", "hair_colour_rgb.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            self.hair_colour_list = {}
            int_column = ["red", "green", "blue"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, int_column=int_column)
                        key = row[0].split("/")[0]
                    self.hair_colour_list[key] = row[1:]
        edit_file.close()

        self.generic_animation_pool = []
        for direction in direction_list:
            with open(os.path.join(main_dir, "data", "animation", "generic", direction + ".csv"), encoding="utf-8",
                      mode="r") as edit_file:
                rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
                rd = [row for row in rd]
                part_name_header = rd[0]
                list_column = ["head", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                               "l_arm_low", "l_hand", "r_leg", "r_foot", "l_leg", "l_foot", "main_weapon", "sub_weapon"]
                for p in range(1, 5):  # up to p4
                    p_name = "p" + str(p) + "_"
                    list_column += [p_name + item for item in list_column]
                list_column += ["effect_1", "effect_2", "effect_3", "effect_4", "dmg_effect_1", "dmg_effect_2",
                                "dmg_effect_3", "dmg_effect_4", "special_1", "special_2", "special_3", "special_4",
                                "special_5", "special_6", "special_7", "special_8", "special_9",
                                "special_10", "frame_property", "animation_property"]  # value in list only
                list_column = [index for index, item in enumerate(part_name_header) if item in list_column]
                part_name_header = part_name_header[1:]  # keep only part name for list ref later
                animation_pool = {}
                for row_index, row in enumerate(rd):
                    if row_index > 0:
                        key = row[0].split("/")[0]
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, list_column=list_column)
                        row = row[1:]
                        if key in animation_pool:
                            animation_pool[key].append(
                                {part_name_header[item_index]: item for item_index, item in enumerate(row)})
                        else:
                            animation_pool[key] = [
                                {part_name_header[item_index]: item for item_index, item in enumerate(row)}]
                self.generic_animation_pool.append(animation_pool)
            edit_file.close()

        # self.skel_joint_list = []
        # print(race_list)
        # for race in race_list:
        #     try:
        #         for direction in direction_list:
        #             with open(os.path.join(main_dir, "data", "sprite", "generic", race, direction, "skeleton_link.csv"), encoding="utf-8",
        #                       mode="r") as edit_file:
        #                 rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        #                 rd = [row for row in rd]
        #                 header = rd[0]
        #                 list_column = ("Position", )  # value in list only
        #                 list_column = [index for index, item in enumerate(header) if item in list_column]
        #                 joint_list = {}
        #                 for row_index, row in enumerate(rd):
        #                     if row_index > 0:
        #                         for n, i in enumerate(row):
        #                             row = stat_convert(row, n, i, list_column=list_column)
        #                             key = row[0].split("/")[0]
        #                         if key in joint_list:
        #                             joint_list[key].append({row[1:][0]: pygame.Vector2(row[1:][1])})
        #                         else:
        #                             joint_list[key] = [{row[1:][0]: pygame.Vector2(row[1:][1])}]
        #                 self.skel_joint_list.append(joint_list)
        #             edit_file.close()
        #     except FileNotFoundError:  # file not exist
        #         pass

        self.weapon_joint_list = {}
        for direction_index, direction in enumerate(direction_list):
            self.weapon_joint_list[direction] = {}
            with open(os.path.join(main_dir, "data", "sprite", "generic", "weapon", "joint.csv"), encoding="utf-8",
                      mode="r") as edit_file:
                rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
                rd = [row for row in rd]
                header = rd[0]
                list_column = direction_list  # value in list only
                list_column = [index for index, item in enumerate(header) if item in list_column]
                for row_index, row in enumerate(rd):
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, list_column=list_column)
                            key = row[0].split("/")[0]
                        position = row[direction_index + 1]
                        if position == ["center"] or position == [""]:
                            position = "center"
                        else:
                            position = pygame.Vector2(position[0], position[1])

                        self.weapon_joint_list[direction][key] = position
            edit_file.close()

        self.gen_body_sprite_pool = {}
        for race in race_list:
            self.gen_body_sprite_pool[race] = {}
            for direction in direction_list:
                part_folder = Path(os.path.join(main_dir, "data", "sprite", "generic", race, direction))
                try:
                    subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if
                                      x.is_dir()]
                    self.gen_body_sprite_pool[race][direction] = {}
                    for folder in subdirectories:
                        imgs = load_textures(main_dir, folder)
                        self.gen_body_sprite_pool[race][direction][folder[-1]] = imgs
                except FileNotFoundError:
                    pass

        self.gen_armour_sprite_pool = {}
        for race in race_list:
            self.gen_armour_sprite_pool[race] = {}
            for direction in direction_list:
                try:
                    part_subfolder = Path(
                        os.path.join(main_dir, "data", "sprite", "generic", race, direction, "armour"))
                    subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_subfolder.iterdir() if
                                      x.is_dir()]
                    for subfolder in subdirectories:
                        part_subsubfolder = Path(
                            os.path.join(main_dir, "data", "sprite", "generic", race, direction, "armour",
                                         subfolder[-1]))
                        subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in part_subsubfolder.iterdir()
                                             if
                                             x.is_dir()]
                        if subfolder[-1] not in self.gen_armour_sprite_pool[race]:
                            self.gen_armour_sprite_pool[race][subfolder[-1]] = {}
                        for subsubfolder in subsubdirectories:
                            if subsubfolder[-1] not in self.gen_armour_sprite_pool[race][subfolder[-1]]:
                                self.gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]] = {}
                            self.gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]][direction] = {}
                            body_subsubfolder = Path(
                                os.path.join(main_dir, "data", "sprite", "generic", race, direction, "armour",
                                             subfolder[-1], subsubfolder[-1]))
                            body_directories = [str(x).split("data\\")[1].split("\\") for x in
                                                body_subsubfolder.iterdir()
                                                if x.is_dir()]
                            for body_folder in body_directories:
                                imgs = load_textures(main_dir,
                                                     ["sprite", "generic", race, direction, "armour", subfolder[-1],
                                                      subsubfolder[-1], body_folder[-1]])
                                self.gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]][direction][
                                    body_folder[-1]] = imgs
                except FileNotFoundError:
                    pass

        self.gen_weapon_sprite_pool = {}
        part_folder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon"))
        subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            self.gen_weapon_sprite_pool[folder[-1]] = {}
            part_subfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon", folder[-1]))
            subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in part_subfolder.iterdir() if x.is_dir()]
            for subfolder in subsubdirectories:
                self.gen_weapon_sprite_pool[folder[-1]][subfolder[-1]] = {}
                for direction in direction_list:
                    imgs = load_textures(main_dir,
                                         ["sprite", "generic", "weapon", folder[-1], subfolder[-1], direction])
                    if direction not in self.gen_weapon_sprite_pool[folder[-1]]:
                        self.gen_weapon_sprite_pool[folder[-1]][subfolder[-1]][direction] = imgs
                    else:
                        self.gen_weapon_sprite_pool[folder[-1]][subfolder[-1]][direction].update(imgs)


class EffectSpriteData:
    def __init__(self, main_dir):
        self.effect_sprite_pool = {}
        part_folder = Path(os.path.join(main_dir, "data", "sprite", "effect"))
        subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            self.effect_sprite_pool[folder[-1]] = {}
            part_folder = Path(os.path.join(main_dir, "data", "sprite", "effect", folder[-1]))
            subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
            for subfolder in subsubdirectories:
                images = load_textures(main_dir, subfolder)
                self.effect_sprite_pool[folder[-1]][subfolder[-1]] = images
