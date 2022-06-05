import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def leader_position_check(self, subunit_array):
    """
    Find position of leader
    :param self: Battle object
    :param subunit_array: Array of subunit
    :return: leader_position: Number position of leader from top left, return as tuple to make it compatible with other modes
    """
    leader_position = 0
    for row in subunit_array:
        for stuff in row:
            if stuff == "h":
                break
            elif stuff != "0":
                leader_position += 1
        else:
            continue
        break
    return (leader_position,)
