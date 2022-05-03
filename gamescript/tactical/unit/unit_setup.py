import numpy as np

from gamescript.common import utility

rotation_xy = utility.rotation_xy

letter_board = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def add_unit(game_id, pos, subunit_list, colour, leader_list, leader_stat, control, coa, command, start_angle, start_hp, start_stamina,
             team):
    """
    Create unit object into the game and leader of the unit
    :param game_id: game id for the unit
    :param pos: pos of the unit in battle map
    :param subunit_list: list of subunits in the unit
    :param colour: team colour
    :param leader_list: list of leader in the unit
    :param leader_stat: leader stat data
    :param control: for checking whether player can control the unit
    :param coa: coat of arm image
    :param command: commander unit or not
    :param start_angle: starting angle of unit
    :param start_hp: starting troop number/health of the unit
    :param start_stamina: starting troop stamina of the unit
    :param team: team number
    :return: unit object
    """

    from gamescript import unit, leader
    old_subunit_list = subunit_list[~np.all(subunit_list == 0, axis=1)]  # remove whole empty column in subunit list
    subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(game_id, pos, subunit_list, colour, control, coa, command, abs(360 - start_angle), start_hp, start_stamina, team)

    # add leader
    unit.leader = [leader.Leader(leader_list[0], leader_list[4], 0, unit, leader_stat),
                   leader.Leader(leader_list[1], leader_list[5], 1, unit, leader_stat),
                   leader.Leader(leader_list[2], leader_list[6], 2, unit, leader_stat),
                   leader.Leader(leader_list[3], leader_list[7], 3, unit, leader_stat)]
    return unit


def generate_unit(self, which_army, setup_data, control, command, colour, coa, subunit_game_id, *args):
    """
    generate unit and their subunits
    :param self: battle object
    :param which_army: team group
    :param setup_data: list of data for the unit
    :param control: for checking whether player can control the unit
    :param command: commander unit or not
    :param colour: colour for their icon
    :param coa: coat of arm image
    :param subunit_game_id: starting game id for subunits
    :param args: other arguments
    :return: latest subunit game id for other unit generation
    """

    from gamescript import battleui, subunit
    this_unit = add_unit(setup_data["ID"], setup_data["POS"],
                         np.array([setup_data["Row 1"], setup_data["Row 2"], setup_data["Row 3"], setup_data["Row 4"],
                                   setup_data["Row 5"], setup_data["Row 6"], setup_data["Row 7"], setup_data["Row 8"]]),
                         colour, setup_data["Leader"] + setup_data["Leader Position"], self.leader_data, control,
                         coa, command, setup_data["Angle"], setup_data["Start Health"], setup_data["Start Stamina"],
                         setup_data["Team"])
    which_army.add(this_unit)
    army_subunit_index = 0  # army_subunit_index is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    max_column = len(this_unit.subunit_list[0])
    for subunit_number in np.nditer(this_unit.subunit_list, op_flags=["readwrite"], order="C"):
        if subunit_number != 0:
            add_subunit = subunit.Subunit(subunit_number, subunit_game_id, this_unit, this_unit.subunit_position_list[army_subunit_index],
                                          this_unit.start_hp, this_unit.start_stamina, self.unit_scale)
            self.subunit.add(add_subunit)
            add_subunit.board_pos = board_pos[army_subunit_index]
            subunit_number[...] = subunit_game_id
            this_unit.subunits_array[row][column] = add_subunit
            this_unit.subunits.append(add_subunit)
            subunit_game_id += 1
        else:
            this_unit.subunits_array[row][column] = None  # replace numpy None with python None

        column += 1
        if column == max_column:
            column = 0
            row += 1
        army_subunit_index += 1
    self.troop_number_sprite.add(battleui.TroopNumber(self.screen_scale, this_unit))  # create troop number text sprite
    return subunit_game_id


def split_new_unit(self, who, add_unit_list=True):
    """
    Split the unit into two units
    :param self: battle object
    :param who: unit object
    :param add_unit_list: unit list to add a new unit into
    :return:
    """
    from gamescript import battleui
    # generate subunit sprite array for inspect ui
    who.subunits_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
    found_count = 0  # for subunit_sprite index
    found_count2 = 0  # for positioning
    for row in range(0, len(who.subunit_list)):
        for column in range(0, len(who.subunit_list[0])):
            if who.subunit_list[row][column] != 0:
                who.subunits_array[row][column] = who.subunits[found_count]
                who.subunits[found_count].unit_position = (who.subunit_position_list[found_count2][0] / 10,
                                                           who.subunit_position_list[found_count2][1] / 10)  # position in unit sprite
                found_count += 1
            else:
                who.subunits_array[row][column] = None
            found_count2 += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(who.subunits):  # reset leader subunit_pos
        if this_subunit.leader is not None:
            this_subunit.leader.subunit_pos = index

    who.zoom = 11 - self.camera_zoom
    who.new_angle = who.angle

    who.start_set(self.subunit)
    who.set_target(who.front_pos)

    number_pos = (who.base_pos[0] - who.base_width_box,
                  (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotation_xy(who.base_pos, number_pos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunits:
        this_subunit.start_set(this_subunit.zoom)

    if add_unit_list:
        self.alive_unit_list.append(who)
        self.alive_unit_index.append(who.game_id)

    number_spite = battleui.TroopNumber(self.screen_scale, who)
    self.troop_number_sprite.add(number_spite)


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
        subunit.find_nearby_subunit()  # reset nearby subunit in the same unit
        if subunit in self.frontline_object[0]:
            subunit.frontline = True

    self.auth_penalty = 0
    for subunit in self.subunits:
        if subunit.state != 100:
            self.auth_penalty += subunit.auth_penalty  # add authority penalty of all alive subunit
