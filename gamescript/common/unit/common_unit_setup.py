import csv
import os

import numpy as np
import pygame

from gamescript.common import utility

rotation_xy = utility.rotation_xy
stat_convert = utility.stat_convert

letter_board = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)


def add_unit(game_id, pos, subunit_list, colour, leader_list, leader_pos, leader_stat, control, coa, command,
             start_angle, start_hp, start_stamina, team):
    """
    Create unit object into the game and leader of the unit
    :param game_id: game id for the unit
    :param pos: pos of the unit in battle map
    :param subunit_list: list of subunits in the unit
    :param colour: team colour
    :param leader_list: list of leader in the unit
    :param leader_pos: list of leader position
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
    old_subunit_list = subunit_list[~np.all(subunit_list == "0", axis=1)]  # remove whole empty column in subunit list
    subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == "0", axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(game_id, pos, subunit_list, colour, control, coa, command,
                     abs(360 - start_angle), start_hp, start_stamina, team)

    # add leader
    unit.leader = [leader.Leader(leader_list[index], leader_pos[index], index,
                                 unit, leader_stat) for index, _ in enumerate(leader_list)]
    return unit


def generate_unit(self, which_team, setup_data, control, command, colour, coa, subunit_game_id, troop_list):
    """
    generate unit and their subunits
    :param self: battle object
    :param which_team: team group
    :param setup_data: list of data for the unit
    :param control: for checking whether player can control the unit
    :param command: commander unit or not
    :param colour: colour for their icon
    :param coa: coat of arm image
    :param subunit_game_id: starting game id for subunits
    :param troop_list: troop data, use for checking troop size
    :param add_number: add troop number sprite in battle or not
    :return: latest subunit game id for other unit generation
    """
    from gamescript import battleui, subunit
    row_header = [header for header in setup_data if "Row " in header]
    subunit_array = np.array([setup_data[header] for header in row_header])
    leader_position = self.leader_position_check(subunit_array)
    if leader_position is None:
        leader_position = setup_data["Leader Position"]
    this_unit = add_unit(setup_data["ID"], setup_data["POS"], subunit_array,
                         colour, setup_data["Leader"], leader_position, self.leader_data, control,
                         coa, command, setup_data["Angle"], setup_data["Start Health"], setup_data["Start Stamina"],
                         setup_data["Team"])
    which_team.add(this_unit)
    army_subunit_index = 0  # army_subunit_index is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    max_column = len(this_unit.subunit_list[0])
    unit_array = np.array([[0] * self.unit_size[0]] * self.unit_size[1])  # for unit size overlap check if genre has setting
    for subunit_index, subunit_number in enumerate(np.nditer(this_unit.subunit_list, op_flags=["readwrite"], order="C")):
        now_row = int(subunit_index / len(unit_array[0]))
        now_col = subunit_index - (now_row * len(unit_array[0]))
        this_unit.subunits_array[row][column] = None  # replace numpy None with python None
        if subunit_number != "0" and (self.troop_size_adjustable is False or unit_array[now_row][now_col] == 0):
            this_subunit_number = str(subunit_number)
            size = 1
            if this_subunit_number == "h":  # Leader, only need in genre with leader as subunit itself
                this_subunit_number = this_subunit_number + str(setup_data["Leader"][0])
                size = 1  # TODO change when there is way to check leader size
            elif this_subunit_number != "0":
                size = int(troop_list[int(subunit_number)]["Size"])

            if self.troop_size_adjustable is False or (now_row + size <= 5 and now_col + size <= 5):  # skip if subunit exceed unit size array
                for row_number in range(now_row, now_row + size):
                    for col_number in range(now_col, now_col + size):
                        unit_array[row_number][col_number] = 1

                add_subunit = subunit.Subunit(this_subunit_number, subunit_game_id, this_unit,
                                              this_unit.subunit_position_list[army_subunit_index],
                                              this_unit.start_hp, this_unit.start_stamina, self.unit_scale)
                add_subunit.board_pos = board_pos[army_subunit_index]
                subunit_number[...] = subunit_game_id
                this_unit.subunits_array[row][column] = add_subunit
                this_unit.subunits.append(add_subunit)
                subunit_game_id += 1

        column += 1
        if column == max_column:
            column = 0
            row += 1
        army_subunit_index += 1
    if self.add_troop_number:
        self.troop_number_sprite.add(battleui.TroopNumber(self.screen_scale, this_unit))  # create troop number text sprite
    return subunit_game_id


def setup_unit(self, all_team_unit, troop_list, specific_team=None):
    """
    Read unit battle data from unit_pos file
    :param self: Battle or Game object
    :param all_team_unit: List of team unit group
    :param troop_list: Troop_list from troop data
    :param specific_team: Assign the unit to which specific team
    """
    from gamescript import unit
    team_colour = unit.team_colour

    main_dir = self.main_dir

    with open(os.path.join(main_dir, "data", "ruleset", self.ruleset_folder, "map",
                           self.map_selected, str(self.map_source),
                           self.genre, "unit_pos.csv"), encoding="utf-8", mode="r") as unit_file:
        rd = csv.reader(unit_file, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        header = rd[0]
        int_column = ["ID", "Faction", "Team"]  # value int only
        list_column = [item for item in header if "Row " in item] + ["POS", "Leader", "Leader Position"]  # value in list only
        float_column = ["Angle", "Start Health", "Start Stamina"]  # value in float
        int_column = [index for index, item in enumerate(header) if item in int_column]
        list_column = [index for index, item in enumerate(header) if item in list_column]
        float_column = [index for index, item in enumerate(header) if item in float_column]
        subunit_game_id = 1
        for this_unit in rd[1:]:  # skip header
            for n, i in enumerate(this_unit):
                this_unit = stat_convert(this_unit, n, i, list_column=list_column, int_column=int_column, float_column=float_column)
            this_unit = {header[index]: stuff for index, stuff in enumerate(this_unit)}
            for key, value in this_unit.items():  # convert int troop id to str for compatibility
                if "Row " in key:
                    this_unit[key] = [str(item) for item in value]
            if specific_team is None or specific_team == this_unit["Team"]:  # check player control
                control = False
                if self.team_selected == this_unit["Team"] or self.enactment:
                    control = True

                colour = team_colour[this_unit["Team"]]
                if type(all_team_unit) == dict:
                    if this_unit["Team"] not in all_team_unit:
                        all_team_unit[this_unit["Team"]] = pygame.sprite.Group()
                    which_team = all_team_unit[this_unit["Team"]]
                else:  # for character selection
                    which_team = all_team_unit

                command = False  # Not commander unit by default
                if len(which_team) == 0:  # First unit is commander
                    command = True
                coa = pygame.transform.scale(self.faction_data.coa_list[this_unit["Faction"]], (60, 60))  # get coa_list image and scale smaller to fit ui
                subunit_game_id = self.generate_unit(which_team, this_unit, control, command, colour, coa,
                                                     subunit_game_id, troop_list)
                # ^ End subunit setup

    unit_file.close()


def assign_commander(self, replace=None):
    """
    :param self: Unit object
    :param replace: New unit that is replaced as the new commander
    :return:
    """
    if replace is not None:
        self.commander = True
        self.team_commander = replace.leader[0]
    else:
        self.commander = False
        self.team_commander = self.leader[0]
        for this_unit in self.battle.all_team_unit[self.team]:
            this_unit.team_commander = self.leader[0]



def setup_frontline(self):
    """
    Setup frontline array
    :param self: unit object
    """

    # check if completely empty side row/col, then delete and re-adjust array
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

    # keep finding another subunit while true
    got_another = True

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
