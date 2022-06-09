import numpy as np


def shift_line(self, how):
    """
    Shift a whole line of subunit
    :param self: Unit object
    :param how: String value of how to shift
    """
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

    self.subunit_formation_change()
