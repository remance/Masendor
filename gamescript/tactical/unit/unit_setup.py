import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def leader_position_check(self, *args):
    """
    Find position of leader, not used in tactical mode
    :param self: Battle object
    """
    return None


def split_new_unit(self, who, add_unit_list=True):
    """
    Split the unit into two units
    :param self: battle object
    :param who: unit object
    :param add_unit_list: unit list to add a new unit into
    :return:
    """
    from gamescript import battleui
    # generate subunit sprite array for inspect ui
    who.subunits_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
    found_count = 0  # for subunit_sprite index
    found_count2 = 0  # for positioning
    for row in range(0, len(who.subunit_list)):
        for column in range(0, len(who.subunit_list[0])):
            if who.subunit_list[row][column] != 0:
                who.subunits_array[row][column] = who.subunits[found_count]
                who.subunits[found_count].unit_position = (who.subunit_position_list[found_count2][0] / 10,
                                                           who.subunit_position_list[found_count2][1] / 10)  # position in unit sprite
                found_count += 1
            else:
                who.subunits_array[row][column] = None
            found_count2 += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(who.subunits):  # reset leader subunit_pos
        if this_subunit.leader is not None:
            this_subunit.leader.subunit_pos = index

    who.zoom = 11 - self.camera_zoom
    who.new_angle = who.angle

    who.start_set(self.subunit_updater)
    who.set_target(who.front_pos)

    number_pos = (who.base_pos[0] - who.base_width_box,
                  (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotation_xy(who.base_pos, number_pos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunits:
        this_subunit.start_set(this_subunit.zoom, self.subunit_animation_pool)

    if add_unit_list:
        self.all_team_unit["alive"].append(who)

    number_spite = battleui.TroopNumber(self.screen_scale, who)
    self.troop_number_sprite.add(number_spite)

