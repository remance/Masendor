import csv
import os
import sys

import pool

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
sys.path.insert(1, main_dir)

read_anim_data = pool.read_anim_data

pool = []
with open(os.path.join(main_dir, "data", "animation", "side.csv"), encoding="utf-8",
          mode="r") as edit_file:
    rd = csv.reader(edit_file, quoting=csv.QUOTE_MINIMAL)
    rd = [row for row in rd]
    part_name_header = rd[0]
    animation_pool = {}
    for row_index, row in enumerate(rd):
        if row_index > 0:
            key = row[0]
            row = row[1:]
            animation_pool[key] = {part_name_header[1:][item_index]: item.split(",") for item_index, item in enumerate(row)}
    pool = animation_pool
edit_file.close()


def frame_adjust(pool, pool_name, header, filter_list, part_anchor, exclude_filter_list=()):
    """Move every parts in animation pool of specific direction based on specific input part and desired new position"""
    for key, value in pool.items():
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
                        pool[key][key2][2] = str(float(pool[key][key2][2]) + offset[0])
                        pool[key][key2][3] = str(float(pool[key][key2][3]) + offset[1])
                    else:
                        pool[key][key2][3] = str(float(pool[key][key2][3]) + offset[0])
                        pool[key][key2][4] = str(float(pool[key][key2][4]) + offset[1])
    for key in pool:
        for key2, value in pool[key].items():
            new_value = str(pool[key][key2])
            for character in "'[]":
                new_value = new_value.replace(character, "")
            new_value = new_value.replace(", ", ",")
            pool[key][key2] = new_value
    for key in pool:
        pool[key] = [value for value in pool[key].values()]
    save_list = pool
    final_save = [[item for item in header]]
    for item in list(save_list.items()):
        final_save.append([item[0]] + item[1])
    with open(os.path.join(main_dir, "data", "animation", pool_name, "side.csv"), mode="w",
              encoding='utf-8',
              newline="") as edit_file:
        filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in final_save:
            filewriter.writerow(row)
        edit_file.close()

# frame_adjust(pool, "generic", part_name_header, ("Chariot", ), ("p4_body", (201.8, 222)), exclude_filter_list=("Die", ))