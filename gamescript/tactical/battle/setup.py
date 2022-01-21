import csv
import os
import numpy as np
import pygame

letter_board = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


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

    from gamescript import unit
    team_colour = unit.team_colour

    main_dir = gamebattle.main_dir
    # defaultunit = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
    # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])

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


def add_new_unit(gamebattle, who, addunitlist=True):
    from gamescript import unit
    # generate subunit sprite array for inspect ui
    who.subunit_sprite_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
    foundcount = 0  # for subunit_sprite index
    foundcount2 = 0  # for positioning
    for row in range(0, len(who.subunit_list)):
        for column in range(0, len(who.subunit_list[0])):
            if who.subunit_list[row][column] != 0:
                who.subunit_sprite_array[row][column] = who.subunit_sprite[foundcount]
                who.subunit_sprite[foundcount].unit_position = (who.subunit_position_list[foundcount2][0] / 10,
                                                                who.subunit_position_list[foundcount2][1] / 10)  # position in unit sprite
                foundcount += 1
            else:
                who.subunit_sprite_array[row][column] = None
            foundcount2 += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(who.subunit_sprite):  # reset leader subunit_pos
        if this_subunit.leader is not None:
            this_subunit.leader.subunit_pos = index

    who.zoom = 11 - gamebattle.camera_scale
    who.new_angle = who.angle

    who.start_set(gamebattle.subunit)
    who.set_target(who.front_pos)

    numberpos = (who.base_pos[0] - who.base_width_box,
                 (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotation_xy(who.base_pos, numberpos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunit_sprite:
        this_subunit.gamestart(this_subunit.zoom)

    if addunitlist:
        gamebattle.all_unit_list.append(who)
        gamebattle.all_unit_index.append(who.game_id)

    numberspite = unit.TroopNumber(gamebattle.screen_scale, who)
    gamebattle.troop_number_sprite.add(numberspite)
