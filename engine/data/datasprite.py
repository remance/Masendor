import csv
import os
from pathlib import Path

from pygame import Vector2

from engine.utility import apply_sprite_colour, load_images, stat_convert, filename_convert_readable as fcv

direction_list = ("side",)


class TroopAnimationData:
    def __init__(self, data_dir, module_dir, race_list, team_colour):
        """
        Containing data related to troop animation sprite
        :param data_dir: Game data folder direction
        :param data_dir: Game module data folder direction
        :param race_list: List of troop races
        :param team_colour: List of team colour for colourising damage effect sprites
        """
        with open(os.path.join(data_dir, "sprite", "colour_rgb.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            self.colour_list = {}
            int_column = ["red", "green", "blue"]  # value in list only
            int_column = [index for index, item in enumerate(header) if item in int_column]
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, int_column=int_column)
                        key = row[0].split("/")[0]
                    self.colour_list[key] = row[1:]
        edit_file.close()

        self.unit_animation_data = {}
        part_folder = Path(os.path.join(module_dir, "animation"))
        files = [os.path.split(x)[-1].replace(".csv", "") for x in part_folder.iterdir() if
                 ".csv" in os.path.split(x)[-1] and "lock." not in os.path.split(x)[-1]]
        for file in files:
            with open(os.path.join(module_dir, "animation", file + ".csv"), encoding="utf-8",
                      mode="r") as edit_file:
                rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
                part_name_header = rd[0]
                list_column = ["head", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                               "l_arm_low", "l_hand", "r_leg", "r_foot", "l_leg", "l_foot", "main_weapon", "sub_weapon",
                               "special_1", "special_2", "special_3", "special_4", "special_5"]
                for p in range(1, 5):  # up to p4
                    p_name = "p" + str(p) + "_"
                    list_column += [p_name + item for item in list_column]
                list_column += ["effect_1", "effect_2", "effect_3", "effect_4", "dmg_effect_1", "dmg_effect_2",
                                "dmg_effect_3", "dmg_effect_4", "frame_property",
                                "animation_property"]  # value in list only
                list_column = [index for index, item in enumerate(part_name_header) if item in list_column]
                part_name_header = part_name_header[1:]  # keep only part name for list ref later
                animation_pool = {}
                file_data_name = fcv(file)
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
                self.unit_animation_data[file_data_name] = animation_pool
            edit_file.close()

        self.weapon_joint_list = {}
        with open(os.path.join(module_dir, "sprite", "unit", "weapon", "joint.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            list_column = direction_list  # value in list only
            list_column = [index for index, item in enumerate(header) if item in list_column]
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        row = stat_convert(row, n, i, list_column=list_column)
                        key = row[0].split("/")[0]
                    position = row[1]
                    if position == ["center"] or not position:
                        position = "center"
                    else:
                        position = Vector2(position[0], position[1])

                    self.weapon_joint_list[key] = position
            edit_file.close()

        self.body_sprite_pool = {}
        for race in race_list:
            race_file_name = fcv(race, revert=True)
            self.body_sprite_pool[race] = {}
            part_folder = Path(os.path.join(module_dir, "sprite", "unit", race_file_name))
            try:
                subdirectories = [os.path.split(os.sep.join(
                    os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for x
                    in part_folder.iterdir() if x.is_dir()]
                self.body_sprite_pool[race] = {}

                for folder in subdirectories:
                    if folder[1] != "armour":
                        imgs = load_images(module_dir, subfolder=folder, key_file_name_readable=True)
                        self.body_sprite_pool[race][folder[-1]] = imgs
                        part_subfolder = Path(os.path.join(module_dir, "sprite", "unit", race_file_name, folder[-1]))
                        sub2_directories = [os.path.split(os.sep.join(
                            os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for
                            x in part_subfolder.iterdir() if x.is_dir()]
                        for sub1_folder in sub2_directories:
                            imgs = load_images(module_dir, subfolder=sub1_folder, key_file_name_readable=True)
                            self.body_sprite_pool[race][folder[-1]][sub1_folder[-1]] = imgs
            except FileNotFoundError:
                pass

        self.armour_sprite_pool = {}
        for race in race_list:
            self.armour_sprite_pool[race] = {}
            try:
                race_file_name = fcv(race, revert=True)
                part_subfolder = Path(
                    os.path.join(module_dir, "sprite", "unit", race_file_name, "armour"))
                subdirectories = [os.path.split(os.sep.join(
                    os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for x
                    in part_subfolder.iterdir() if x.is_dir()]
                for sub1_folder in subdirectories:
                    sub1_folder_name = sub1_folder[-1]
                    sub1_folder_data_name = fcv(sub1_folder[-1])
                    part_subsubfolder = Path(
                        os.path.join(module_dir, "sprite", "unit", race_file_name, "armour",
                                     sub1_folder[-1]))
                    sub2_directories = [os.path.split(os.sep.join(
                        os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for
                        x
                        in part_subsubfolder.iterdir() if x.is_dir()]
                    if sub1_folder_data_name not in self.armour_sprite_pool[race]:
                        self.armour_sprite_pool[race][sub1_folder_data_name] = {}
                    for sub2_folder in sub2_directories:
                        sub2_folder_name = sub2_folder[-1]
                        sub2_folder_data_name = fcv(sub2_folder[-1])
                        if sub2_folder_data_name not in self.armour_sprite_pool[race][sub1_folder_data_name]:
                            self.armour_sprite_pool[race][sub1_folder_data_name][sub2_folder_data_name] = {}
                        body_subsubfolder = Path(
                            os.path.join(module_dir, "sprite", "unit", race_file_name, "armour",
                                         sub1_folder_name, sub2_folder_name))
                        body_directories = [os.path.split(os.sep.join(
                            os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):]))
                            for x
                            in body_subsubfolder.iterdir() if x.is_dir()]
                        for body_folder in body_directories:
                            imgs = load_images(module_dir,
                                               subfolder=("sprite", "unit", race_file_name, "armour",
                                                          sub1_folder_name, sub2_folder_name, body_folder[-1]),
                                               key_file_name_readable=True)
                            self.armour_sprite_pool[race][sub1_folder_data_name][sub2_folder_data_name][
                                body_folder[-1]] = imgs
            except FileNotFoundError:
                pass

        self.weapon_sprite_pool = {}
        part_folder = Path(os.path.join(module_dir, "sprite", "unit", "weapon"))
        subdirectories = [os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for x
            in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            folder_name = folder[-1]
            folder_data_name = fcv(folder[-1])
            self.weapon_sprite_pool[folder_data_name] = {}
            part_subfolder = Path(os.path.join(module_dir, "sprite", "unit", "weapon", folder_name))
            sub2_directories = [os.path.split(
                os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for
                x
                in part_subfolder.iterdir() if x.is_dir()]
            for sub1_folder in sub2_directories:
                sub1_folder_name = sub1_folder[-1]
                sub1_folder_data_name = fcv(sub1_folder[-1])
                self.weapon_sprite_pool[folder_data_name][sub1_folder_data_name] = {}
                icon_imgs = load_images(module_dir, subfolder=("sprite", "unit", "weapon",
                                                               folder_name, sub1_folder_name))
                self.weapon_sprite_pool[folder_data_name][sub1_folder_data_name]["icon"] = icon_imgs
                imgs = load_images(module_dir, subfolder=("sprite", "unit", "weapon",
                                                          folder_name, sub1_folder_name),
                                   key_file_name_readable=True)
                self.weapon_sprite_pool[folder_data_name][sub1_folder_data_name] = imgs

        self.effect_sprite_pool = {}
        self.effect_animation_pool = {}
        part_folder = Path(os.path.join(module_dir, "sprite", "effect"))
        subdirectories = [os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for x
            in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            folder_data_name = fcv(folder[-1])
            images = load_images(module_dir, subfolder=folder, key_file_name_readable=True)
            self.effect_sprite_pool[folder_data_name] = images

            self.effect_animation_pool[folder_data_name] = {}
            true_name_list = []
            for key, value in images.items():
                if key.split(" ")[-1].isdigit():
                    true_name = " ".join([string for string in key.split(" ")[:-1]]) + "#"
                else:
                    true_name = key
                true_name_list.append(true_name)

            for team in team_colour:
                for true_name in set(true_name_list):  # create effect animation list
                    if "#" in true_name:  # has animation to play
                        animation_list = [value for key, value in images.items() if true_name[:-1] ==
                                          " ".join([string for string in key.split(" ")[:-1]])]
                        if " (team)" in folder_data_name:
                            self.effect_animation_pool[folder_data_name][team] = {}
                            animation_list = [apply_sprite_colour(item, team_colour[team], keep_white=False) for
                                              item in animation_list]
                            self.effect_animation_pool[folder_data_name][team][true_name[:-1]] = tuple(animation_list)
                        else:
                            self.effect_animation_pool[folder_data_name][true_name[:-1]] = tuple(animation_list)
                    else:
                        animation_list = [value for key, value in images.items() if true_name == key]
                        if " (team)" in folder_data_name:
                            self.effect_animation_pool[folder_data_name][team] = {}
                            animation_list = [apply_sprite_colour(item, team_colour[team], keep_white=False) for
                                              item in animation_list]
                            self.effect_animation_pool[folder_data_name][team][true_name] = tuple(animation_list)
                        else:
                            self.effect_animation_pool[folder_data_name][true_name] = tuple(animation_list)

        self.status_animation_pool = {}
        part_folder = Path(os.path.join(module_dir, "sprite", "status"))
        subdirectories = [os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for x
            in part_folder.iterdir() if x.is_dir()]
        for folder in subdirectories:
            folder_data_name = fcv(folder[-1])
            images = load_images(module_dir, subfolder=folder)
            self.status_animation_pool[folder_data_name] = tuple(images.values())
