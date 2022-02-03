import csv
import os

import numpy as np
import pygame

letter_board = ("a", "b", "c", "d", "e")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def add_unit(subunit_list, position, game_id, colour, unit_leader, leader_stat, control, coa, command, start_angle, start_hp, start_stamina, team):
    """Create unit object into the battle and leader of the unit"""
    from gamescript import unit, leader
    old_subunit_list = subunit_list[~np.all(subunit_list == 0, axis=1)]  # remove whole empty column in subunit list
    subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(position, game_id, subunit_list, colour, control, coa, command, abs(360 - start_angle), start_hp, start_stamina, team)

    # add leader
    leader_pos = np.where(subunit_list == "h")[0]
    unit.leader = [leader.Leader(unit_leader, leader_pos, 0, unit, leader_stat)]
    return unit


def generate_unit(battle, which_army, row, control, command, colour, coa, subunit_game_id, troop_list):
    """generate unit data into self object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript import battleui, subunit
    this_unit = add_unit(np.array([row[1], row[2], row[3], row[4], row[5]]), (row[6][0], row[6][1]), row[0],
                         colour, row[7], battle.leader_stat, control,
                         coa, command, row[8], row[9], row[10], row[11])
    which_army.add(this_unit)
    army_subunit_index = 0  # army_subunit_index is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    unit_array = np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])  # for unit size overlap check
    max_column = len(this_unit.subunit_list[0])
    for subunit_index, subunit_number in enumerate(np.nditer(this_unit.subunit_list, op_flags=["readwrite"], order="C")):
        now_row = int(subunit_index / 5)
        now_col = subunit_index - (now_row * 5)
        this_unit.subunit_sprite_array[row][column] = None  # replace numpy None with python None
        if subunit_number != 0 and unit_array[now_row][now_col] == 0:  # skip if there is already subunit occupy the slot
            size = troop_list[subunit_number]["Size"]
            if now_row + size <= 5 and now_col + size <= 5:  # skip if subunti exceed unit size array
                for row_number in range(now_row, now_row + size):
                    for col_number in range(now_col, now_col + size):
                        unit_array[row_number][col_number] = subunit_number
                add_subunit = subunit.Subunit(subunit_number, subunit_game_id, this_unit, this_unit.subunit_position_list[army_subunit_index],
                                             this_unit.start_hp, this_unit.start_stamina, battle.unitscale, battle.genre)
                battle.subunit.add(add_subunit)
                subunit_number[...] = subunit_game_id
                this_unit.subunit_sprite_array[row][column] = add_subunit
                this_unit.subunit_sprite.append(add_subunit)
                subunit_game_id += 1

        column += 1
        if column == max_column:
            column = 0
            row += 1
        army_subunit_index += 1

    return subunit_game_id


def unit_setup(battle):
    """read unit from unit_pos(source) file and create object with addunit function"""

    from gamescript import unit
    team_colour = unit.team_colour

    main_dir = battle.main_dir
    # default_unit = np.array([[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0], [0,0,0,0,0]])

    team_army = (battle.team0_unit, battle.team1_unit, battle.team2_unit)

    with open(os.path.join(main_dir, "data", "ruleset", battle.ruleset_folder, "map",
                           battle.mapselected, battle.source, battle.genre, "unit_pos.csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        subunit_game_id = 1
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 6):  # column that need to be in list format
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]

            control = False
            if battle.playerteam == row[11]:  # player can control only his team or both in enactment mode
                control = True

            colour = team_colour[row[11]]
            which_army = team_army[row[11]]

            command = False  # Not commander unit by default
            if len(which_army) == 0:  # First unit is commander
                command = True
            coa = pygame.transform.scale(battle.coa_list[row[12]], (60, 60))  # get coa_list image and scale smaller to fit ui
            subunit_game_id = generate_unit(battle, which_army, row, control, command, colour, coa, subunit_game_id, battle.troop_data.troop_list)
            # ^ End subunit setup

    unitfile.close()


def add_new_unit(battle, who, add_unit_list=True):
    from gamescript import battleui
    # generate subunit sprite array for inspect ui
    who.subunit_sprite_array = np.empty((5, 5), dtype=object)  # array of subunit object(not index)
    found_count = 0  # for subunit_sprite index
    found_count2 = 0  # for positioning
    for row in range(0, len(who.subunit_list)):
        for column in range(0, len(who.subunit_list[0])):
            if who.subunit_list[row][column] != 0:
                who.subunit_sprite_array[row][column] = who.subunit_sprite[found_count]
                who.subunit_sprite[found_count].unit_position = (who.subunit_position_list[found_count2][0] / 10,
                                                                 who.subunit_position_list[found_count2][1] / 10)  # position in unit sprite
                found_count += 1
            else:
                who.subunit_sprite_array[row][column] = None
            found_count2 += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(who.subunit_sprite):  # reset leader subunit_pos
        if this_subunit.leader is not None:
            this_subunit.leader.subunit_pos = index

    who.zoom = 11 - battle.camera_scale
    who.new_angle = who.angle

    who.start_set(battle.subunit)
    who.set_target(who.front_pos)

    number_pos = (who.base_pos[0] - who.base_width_box,
                  (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotation_xy(who.base_pos, number_pos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunit_sprite:
        this_subunit.start_set(this_subunit.zoom)

    if add_unit_list:
        battle.all_unit_list.append(who)
        battle.all_unit_index.append(who.game_id)

    number_spite = battleui.TroopNumber(battle.screen_scale, who)
    battle.troop_number_sprite.add(number_spite)
