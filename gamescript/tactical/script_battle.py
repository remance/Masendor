import csv
import os
import random

import numpy as np
import pygame

from gamescript.tactical.script_other import board_pos

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def check_split(self, who):
    """Check if unit can be splitted, if not remove splitting button"""
    # v split by middle column
    if np.array_split(who.subunit_list, 2, axis=1)[0].size >= 10 and np.array_split(who.subunit_list, 2, axis=1)[1].size >= 10 and \
            who.leader[1].name != "None":  # can only split if both unit size will be larger than 10 and second leader exist
        self.battle_ui.add(self.col_split_button)
    elif self.col_split_button in self.battle_ui:
        self.battle_ui.remove(self.col_split_button)
    # ^ End col

    # v split by middle row
    if np.array_split(who.subunit_list, 2)[0].size >= 10 and np.array_split(who.subunit_list, 2)[1].size >= 10 and \
            who.leader[1].name != "None":
        self.battle_ui.add(self.row_split_button)
    elif self.row_split_button in self.battle_ui:
        self.battle_ui.remove(self.row_split_button)


def add_unit(subunitlist, position, gameid, colour, leaderlist, leaderstat, control, coa, command, startangle, starthp, startstamina, team):
    """Create unit object into the battle and leader of the unit"""
    from gamescript import unit, leader
    oldsubunitlist = subunitlist[~np.all(subunitlist == 0, axis=1)]  # remove whole empty column in subunit list
    subunitlist = oldsubunitlist[:, ~np.all(oldsubunitlist == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(position, gameid, subunitlist, colour, control, coa, command, abs(360 - startangle), starthp, startstamina, team)

    # add leader
    unit.leader = [leader.Leader(leaderlist[0], leaderlist[4], 0, unit, leaderstat),
                   leader.Leader(leaderlist[1], leaderlist[5], 1, unit, leaderstat),
                   leader.Leader(leaderlist[2], leaderlist[6], 2, unit, leaderstat),
                   leader.Leader(leaderlist[3], leaderlist[7], 3, unit, leaderstat)]
    return unit


def generate_unit(battle, which_army, row, control, command, colour, coa, subunit_game_id):
    """generate unit data into self object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript import unit, subunit
    this_unit = add_unit(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                         colour, row[10] + row[11], battle.leader_stat, control,
                         coa, command, row[13], row[14], row[15], row[16])
    which_army.add(this_unit)
    army_subunit_index = 0  # army_subunit_index is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    max_column = len(this_unit.subunit_list[0])
    for subunit_number in np.nditer(this_unit.subunit_list, op_flags=["readwrite"], order="C"):
        if subunit_number != 0:
            add_subunit = subunit.Subunit(subunit_number, subunit_game_id, this_unit, this_unit.subunit_position_list[army_subunit_index],
                                         this_unit.start_hp, this_unit.start_stamina, battle.unitscale, battle.genre)
            battle.subunit.add(add_subunit)
            add_subunit.board_pos = board_pos[army_subunit_index]
            subunit_number[...] = subunit_game_id
            this_unit.subunit_sprite_array[row][column] = add_subunit
            this_unit.subunit_sprite.append(add_subunit)
            subunit_game_id += 1
        else:
            this_unit.subunit_sprite_array[row][column] = None  # replace numpy None with python None

        column += 1
        if column == max_column:
            column = 0
            row += 1
        army_subunit_index += 1
    battle.troop_number_sprite.add(unit.TroopNumber(battle.screen_scale, this_unit))  # create troop number text sprite

    return subunit_game_id


def unit_setup(gamebattle):
    """read unit from unit_pos(source) file and create object with addunit function"""
    main_dir = gamebattle.main_dir
    # defaultunit = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
    # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])

    team_colour = gamebattle.team_colour
    team_army = (gamebattle.team0_unit, gamebattle.team1_unit, gamebattle.team2_unit)

    with open(os.path.join(main_dir, "data", "ruleset", gamebattle.ruleset_folder, "map",
                           gamebattle.mapselected, gamebattle.source, gamebattle.genre, "unit_pos.csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        subunit_game_id = 1
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]

            control = False
            if gamebattle.playerteam == row[16] or gamebattle.enactment:  # player can control only his team or both in enactment mode
                control = True

            colour = team_colour[row[16]]
            which_army = team_army[row[16]]

            command = False  # Not commander unit by default
            if len(which_army) == 0:  # First unit is commander
                command = True
            coa = pygame.transform.scale(gamebattle.coa_list[row[12]], (60, 60))  # get coa_list image and scale smaller to fit ui
            subunit_game_id = generate_unit(gamebattle, which_army, row, control, command, colour, coa, subunit_game_id)
            # ^ End subunit setup

    unitfile.close()
