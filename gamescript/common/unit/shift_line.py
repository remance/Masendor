import numpy as np


def shift_line(self, how):
    """
    Shift a whole line of subunit
    :param self: Unit object
    :param how: String value of how to shift
    """
    print(self.subunit_id_array)
    if how == "Front To Back":  # move up and not already at top row
        index = np.array(list(range(0, len(self.subunit_id_array))))
        index = np.roll(index, -1)
        self.subunit_id_array = self.subunit_id_array[index]
    elif how == "Back To Front":  # move down and not already at bottom row
        index = np.array(list(range(0, len(self.subunit_id_array))))
        index = np.roll(index, 1)
        self.subunit_id_array = self.subunit_id_array[index]
    elif how == "Left To Right":  # move left and not already at max left column
        index = np.array(list(range(0, len(self.subunit_id_array[0]))))
        index = np.roll(index, 1)
        self.subunit_id_array = self.subunit_id_array[:, index]
    elif how == "Right To Left":  # move right and not already at max right column
        index = np.array(list(range(0, len(self.subunit_id_array[0]))))
        index = np.roll(index, -1)
        self.subunit_id_array = self.subunit_id_array[:, index]

    found_count = 0
    position_count = 0
    for row in range(0, len(self.subunit_id_array)):
        for column in range(0, len(self.subunit_id_array[0])):
            if found_count < len(self.subunit_list):
                if self.subunit_id_array[row][column] != 0:
                    print(self.subunit_id_array[row][column])
                    for subunit in self.subunit_list:
                        if self.subunit_id_array[row][column] == subunit.game_id:
                            self.subunit_object_array[row][column] = self.subunit_list[found_count]
                            subunit.unit_position = (self.subunit_position_list[position_count][0] / 10,
                                                     self.subunit_position_list[position_count][1] / 10)  # position in unit sprite
                            break
                    found_count += 1
                else:
                    self.subunit_object_array[row][column] = None
            else:
                self.subunit_object_array[row][column] = None
            position_count += 1

    self.subunit_formation_change()
