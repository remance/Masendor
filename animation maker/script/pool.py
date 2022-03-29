import os
import sys
import csv
import pygame

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\")+1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
sys.path.insert(1, main_dir)

from gamescript import statdata

stat_convert = statdata.stat_convert


def read_anim_data(direction_list, pool_type):
    pool = []
    for direction in direction_list:
        with open(os.path.join(main_dir, "data", "animation", pool_type, direction + ".csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            part_name_header = rd[0]
            list_column = ["p1_head", "p1_face", "p1_body", "p1_r_arm_up", "p1_r_arm_low", "p1_r_hand", "p1_l_arm_up",
                           "p1_l_arm_low", "p1_l_hand", "p1_r_leg", "p1_r_foot", "p1_l_leg", "p1_l_foot",
                           "p1_main_weapon", "p1_sub_weapon", "p2_head", "p2_face", "p2_body", "p2_r_arm_up",
                           "p2_r_arm_low", "p2_r_hand",
                           "p2_l_arm_up", "p2_l_arm_low", "p2_l_hand", "p2_r_leg", "p2_r_foot", "p2_l_leg",
                           "p2_l_foot", "p2_main_weapon", "p2_sub_weapon", "effect_1", "effect_2", "dmg_effect_1",
                           "dmg_effect_2",
                           "frame_property", "animation_property", "special_1", "special_2", "special_3", "special_4",
                           "special_5"]  # value in list only
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
            pool.append(animation_pool)
            part_name_header = [item for item in part_name_header if item != "effect" and "property" not in item]
        edit_file.close()
    return pool, part_name_header


def read_joint_data(direction_list, race_list, race_accept):
    skel_joint_list = []
    for race in race_list:
        if race in race_accept:
            for direction in direction_list:
                with open(os.path.join(main_dir, "data", "sprite", "generic", race, direction, "skeleton_link.csv"),
                          encoding="utf-8",
                          mode="r") as edit_file:
                    rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
                    rd = [row for row in rd]
                    header = rd[0]
                    list_column = ["Position"]  # value in list only
                    list_column = [index for index, item in enumerate(header) if item in list_column]
                    joint_list = {}
                    for row_index, row in enumerate(rd):
                        if row_index > 0:
                            for n, i in enumerate(row):
                                row = stat_convert(row, n, i, list_column=list_column)
                                key = row[0].split("/")[0]
                            if key in joint_list:
                                joint_list[key].append({row[1:][0]: pygame.Vector2(row[1:][1])})
                            else:
                                joint_list[key] = [{row[1:][0]: pygame.Vector2(row[1:][1])}]
                    skel_joint_list.append(joint_list)
                edit_file.close()

    weapon_joint_list = []
    for direction_index, direction in enumerate(direction_list):
        with open(os.path.join(main_dir, "data", "sprite", "generic", "weapon", "joint.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            header = rd[0]
            list_column = direction_list
            list_column = [index for index, item in enumerate(header) if item in list_column]
            joint_list = {}
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

                    if key in joint_list:
                        joint_list[key].append({row[0]: position})
                    else:
                        joint_list[key] = [{row[0]: position}]
            weapon_joint_list.append(joint_list)
        edit_file.close()
    return skel_joint_list, weapon_joint_list


def anim_to_pool(animation_name, pool, char, activate_list, new=False, replace=None, duplicate=None):
    """Add animation to animation pool data"""
    if replace is not None:  # rename animation
        for direction in range(0, 5):
            pool[direction] = {animation_name if k == replace else k: v for k, v in pool[direction].items()}
    if duplicate is not None:
        for direction in range(0, 5):
            pool[direction][animation_name] = pool[direction][duplicate]
    else:
        if animation_name not in pool[0]:
            for direction in range(0, 5):
                pool[direction][animation_name] = []
        if new:
            for direction in range(0, 5):
                pool[direction][animation_name] = [frame for index, frame in enumerate(char.frame_list) if frame != {} and activate_list[index]]
        else:
            pool[char.side][animation_name] = [frame for index, frame in enumerate(char.frame_list) if frame != {} and activate_list[index]]


def anim_save_pool(pool, pool_name, direction_list, anim_column_header):
    """Save animation pool data"""
    for index, direction in enumerate(direction_list):
        with open(os.path.join(main_dir, "data", "animation", pool_name, direction + ".csv"), mode="w", encoding='utf-8', newline="") as edit_file:
            filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
            save_list = pool[index]
            final_save = [[item for item in anim_column_header]]
            for item in list(save_list.items()):
                for frame_num, frame in enumerate(item[1]):
                    subitem = [tiny_item for tiny_item in list(frame.values())]
                    for item_index, min_item in enumerate(subitem):
                        if type(min_item) == list:
                            new_item = str(min_item)
                            for character in "'[] ":
                                new_item = new_item.replace(character, '')
                            subitem[item_index] = new_item
                    new_item = [item[0] + "/" + str(frame_num)] + subitem
                    final_save.append(new_item)
            for row in final_save:
                filewriter.writerow(row)
        edit_file.close()


def anim_del_pool(pool, animation_name):
    """Delete animation from animation pool data"""
    if animation_name in pool[0]:
        for direction in range(0, 5):
            try:
                del pool[direction][animation_name]
            except:
                pass
