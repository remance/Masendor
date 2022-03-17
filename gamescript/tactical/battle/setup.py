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
        self.inspect_button.change_pos((self.unitstat_ui.rect.topleft[0] - (self.inspect_button.image.get_width() / 2), self.unitstat_ui.pos[1]))

        self.inspect_ui.change_pos((self.screen_rect.width - self.inspect_ui.image.get_width() / 2,
                                    self.unitstat_ui.image.get_height() + (self.inspect_ui.image.get_height() / 2)))

        self.troop_card_ui.change_pos((self.inspect_ui.rect.bottomleft[0] + self.troop_card_ui.image.get_width() / 2,
                                       (self.inspect_ui.rect.bottomleft[1] + self.troop_card_ui.image.get_height() / 2)))

        self.time_ui.change_pos((self.unit_selector.rect.topright), self.time_number)
        self.time_button[0].change_pos((self.time_ui.rect.center[0] - self.time_button[0].image.get_width(),
                                        self.time_ui.rect.center[1]))  # time pause button
        self.time_button[1].change_pos((self.time_ui.rect.center[0], self.time_ui.rect.center[1]))  # time decrease button
        self.time_button[2].change_pos((self.time_ui.rect.midright[0] - self.time_button[2].image.get_width() * 2,
                                        self.time_ui.rect.center[1]))  # time increase button

        self.scale_ui.change_pos(self.time_ui.rect.bottomleft)
        self.test_button.change_pos((self.scale_ui.rect.bottomleft[0] + (self.test_button.image.get_width() / 2),
                                    self.scale_ui.rect.bottomleft[1] + (self.test_button.image.get_height() / 2)))
        self.warning_msg.change_pos(self.test_button.rect.bottomleft)

        self.speed_number.change_pos(self.time_ui.rect.center)  # self speed number on the time ui

        self.command_ui.change_pos((self.command_ui.image.get_size()[0] / 2,
                                    (self.command_ui.image.get_size()[1] / 2) + self.unit_selector.image.get_height()))

        self.col_split_button.change_pos((self.command_ui.rect.midleft[0] + (self.col_split_button.image.get_width() / 2),
                                          self.command_ui.rect.midleft[1]))
        self.row_split_button.change_pos((self.command_ui.rect.midleft[0] + (self.row_split_button.image.get_width() / 2),
                                          self.command_ui.rect.midleft[1] + (self.col_split_button.image.get_height() * 3)))
        self.decimation_button.change_pos((self.command_ui.rect.midleft[0] + (self.decimation_button.image.get_width() / 2),
                                           self.command_ui.rect.midleft[1] + (self.decimation_button.image.get_height() * 2)))

        self.switch_button[0].change_pos((self.command_ui.rect.bottomleft[0] + (self.switch_button[0].image.get_width()),
                                          self.command_ui.rect.bottomleft[1] - (self.switch_button[0].image.get_height() / 2)))  # skill condition button
        self.switch_button[1].change_pos((self.command_ui.rect.bottomleft[0] + (self.switch_button[1].image.get_width() * 2),
                                          self.command_ui.rect.bottomleft[1] - (self.switch_button[1].image.get_height() / 2)))  # fire at will button
        self.switch_button[2].change_pos((self.command_ui.rect.bottomleft[0] + (self.switch_button[2].image.get_width() * 3),
                                          self.command_ui.rect.bottomleft[1] - (self.switch_button[2].image.get_height() / 2)))  # behaviour button
        self.switch_button[3].change_pos((self.command_ui.rect.bottomleft[0] + (self.switch_button[3].image.get_width() * 4),
                                          self.command_ui.rect.bottomleft[1] - (self.switch_button[3].image.get_height() / 2)))  # shoot range button
        self.switch_button[4].change_pos((self.command_ui.rect.bottomleft[0] + (self.switch_button[4].image.get_width() * 5),
                                          self.command_ui.rect.bottomleft[1] - (self.switch_button[4].image.get_height() / 2)))  # arc_shot button
        self.switch_button[5].change_pos((self.command_ui.rect.bottomleft[0] + (self.switch_button[5].image.get_width() * 6),
                                          self.command_ui.rect.bottomleft[1] - (self.switch_button[5].image.get_height() / 2)))  # toggle run button
        self.switch_button[6].change_pos((self.command_ui.rect.bottomleft[0] + (self.switch_button[6].image.get_width() * 7),
                                          self.command_ui.rect.bottomleft[1] - (self.switch_button[6].image.get_height() / 2)))  # toggle melee mode

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

    change_group(self.unit_selector, self.battle_ui_updater, change)
    change_group(self.unit_selector_scroll, self.battle_ui_updater, change)

    change_group(self.col_split_button, self.button_ui, change)
    change_group(self.row_split_button, self.button_ui, change)
    change_group(self.time_button, self.battle_ui_updater, change)
    change_group(self.scale_ui, self.battle_ui_updater, change)


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


def generate_unit(self, which_army, setup_data, control, command, colour, coa, subunit_game_id):
    """generate unit data into self object"""
    from gamescript import battleui, subunit
    print(setup_data)
    this_unit = add_unit(setup_data["ID"], (setup_data["POS"][0], setup_data["POS"][1]),
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
                                          this_unit.start_hp, this_unit.start_stamina, self.unit_scale, self.genre)
            self.subunit.add(add_subunit)
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
    self.troop_number_sprite.add(battleui.TroopNumber(self.screen_scale, this_unit))  # create troop number text sprite


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
