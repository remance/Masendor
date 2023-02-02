import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy


def setup_formation(self):
    if len(self.subunit_id_array) > 0:  # still has row left
        found_count = 0
        position_count = 0
        self.subunit_object_array = np.full(self.max_unit_size, None)
        self.subunit_hitbox_size_array = np.full(self.max_unit_size, self.battle.subunit_hitbox_size)
        for row in range(0, len(self.subunit_id_array)):
            for column in range(0, len(self.subunit_id_array[0])):
                if found_count < len(self.subunit_list):
                    if self.subunit_id_array[row][column] != 0:
                        for this_subunit in self.subunit_list:
                            if self.subunit_id_array[row][column] == this_subunit.game_id:
                                self.subunit_object_array[row][column] = this_subunit
                                self.subunit_hitbox_size_array[row][column] = this_subunit.subunit_hitbox_size
                                break
                        found_count += 1
                position_count += 1
        for this_subunit in self.alive_subunit_list:
            this_subunit.find_nearby_subunit()

        if len(self.subunit_position_list) > 0:
            old_width_box, old_height_box = find_box_size(self)
        else:
            old_width_box = 0
            old_height_box = 0

        self.setup_subunit_position_list()

        # number_pos = (self.base_pos[0] - self.unit_box_width,
        #               (self.base_pos[1] + self.unit_box_height))  # find new position for number text
        # self.base_number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
        self.base_number_pos = self.base_pos
        self.change_pos_scale()

        # Recalculate center pos of the unit since the formation/size change
        self.unit_box_width, self.unit_box_height = find_box_size(self)

        if old_width_box != 0:
            width_box_dif = old_width_box - self.unit_box_width
            height_box_dif = old_height_box - self.unit_box_height
        else:
            width_box_dif = 0
            height_box_dif = 0
        new_pos = (self.base_pos[0] + width_box_dif, self.base_pos[1] + height_box_dif)

        self.base_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)

        front_pos = (self.base_pos[0], (self.base_pos[1] - self.unit_box_height))  # find front position of unit
        self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
        number_pos = (self.base_pos[0] - self.unit_box_width,
                      (self.base_pos[1] + self.unit_box_height))  # find position for number text
        self.base_number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
        self.change_pos_scale()


def find_box_size(self):
    width_list = [item[0] for item in np.rot90(self.subunit_position_list)[0]][:len(self.subunit_id_array[0])]
    height_list = [item[1] for item in self.subunit_position_list[len(self.subunit_id_array) - 1]]

    width_hitbox_size = self.subunit_hitbox_size_array[width_list.index(max(width_list))][len(self.subunit_id_array[0]) - 1]
    height_hitbox_size = self.subunit_hitbox_size_array[len(self.subunit_id_array) - 1][height_list.index(max(height_list))]

    unit_box_width = (max(width_list) + width_hitbox_size) / 2
    unit_box_height = (max(height_list) + height_hitbox_size) / 2
    return unit_box_width, unit_box_height
