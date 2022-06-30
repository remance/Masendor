import numpy as np

from gamescript.common import utility

stat_convert = utility.stat_convert

letter_board = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)


def generate_unit(self, which_team, setup_data, control, command, colour, coa, subunit_game_id, troop_list):
    """
    generate unit and their subunits
    :param self: Battle object
    :param which_team: Team group
    :param setup_data: List of data for the unit
    :param control: For checking whether player can control the unit
    :param command: Commander unit or not
    :param colour: Colour for their icon
    :param coa: Coat of arm image
    :param subunit_game_id: Starting game id for subunits
    :param troop_list: Troop data, use for checking troop size
    :return: Latest subunit game id for other unit generation
    """
    from gamescript import battleui, subunit, unit, leader
    row_header = [header for header in setup_data if "Row " in header]
    subunit_array = np.array([setup_data[header] for header in row_header])
    leader_position = self.leader_position_check(subunit_array)
    if leader_position is None:
        leader_position = setup_data["Leader Position"]

    old_subunit_list = subunit_array[~np.all(subunit_array == "0", axis=1)]  # remove whole empty column in subunit list
    subunit_array = old_subunit_list[:, ~np.all(old_subunit_list == "0", axis=0)]  # remove whole empty row in subunit list
    this_unit = unit.Unit(setup_data["ID"], setup_data["POS"], subunit_array, colour, control, coa, command,
                          abs(360 - setup_data["Angle"]), setup_data["Start Health"], setup_data["Start Stamina"],
                          setup_data["Team"])

    # Add leader
    this_unit.leader = [leader.Leader(setup_data["Leader"][index], leader_position[index], index,
                                      this_unit, self.leader_data) for index, _ in enumerate(setup_data["Leader"])]

    which_team.add(this_unit)
    army_subunit_index = 0  # army_subunit_index is list index for subunit list in a specific army

    # Setup subunit in unit to subunit group
    unit_array = np.array([[0] * self.unit_size[0]] * self.unit_size[1])  # for unit size overlap check if genre has setting
    new_subunit_list = np.array([[0] * len(this_unit.subunit_id_array[0])] * len(this_unit.subunit_id_array))
    for row_index, row in enumerate(this_unit.subunit_id_array):
        for col_index, col in enumerate(row):
            if col != "0" and (self.troop_size_adjustable is False or unit_array[row_index][col_index] == 0):
                this_subunit_number = col
                size = 1
                if this_subunit_number == "h":  # Leader, only need in genre with leader as subunit itself
                    this_subunit_number = this_subunit_number + str(setup_data["Leader"][0])
                    size = 1  # TODO change when there is way to check leader size
                elif this_subunit_number != "0":
                    size = int(round(int(troop_list[int(col)]["Size"]) / 10, 0))
                    if size == 0:
                        size = 1
                    elif size > 5:
                        size = 5

                if self.troop_size_adjustable is False or (row_index + size <= 5 and col_index + size <= 5):  # skip if subunit exceed unit size array
                    for row_number in range(row_index, row_index + size):
                        for col_number in range(col_index, col_index + size):
                            unit_array[row_number][col_number] = 1

                    add_subunit = subunit.Subunit(this_subunit_number, subunit_game_id, this_unit,
                                                  this_unit.subunit_position_list[row_index][col_index],
                                                  this_unit.start_hp, this_unit.start_stamina, self.unit_scale)
                    add_subunit.board_pos = board_pos[army_subunit_index]
                    new_subunit_list[row_index][col_index] = add_subunit.game_id
                    this_unit.subunit_object_array[row_index][col_index] = add_subunit
                    this_unit.subunit_list.append(add_subunit)
                    subunit_game_id += 1

            army_subunit_index += 1
    this_unit.subunit_id_array = new_subunit_list
    if self.add_troop_number_sprite:
        self.troop_number_sprite.add(battleui.TroopNumber(self.screen_scale, this_unit))  # create troop number text sprite
    return subunit_game_id

