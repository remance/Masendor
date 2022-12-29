import csv
import os
import re
import sys

import pool

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
sys.path.insert(1, main_dir)

read_anim_data = pool.read_anim_data

direction_list = ("front", "side", "back", "sideup", "sidedown")

pool = []
for direction in direction_list:
    with open(os.path.join(main_dir, "data", "animation", "generic", direction + ".csv"), encoding="utf-8",
              mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        part_name_header = rd[0]
        animation_pool = {}
        for row_index, row in enumerate(rd):
            if row_index > 0:
                key = row[0]
                row = row[1:]
                animation_pool[key] = {part_name_header[1:][item_index]: item.split(",") for item_index, item in enumerate(row)}
        pool.append(animation_pool)
    edit_file.close()


def frame_adjust(pool, pool_name, header, filter_list, direction, part_anchor, exclude_filter_list=()):
    """Move every parts in animation pool of specific direction based on specific input part and desired new position"""
    for index, this_direction in enumerate(direction_list):
        if this_direction == direction:
            for key, value in pool[index].items():
                match = False
                for this_filter in filter_list:
                    if this_filter in key:
                        match = True
                for this_filter in exclude_filter_list:
                    if this_filter in key:
                        match = False
                if match:
                    if type(value[part_anchor[0]]) == list and len(value[part_anchor[0]]) > 1:
                        if "weapon" in part_anchor:
                            pos = (float(value[part_anchor[0]][2]), float(value[part_anchor[0]][3]))
                        else:
                            pos = (float(value[part_anchor[0]][3]), float(value[part_anchor[0]][4]))
                        offset = (part_anchor[1][0] - pos[0], part_anchor[1][1] - pos[1])
                    for key2, value2 in value.items():
                        if "property" not in key2 and type(value[key2]) == list and len(value[key2]) > 1:
                            if "weapon" in key2:
                                pool[index][key][key2][2] = str(float(pool[index][key][key2][2]) + offset[0])
                                pool[index][key][key2][3] = str(float(pool[index][key][key2][3]) + offset[1])
                            else:
                                pool[index][key][key2][3] = str(float(pool[index][key][key2][3]) + offset[0])
                                pool[index][key][key2][4] = str(float(pool[index][key][key2][4]) + offset[1])

    for index, this_direction in enumerate(direction_list):
        if this_direction == direction:
            for key in pool[index]:
                for key2, value in pool[index][key].items():
                    new_value = str(pool[index][key][key2])
                    for character in "'[]":
                        new_value = new_value.replace(character, "")
                    new_value = new_value.replace(", ", ",")
                    pool[index][key][key2] = new_value
            for key in pool[index]:
                pool[index][key] = [value for value in pool[index][key].values()]
            save_list = pool[index]
            final_save = [[item for item in header]]
            for item in list(save_list.items()):
                final_save.append([item[0]] + item[1])
            with open(os.path.join(main_dir, "data", "animation", pool_name, this_direction + ".csv"), mode="w",
                      encoding='utf-8',
                      newline="") as edit_file:
                filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
                for row in final_save:
                    filewriter.writerow(row)
                edit_file.close()

frame_adjust(pool, "generic", part_name_header, ("Chariot", ), "back", ("p4_body", (201.8, 222)), exclude_filter_list=("Die", ))