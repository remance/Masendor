import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy


def setup_formation(self):
    if len(self.subunit_id_array) > 0:  # still has row left
        old_width_box, old_height_box = self.base_width_box, self.base_height_box
        self.base_width_box, self.base_height_box = len(self.subunit_id_array[0]) * (self.image_size[0] + 10) / 20, \
                                                    len(self.subunit_id_array) * (self.image_size[1] + 2) / 20

        found_count = 0
        position_count = 0
        self.subunit_object_array = np.full(self.unit_size, None)
        for row in range(0, len(self.subunit_id_array)):
            for column in range(0, len(self.subunit_id_array[0])):
                if found_count < len(self.subunit_list):
                    if self.subunit_id_array[row][column] != 0:
                        for this_subunit in self.subunit_list:
                            if self.subunit_id_array[row][column] == this_subunit.game_id:
                                self.subunit_object_array[row][column] = this_subunit
                                this_subunit.unit_position = (self.subunit_position_list[row][column][0] / 10,
                                                              self.subunit_position_list[row][column][
                                                                  1] / 10)  # position in unit sprite
                                break
                        found_count += 1
                position_count += 1
        for this_subunit in self.alive_subunit_list:
            this_subunit.find_nearby_subunit()

        number_pos = (self.base_pos[0] - self.base_width_box,
                      (self.base_pos[1] + self.base_height_box))  # find new position for number text
        self.number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
        self.change_pos_scale()

        # Recalculate center pos for unit since the formation/size of unit change
        width_box_dif = old_width_box - self.base_width_box
        height_box_dif = old_height_box - self.base_height_box
        new_pos = (self.base_pos[0] + width_box_dif, self.base_pos[1] + height_box_dif)

        self.base_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)
        self.last_base_pos = self.base_pos

        front_pos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find front position of unit
        self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
