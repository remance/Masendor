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
        this_subunit.start_set(this_subunit.zoom)

    if add_unit_list:
        self.all_team_unit["alive"].append(who)

    number_spite = battleui.TroopNumber(self.screen_scale, who)
    self.troop_number_sprite.add(number_spite)


def setup_frontline(self):
    """Setup frontline array"""

    # v check if completely empty side row/col, then delete and re-adjust array
    stop_loop = False
    while stop_loop is False:  # loop until no longer find completely empty row/col
        stop_loop = True
        who_array = self.subunit_list
        full_who_array = [who_array, np.fliplr(who_array.swapaxes(0, 1)), np.rot90(who_array),
                        np.fliplr([who_array])[0]]  # rotate the array based on the side
        who_array = [who_array[0], full_who_array[1][0], full_who_array[2][0], full_who_array[3][0]]
        for index, who_frontline in enumerate(who_array):
            if any(subunit != 0 for subunit in who_frontline) is False:  # has completely empty outer row or column, remove them
                if index == 0:  # front side
                    self.subunit_list = self.subunit_list[1:]
                    for subunit in self.subunits:
                        subunit.unit_position = (subunit.unit_position[0], subunit.unit_position[1] - (self.image_size[1] / 8))
                elif index == 1:  # left side
                    self.subunit_list = np.delete(self.subunit_list, 0, 1)
                    for subunit in self.subunits:
                        subunit.unit_position = (subunit.unit_position[0] - (self.image_size[0] / 8), subunit.unit_position[1])
                elif index == 2:  # right side
                    self.subunit_list = np.delete(self.subunit_list, -1, 1)
                elif index == 3:  # rear side
                    self.subunit_list = np.delete(self.subunit_list, -1, 0)

                if len(self.subunit_list) > 0:  # still has row left
                    old_width_box, old_height_box = self.base_width_box, self.base_height_box
                    self.base_width_box, self.base_height_box = len(self.subunit_list[0]) * (self.image_size[0] + 10) / 20, \
                                                                len(self.subunit_list) * (self.image_size[1] + 2) / 20

                    number_pos = (self.base_pos[0] - self.base_width_box,
                                  (self.base_pos[1] + self.base_height_box))  # find position for number text
                    self.number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
                    self.change_pos_scale()

                    old_width_box = old_width_box - self.base_width_box
                    old_height_box = old_height_box - self.base_height_box
                    if index == 0:  # front
                        new_pos = (self.base_pos[0], self.base_pos[1] + old_height_box)
                    elif index == 1:  # left
                        new_pos = (self.base_pos[0] + old_width_box, self.base_pos[1])
                    elif index == 2:  # right
                        new_pos = (self.base_pos[0] - old_width_box, self.base_pos[1])
                    else:  # rear
                        new_pos = (self.base_pos[0], self.base_pos[1] - old_height_box)
                    self.base_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)
                    self.last_base_pos = self.base_pos

                    front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
                    self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
                stop_loop = False
    # ^ End check completely empty row

    got_another = True  # keep finding another subunit while true

    for index, who_frontline in enumerate(who_array):
        new_frontline = who_frontline.copy()
        dead = np.where((new_frontline == 0))  # replace the dead in frontline with other subunit in the same column
        for dead_subunit in dead[0]:
            run = 0
            while got_another:
                if full_who_array[index][run, dead_subunit] != 0:
                    new_frontline[dead_subunit] = full_who_array[index][run, dead_subunit]
                    got_another = False
                else:
                    run += 1
                    if len(full_who_array[index]) == run:
                        new_frontline[dead_subunit] = 0
                        got_another = False
            got_another = True  # reset for another loop
        empty_array = new_frontline
        new_frontline = empty_array.copy()

        self.frontline[index] = new_frontline

    self.frontline_object = self.frontline.copy()  # frontline array as object instead of index
    for array_index, who_frontline in enumerate(list(self.frontline.values())):
        self.frontline_object[array_index] = self.frontline_object[array_index].tolist()
        for index, stuff in enumerate(who_frontline):
            for subunit in self.subunits:
                if subunit.game_id == stuff:
                    self.frontline_object[array_index][index] = subunit
                    break

    for subunit in self.subunits:  # assign frontline variable to subunit for only front side
        subunit.frontline = False
        subunit.find_nearby_subunit()  # reset nearby subunit in the same unit
        if subunit in self.frontline_object[0]:
            subunit.frontline = True

    self.auth_penalty = 0
    for subunit in self.subunits:
        if subunit.state != 100:
            self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit

