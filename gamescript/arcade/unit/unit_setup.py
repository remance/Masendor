import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy

letter_board = ("a", "b", "c", "d", "e")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def add_unit(game_id, pos, subunit_list, colour, leader_list, leader_stat, control, coa, command, start_angle,
             start_hp, start_stamina, team):
    """Create unit object into the battle and leader of the unit"""
    from gamescript import unit, leader
    old_subunit_list = subunit_list[~np.all(subunit_list == "0", axis=1)]  # remove whole empty column in subunit list
    subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == "0", axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(game_id, pos, subunit_list, colour, control, coa, command,
                     abs(360 - start_angle), start_hp, start_stamina, team)

    # add leader
    unit.leader = [leader.Leader(leader_list[0][0], leader_list[1], 0, unit, leader_stat)]
    return unit


def generate_unit(self, which_army, setup_data, control, command, colour, coa, subunit_game_id, troop_list, *args):
    """generate unit"""
    from gamescript import battleui, subunit
    subunit_array = np.array([setup_data["Row 1"], setup_data["Row 2"], setup_data["Row 3"], setup_data["Row 4"],
                              setup_data["Row 5"]])
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
    this_unit = add_unit(setup_data["ID"], setup_data["POS"], subunit_array,
                         colour, (setup_data["Leader"], leader_position), self.leader_data, control,
                         coa, command, setup_data["Angle"], setup_data["Start Health"], setup_data["Start Stamina"],
                         setup_data["Team"])
    which_army.add(this_unit)
    army_subunit_index = 0  # army_subunit_index is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    unit_array = np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])  # for unit size overlap check
    max_column = len(this_unit.subunit_list[0])
    for subunit_index, subunit_number in enumerate(np.nditer(this_unit.subunit_list, op_flags=["readwrite"], order="C")):
        now_row = int(subunit_index / 5)
        now_col = subunit_index - (now_row * 5)
        this_unit.subunits_array[row][column] = None  # replace numpy None with python None
        if subunit_number != 0 and unit_array[now_row][now_col] == 0:  # skip if there is already subunit occupy the slot
            if "h" not in subunit_number:
                size = int(troop_list[int(subunit_number)]["Size"])
            else:
                size = 1  # TODO change when there is way to check leader size
            if now_row + size <= 5 and now_col + size <= 5:  # skip if subunti exceed unit size array
                for row_number in range(now_row, now_row + size):
                    for col_number in range(now_col, now_col + size):
                        unit_array[row_number][col_number] = 1
                this_subunit_number = str(subunit_number)
                if this_subunit_number == "h":  # Leader
                    this_subunit_number = this_subunit_number + str(setup_data["Leader"][0])
                add_subunit = subunit.Subunit(this_subunit_number, subunit_game_id, this_unit, this_unit.subunit_position_list[army_subunit_index],
                                              this_unit.start_hp, this_unit.start_stamina, self.unit_scale, self.genre)
                self.subunit.add(add_subunit)
                subunit_number[...] = subunit_game_id
                this_unit.subunits_array[row][column] = add_subunit
                this_unit.subunits.append(add_subunit)
                subunit_game_id += 1

        column += 1
        if column == max_column:
            column = 0
            row += 1
        army_subunit_index += 1
    return subunit_game_id


def split_new_unit(self):
    pass


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
        if subunit in self.frontline_object[0]:
            subunit.frontline = True

    self.auth_penalty = 0
    for subunit in self.subunits:
        if subunit.state != 100:
            self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit
