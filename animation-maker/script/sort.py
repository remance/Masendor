import csv
import os
import re
import sys

import pandas as pd
from natsort import natsort_keygen

from pathlib import Path

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
sys.path.insert(1, main_dir)
data_dir = os.path.join(main_dir, "data")

module_name = "historical"
module_dir = os.path.join(data_dir, "module", module_name)

animation_folder = Path(os.path.join(module_dir, "animation"))
sub1_directories = [os.path.normpath(x).split(os.sep)[-1] for x in animation_folder.iterdir() if not x.is_dir()]


def sort_animation(pool, header, sort_by):
    name_list = list(set(pool.keys()))
    new_list = {name: name.split("_") for index, name in enumerate(name_list)}
    type_list = {}
    for key, value in new_list.items():
        race = value[0]
        action = value[-1]
        if re.search("[a-zA-Z]", action) is None:  # animation with variant
            action = value[-2] + value[-1]
        if any(ext in key for ext in ["_Main_", "_Sub_"]):
            action_type = "C"
            hand = value[2]
        elif "Preview" in key:
            action_type = "P"
        elif "_Skill_" in key:
            action_type = "S"
        elif "Default" in key:
            action_type = "A"
            hand = "0hand"
        else:
            action_type = "B"
            hand = value[1]
        type_list[key] = {"Race": race, "Hand": hand, "Type": action_type, "Action": action}
    df = pd.DataFrame.from_dict(type_list, orient="index")
    df = df.reset_index().sort_values(by=sort_by, key=natsort_keygen())

    animation_pool = {}
    for new_stuff in df["index"].tolist():
        try:
            animation_pool[new_stuff] = pool[new_stuff]
        except KeyError:
            pass
    new_pool = animation_pool

    with open(os.path.join(animation_folder, animation_race), mode="w",
              encoding='utf-8',
              newline="") as edit_file:
        filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        save_list = new_pool
        final_save = [[item for item in header]]
        for item in list(save_list.items()):
            final_save.append([item[0]] + item[1])
        for row in final_save:
            filewriter.writerow(row)
    edit_file.close()


for animation_race in sub1_directories:
    if animation_race not in ("readme.md", "template.csv"):
        with open(os.path.join(animation_folder, animation_race), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            rd = [row for row in rd]
            part_name_header = rd[0]
            animation_pool = {}
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    key = row[0]
                    row = row[1:]
                    animation_pool[key] = [item for item_index, item in enumerate(row)]
            pool = animation_pool
        edit_file.close()

        sort_animation(pool, part_name_header, ["Race", "Action", "index"])
