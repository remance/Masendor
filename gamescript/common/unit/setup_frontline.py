import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy


def setup_frontline(self):
    """
    Setup frontline array
    :param self: unit object
    """

    # reset subunit type count
    self.subunit_type_count.update((value, 0) for value in self.subunit_type_count)

    # check if completely empty side row/col, then delete and re-adjust array
    stop_loop = False
    while stop_loop is False:  # loop until no longer find completely empty row/col
        stop_loop = True
        subunit_array = self.subunit_id_array
        full_subunit_array = [subunit_array, np.fliplr(subunit_array.swapaxes(0, 1)), np.rot90(subunit_array),
                              np.fliplr([subunit_array])[0]]  # rotate the array based on the side
        subunit_array = [subunit_array[0], full_subunit_array[1][0], full_subunit_array[2][0], full_subunit_array[3][0]]
        for index, who_frontline in enumerate(subunit_array):
            if any(subunit != 0 for subunit in who_frontline) is False:  # has completely empty outer row or column, remove them
                if index == 0:  # front side
                    self.subunit_id_array = self.subunit_id_array[1:]
                elif index == 1:  # left side
                    self.subunit_id_array = np.delete(self.subunit_id_array, 0, 1)
                elif index == 2:  # right side
                    self.subunit_id_array = np.delete(self.subunit_id_array, -1, 1)
                elif index == 3:  # rear side
                    self.subunit_id_array = np.delete(self.subunit_id_array, -1, 0)

                stop_loop = False

    if len(self.subunit_id_array) > 0:  # still has row left, i.e., not completely destroyed
        old_width_box, old_height_box = self.base_width_box, self.base_height_box
        self.base_width_box, self.base_height_box = len(self.subunit_id_array[0]) * (self.image_size[0] + 10) / 20, \
                                                    len(self.subunit_id_array) * (self.image_size[1] + 2) / 20

        self.subunit_object_array = np.full(self.unit_size, None)
        for subunit in self.alive_subunit_list:
            position = np.where((self.subunit_id_array == subunit.game_id))
            self.subunit_object_array[position[0][0]][position[1][0]] = subunit
            subunit.unit_position = (self.subunit_position_list[position[0][0]][position[1][0]][0] / 10,
                                     self.subunit_position_list[position[0][0]][position[1][0]][1] / 10)  # new sprite position

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

    # Setup frontline
    got_another = True  # keep finding another subunit while true
    self.frontline_object = {0: [], 1: [], 2: [], 3: []}
    for index, who_frontline in enumerate(subunit_array):
        new_frontline = who_frontline.copy()
        dead = np.where((new_frontline == 0))  # replace the dead in frontline with other subunit in the same column
        for dead_subunit in dead[0]:
            run = 0
            while got_another:
                if full_subunit_array[index][run, dead_subunit] != 0:
                    new_frontline[dead_subunit] = full_subunit_array[index][run, dead_subunit]
                    got_another = False
                else:
                    run += 1
                    if len(full_subunit_array[index]) == run:
                        new_frontline[dead_subunit] = 0
                        got_another = False
            got_another = True  # reset for another loop
        self.frontline_object[index] = new_frontline.copy()

    for array_index, who_frontline in enumerate(list(self.frontline_object.values())):  # replace id with object
        self.frontline_object[array_index] = self.frontline_object[array_index].tolist()
        for index, stuff in enumerate(who_frontline):
            self.frontline_object[array_index][index] = None
            for subunit in self.alive_subunit_list:
                if subunit.game_id == stuff:
                    self.frontline_object[array_index][index] = subunit
                    break

    for subunit in self.alive_subunit_list:  # assign frontline variable to subunit for only front side
        subunit.frontline = False
        self.subunit_type_count[subunit.subunit_type] += 1
        subunit.find_nearby_subunit()  # reset nearby subunit in the same unit
        if subunit in self.frontline_object[0]:
            subunit.frontline = True

    self.auth_penalty = 0
    for subunit in self.alive_subunit_list:
        self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit
