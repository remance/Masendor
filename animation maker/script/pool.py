import csv
import os
import sys
from pathlib import Path

import pygame

current_dir = os.path.split(os.path.abspath(__file__))[0]

main_dir = os.sep.join(os.path.normpath(current_dir).split(os.sep)[
                       :-2])  # two folder further back, comment out if data in same folder as animation maker
sys.path.insert(1, main_dir)

from gamescript import datastat

stat_convert = datastat.stat_convert


def read_anim_data(anim_column_header):
    pool = {}
    part_folder = Path(os.path.join(main_dir, "data", "animation"))
    files = [os.path.split(x)[-1].replace(".csv", "") for x in part_folder.iterdir() if ".csv" in os.path.split(x)[-1]]
    for file in files:
        with open(os.path.join(main_dir, "data", "animation", file + ".csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            part_name_header = rd[0]
            list_column = anim_column_header  # value in list only
            list_exclude = ["Name", "size", "eye", "mouth"]
            list_column = [item for item in list_column if
                           item not in list_exclude and any(ext in item for ext in list_exclude) is False]
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
            pool[file] = animation_pool
            part_name_header = [item for item in part_name_header if item != "effect" and "property" not in item]
            edit_file.close()
    return pool, part_name_header


def read_joint_data():
    with open(os.path.join(main_dir, "data", "sprite", "subunit", "weapon", "joint.csv"), encoding="utf-8",
              mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        header = rd[0]
        list_column = ["side"]
        list_column = [index for index, item in enumerate(header) if item in list_column]
        joint_list = {}
        for row_index, row in enumerate(rd):
            if row_index > 0:
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column)
                    key = row[0].split("/")[0]
                position = row[1]
                if position == ["center"] or not position:
                    position = "center"
                else:
                    position = pygame.Vector2(position[0], position[1])

                joint_list[key] = position
        weapon_joint_list = joint_list
    edit_file.close()
    return weapon_joint_list


def anim_to_pool(animation_name, pool, char, activate_list, new=False, replace=None, duplicate=None):
    """Add animation to animation pool data"""
    if replace is not None:  # rename animation
        pool[animation_name] = pool.pop(replace)
    elif duplicate is not None:
        pool[animation_name] = [
            {key: [small_value for small_value in value] if type(value) == list else value for key, value in
             this_frame.items()} for this_frame in pool[duplicate]]
    else:
        if animation_name not in pool:
            pool[animation_name] = []
        if new:
            pool[animation_name] = [frame for index, frame in enumerate(char.frame_list) if
                                    frame != {} and activate_list[index]]
        else:
            pool[animation_name] = [frame for index, frame in enumerate(char.frame_list) if
                                    frame != {} and activate_list[index]]


def anim_save_pool(pool, race_name, anim_column_header):
    """Save animation pool data"""
    with open(os.path.join(main_dir, "data", "animation", race_name + ".csv"), mode="w",
              encoding='utf-8', newline="") as edit_file:
        filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        save_list = pool
        final_save = [[item for item in anim_column_header]]
        for item in list(save_list.items()):
            for frame_num, frame in enumerate(item[1]):
                subitem = [tiny_item for tiny_item in list(frame.values())]
                for item_index, min_item in enumerate(subitem):
                    if type(min_item) == list:
                        min_item = [this_item if type(this_item) != float else round(this_item, 1) for this_item in
                                    min_item]
                        new_item = str(min_item)
                        for character in "'[]":
                            new_item = new_item.replace(character, "")
                        new_item = new_item.replace(", ", ",")
                        subitem[item_index] = new_item
                new_item = [item[0] + "/" + str(frame_num)] + subitem
                final_save.append(new_item)
        for row in final_save:
            filewriter.writerow(row)
        edit_file.close()


def anim_del_pool(pool, animation_name):
    """Delete animation from animation pool data"""
    if animation_name in pool:
        del pool[animation_name]

