import csv
import os
from pathlib import Path


def make_battle_list_data(main_dir, ruleset_folder, language):
    """Load battle map list"""
    read_folder = Path(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "map", "preset"))
    subdirectories = [x for x in read_folder.iterdir() if x.is_dir()]

    preset_map_list = []  # map name list for map selection list
    preset_map_folder = []  # folder for reading later

    for file_map in subdirectories:
        preset_map_folder.append(os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:]))
        with open(os.path.join(str(file_map), "info_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "Name":
                    preset_map_list.append(row[0])
        edit_file.close()

    # Load custom map list
    read_folder = Path(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "map", "custom"))
    subdirectories = [x for x in read_folder.iterdir() if x.is_dir()]

    custom_map_list = []
    custom_map_folder = []

    for file_map in subdirectories:
        custom_map_folder.append(os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:]))
        with open(os.path.join(str(file_map), "info_" + language + ".csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "Name":
                    custom_map_list.append(row[0])
        edit_file.close()

    return preset_map_list, preset_map_folder, custom_map_list, custom_map_folder
