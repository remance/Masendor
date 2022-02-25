import csv
import os

import numpy as np
import pygame

from gamescript import battleui
from gamescript.common import utility

change_group = utility.change_group

letter_board = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def setup_battle_ui(self, change):
    """Change can be either 'add' or 'remove' for adding or removing ui"""
    if change == "add":
        self.unitstat_ui.change_pos((self.screen_rect.width - self.unitstat_ui.image.get_width() / 2,
                                     self.unitstat_ui.image.get_height() / 2))
        self.inspect_button.change_pos((self.unitstat_ui.pos[0] - 206, self.unitstat_ui.pos[1] - 1))

        self.inspect_ui.change_pos((self.screen_rect.width - self.inspect_ui.image.get_width() / 2,
                                    self.unitstat_ui.image.get_height() + (self.inspect_ui.image.get_height() / 2)))

        self.troop_card_ui.change_pos((self.inspect_ui.rect.bottomleft[0] + self.troop_card_ui.image.get_width() / 2,
                                       (self.inspect_ui.rect.bottomleft[1] + self.troop_card_ui.image.get_height() / 2)))

        self.time_ui.change_pos((self.unit_selector.rect.topright), self.time_number)
        self.time_button[0].change_pos((self.time_ui.rect.center[0] - 30, self.time_ui.rect.center[1]))  # time pause button
        self.time_button[1].change_pos((self.time_ui.rect.center[0], self.time_ui.rect.center[1]))  # time decrease button
        self.time_button[2].change_pos((self.time_ui.rect.midright[0] - 60, self.time_ui.rect.center[1]))  # time increase button

        self.scale_ui.change_pos(self.time_ui.rect.bottomleft)
        self.test_button.change_pos((self.scale_ui.rect.bottomleft[0] + (self.test_button.image.get_width() / 2),
                                    self.scale_ui.rect.bottomleft[1] + (self.test_button.image.get_height() / 2)))

        self.speed_number.change_pos(self.time_ui.rect.center)  # self speed number on the time ui

        self.command_ui.change_pos((self.command_ui.image.get_size()[0] / 2,
                                    (self.command_ui.image.get_size()[1] / 2) + self.unit_selector.image.get_height()))
        self.col_split_button.change_pos((self.command_ui.pos[0] - 115, self.command_ui.pos[1] + 26))
        self.row_split_button.change_pos((self.command_ui.pos[0] - 115, self.command_ui.pos[1] + 56))
        self.decimation_button.change_pos((self.command_ui.pos[0] + 100, self.command_ui.pos[1] + 56))

        self.switch_button[0].change_pos((self.command_ui.pos[0] - 40, self.command_ui.pos[1] + 96))  # skill condition button
        self.switch_button[1].change_pos((self.command_ui.pos[0] - 80, self.command_ui.pos[1] + 96))  # fire at will button
        self.switch_button[2].change_pos((self.command_ui.pos[0], self.command_ui.pos[1] + 96))  # behaviour button
        self.switch_button[3].change_pos((self.command_ui.pos[0] + 40, self.command_ui.pos[1] + 96))  # shoot range button
        self.switch_button[4].change_pos((self.command_ui.pos[0] - 125, self.command_ui.pos[1] + 96))  # arc_shot button
        self.switch_button[5].change_pos((self.command_ui.pos[0] + 80, self.command_ui.pos[1] + 96))  # toggle run button
        self.switch_button[6].change_pos((self.command_ui.pos[0] + 120, self.command_ui.pos[1] + 96))  # toggle melee mode

        self.event_log_button[0].change_pos((self.event_log.pos[0] + (self.event_log_button[0].image.get_width() / 2),
                                             self.event_log.pos[1] - self.event_log.image.get_height() - (self.event_log_button[0].image.get_height() / 2)))
        self.event_log_button[1].change_pos((self.event_log_button[0].pos[0] + self.event_log_button[0].image.get_width(),
                                             self.event_log_button[0].pos[1]))  # army tab log button
        self.event_log_button[2].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 2),
                                             self.event_log_button[0].pos[1]))  # leader tab log button
        self.event_log_button[3].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 3),
                                             self.event_log_button[0].pos[1]))  # subunit tab log button
        self.event_log_button[4].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 5),
                                             self.event_log_button[0].pos[1]))  # delete current tab log button
        self.event_log_button[5].change_pos((self.event_log_button[0].pos[0] + (self.event_log_button[0].image.get_width() * 6),
                                             self.event_log_button[0].pos[1]))  # delete all log button

        inspect_ui_pos = [self.unitstat_ui.rect.bottomleft[0] - self.icon_sprite_width / 1.25,
                               self.unitstat_ui.rect.bottomleft[1]]
        width, height = inspect_ui_pos[0], inspect_ui_pos[1]
        sub_unit_number = 0  # Number of subunit based on the position in row and column
        imgsize = (self.icon_sprite_width, self.icon_sprite_height)
        for this_subunit in list(range(0, 64)):
            width += imgsize[0]
            self.inspect_subunit.append(battleui.InspectSubunit((width, height)))
            sub_unit_number += 1
            if sub_unit_number == 8:  # Reach the last subunit in the row, go to the next one
                width = inspect_ui_pos[0]
                height += imgsize[1]
                sub_unit_number = 0

    change_group(self.unit_selector, self.battle_ui, change)
    change_group(self.select_scroll, self.battle_ui, change)

    change_group(self.col_split_button, self.button_ui, change)
    change_group(self.row_split_button, self.button_ui, change)
    change_group(self.time_button, self.battle_ui, change)
    change_group(self.scale_ui, self.battle_ui, change)


def add_unit(game_id, position, subunit_list, colour, leader_list, leader_stat, control, coa, command, start_angle, start_hp, start_stamina,
             team):
    """Create unit object into the battle and leader of the unit"""
    from gamescript import unit, leader
    old_subunit_list = subunit_list[~np.all(subunit_list == 0, axis=1)]  # remove whole empty column in subunit list
    subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(game_id, position, subunit_list, colour, control, coa, command, abs(360 - start_angle), start_hp, start_stamina, team)

    # add leader
    unit.leader = [leader.Leader(leader_list[0], leader_list[4], 0, unit, leader_stat),
                   leader.Leader(leader_list[1], leader_list[5], 1, unit, leader_stat),
                   leader.Leader(leader_list[2], leader_list[6], 2, unit, leader_stat),
                   leader.Leader(leader_list[3], leader_list[7], 3, unit, leader_stat)]
    return unit


def generate_unit(battle, which_army, setup_data, control, command, colour, coa, subunit_game_id):
    """generate unit data into self object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript import battleui, subunit
    this_unit = add_unit(setup_data[0], (setup_data[9][0], setup_data[9][1]),
                         np.array([setup_data[1], setup_data[2], setup_data[3], setup_data[4], setup_data[5],
                                   setup_data[6], setup_data[7], setup_data[8]]),
                         colour, setup_data[10] + setup_data[11], battle.leader_data, control,
                         coa, command, setup_data[13], setup_data[14], setup_data[15], setup_data[16])
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
    battle.troop_number_sprite.add(battleui.TroopNumber(battle.screen_scale, this_unit))  # create troop number text sprite

    return subunit_game_id


def unit_setup(battle):
    """read unit from unit_pos(source) file and create object with addunit function"""

    from gamescript import unit
    team_colour = unit.team_colour

    main_dir = battle.main_dir
    # default_unit = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
    # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])

    team_army = (battle.team0_unit, battle.team1_unit, battle.team2_unit)

    with open(os.path.join(main_dir, "data", "ruleset", battle.ruleset_folder, "map",
                           battle.mapselected, battle.source, battle.genre, "unit_pos.csv"), encoding="utf-8", mode="r") as unit_file:
        rd = csv.reader(unit_file, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        subunit_game_id = 1
        for row in rd[1:]:  # skip header
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]

            control = False
            if battle.playerteam == row[16] or battle.enactment:  # player can control only his team or both in enactment mode
                control = True

            colour = team_colour[row[16]]
            which_army = team_army[row[16]]

            command = False  # Not commander unit by default
            if len(which_army) == 0:  # First unit is commander
                command = True
            coa = pygame.transform.scale(battle.coa_list[row[12]], (60, 60))  # get coa_list image and scale smaller to fit ui
            subunit_game_id = generate_unit(battle, which_army, row, control, command, colour, coa, subunit_game_id)
            # ^ End subunit setup

    unit_file.close()


def add_new_unit(battle, who, add_unit_list=True):
    from gamescript import battleui
    # generate subunit sprite array for inspect ui
    who.subunit_sprite_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
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
