import numpy as np


def find_nearby_subunit(self):
    """Find nearby friendly squads in the same unit for applying buff"""
    self.nearby_subunit_list = []
    corner_subunit = []
    index = np.where(self.unit.subunit_id_array == self.game_id)
    row_index = index[0][0]
    column_index = index[1][0]
    if column_index > 0:  # get subunit from left if not at first column
        self.nearby_subunit_list.append(self.unit.subunit_object_array[row_index][column_index - 1])  # index 0
    else:  # not exist
        self.nearby_subunit_list.append(None)  # add None instead

    if column_index + 1 < len(self.unit.subunit_id_array[0]):  # get subunit from right if not at last column
        self.nearby_subunit_list.append(self.unit.subunit_object_array[row_index][column_index + 1])  # index 1
    else:  # not exist
        self.nearby_subunit_list.append(None)  # add None instead

    if row_index > 0:  # get top subunit
        self.nearby_subunit_list.append(self.unit.subunit_object_array[row_index - 1][column_index])  # index 2
        if column_index > 0:  # get top left subunit
            corner_subunit.append(self.unit.subunit_object_array[row_index - 1][column_index - 1])  # index 3
        else:  # not exist
            corner_subunit.append(None)  # add None instead
        if column_index + 1 < len(self.unit.subunit_id_array[0]):  # get top right
            corner_subunit.append(self.unit.subunit_object_array[row_index - 1][column_index + 1])  # index 4
        else:  # not exist
            corner_subunit.append(None)  # add None instead
    else:  # not exist
        self.nearby_subunit_list.append(None)  # add None instead

    if row_index + 1 < len(self.unit.subunit_id_array):  # get bottom subunit
        self.nearby_subunit_list.append(self.unit.subunit_object_array[row_index + 1][column_index])  # index 5
        if column_index > 0:  # get bottom left subunit
            corner_subunit.append(self.unit.subunit_object_array[row_index + 1][column_index])  # index 6
        else:  # not exist
            corner_subunit.append(None)  # add None instead
        if column_index + 1 < len(self.unit.subunit_id_array[0]):  # get bottom  right subunit
            corner_subunit.append(self.unit.subunit_object_array[row_index + 1][column_index])  # index 7
        else:  # not exist
            corner_subunit.append(None)  # add None instead
    else:  # not exist
        self.nearby_subunit_list.append(None)  # add None instead
    self.nearby_subunit_list = self.nearby_subunit_list + corner_subunit
