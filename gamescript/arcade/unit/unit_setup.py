import numpy as np

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


def split_new_unit(self):
    pass
