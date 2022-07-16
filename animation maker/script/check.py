import os
import sys

import pool

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\")+1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
sys.path.insert(1, main_dir)

read_anim_data = pool.read_anim_data

direction_list = ("front", "side", "back", "sideup", "sidedown")
animation_pool, part_name_header = read_anim_data(direction_list, "generic")


def check_pool():
    """Check if all animation direction has same number of frames and properties"""
    warning_list = {}
    stat_list = {}
    for index, direction in enumerate(direction_list):
        for animation, value in animation_pool[index].items():
            if animation not in warning_list:
                warning_list[animation] = {}
                stat_list[animation] = {this_direction: {"frames": 0, "frame properties": {}, } for this_direction in direction_list}
            stat_list[animation][direction]["frames"] = len(value)
            for frame_index, frame in enumerate(value):
                stat_list[animation][direction]["frame properties"][frame_index] = frame["frame_property"]
    for key, value in stat_list.items():
        race = value[0]
        action = value[-1]
        frames = {}
        props = {}

        for direction, anim_value in value.items():
            frames[direction] = anim_value["frames"]
            props[direction] = anim_value["frame properties"]
        if len(list(set(list(frames.values())))) != 1:
            warning_list[animation]["Unequal frame number"] = True
        if len(list(set(list(frames.values())))) != 1:
            warning_list[animation]["Unequal frame prop"] = True
    warning_list = {key: value for key, value in warning_list.items() if value != {}}
    print(warning_list)
    print(stat_list)


check_pool()
