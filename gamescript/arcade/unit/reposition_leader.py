import numpy as np


def reposition_leader(self, how):
    """Use static number for maximum array size here, arcade mode accept only 5x5 unit so maximum at 4"""
    leader_position = np.where(np.asarray(self.subunits_array) == self.leader_subunit)  # position of leader
    old_leader_position = ([leader_position[0][0]], [leader_position[1][0]])
    old_unit_position = (leader_position[0][0] * 5) + leader_position[1][0]

    if how == "up" and leader_position[0][0] != 0:  # move up and not already at top row
        leader_position[0][0] -= 1
    elif how == "down" and leader_position[0][0] != 4:  # move down and not already at bottom row
        leader_position[0][0] += 1
        if len(self.subunit_list) < leader_position[0][0] + 1:  # add new row
            self.subunit_list = np.vstack((self.subunit_list, np.array([0, 0, 0, 0, 0])))
    elif how == "left" and leader_position[1][0] != 0:  # move left and not already at max left column
        leader_position[1][0] -= 1
    elif how == "right" and leader_position[1][0] != 4:  # move right and not already at max right column
        leader_position[1][0] += 1
        if len(self.subunit_list[0]) < leader_position[1][0] + 1:  # add new column
            self.subunit_list = np.column_stack((self.subunit_list, np.array([0, 0, 0, 0, 0])))
    new_unit_position = (leader_position[0][0] * 5) + leader_position[1][0]

    if leader_position != old_leader_position:
        old_subunit = self.subunits_array[leader_position[0][0]][leader_position[1][0]]
        self.subunits_array[leader_position[0][0]][leader_position[1][0]] = self.leader_subunit
        self.subunits_array[old_leader_position[0][0]][old_leader_position[1][0]] = old_subunit
        self.subunit_list[leader_position[0][0]][leader_position[1][0]] = self.leader_subunit.game_id

        self.leader_subunit.unit_position = (self.subunit_position_list[new_unit_position][0] / 10,
                                             self.subunit_position_list[new_unit_position][1] / 10)
        if old_subunit is not None:
            self.subunit_list[old_leader_position[0][0]][old_leader_position[1][0]] = old_subunit.game_id
            old_subunit.unit_position = (self.subunit_position_list[old_unit_position][0] / 10,
                                         self.subunit_position_list[old_unit_position][1] / 10)
        else:
            self.subunit_list[old_leader_position[0][0]][old_leader_position[1][0]] = 0

        # old_subunit_list = self.subunit_list[~np.all(self.subunit_list == 0, axis=1)]  # remove whole empty column in subunit list
        # self.subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == 0, axis=0)]  # remove whole empty row in subunit list

        self.base_width_box, self.base_height_box = len(self.subunit_list[0]) * (self.image_size[0] + 10) / 20, \
                                                    len(self.subunit_list) * (self.image_size[1] + 2) / 20
        self.set_subunit_target()
        self.setup_frontline()
        if self.control:
            self.battle.change_inspect_subunit()
        self.input_delay = 0.5
