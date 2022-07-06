import numpy as np
import pygame

from gamescript import battleui
from gamescript.common import utility

rotation_xy = utility.rotation_xy


def split_unit(self, how):
    """
    Split unit either by row or column into two seperate unit
    :param self: Unit object
    :param self: 
    :param how: 
    :return: 
    """  # TODO check split when moving
    from gamescript import unit, leader
    from gamescript.tactical.unit import transfer_leader

    move_leader_subunit = transfer_leader.transfer_leader

    if how == 0:  # split by row
        new_army_subunit = np.array_split(self.subunit_id_array, 2)[1]
        self.subunit_id_array = np.array_split(self.subunit_id_array, 2)[0]
        new_pos = pygame.Vector2(self.base_pos[0], self.base_pos[1] + (self.base_height_box / 2))
        new_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)  # new unit pos (back)
        base_pos = pygame.Vector2(self.base_pos[0], self.base_pos[1] - (self.base_height_box / 2))
        self.base_pos = rotation_xy(self.base_pos, base_pos, self.radians_angle)  # new position for original unit (front)
        self.base_height_box /= 2

    else:  # split by column
        new_army_subunit = np.array_split(self.subunit_id_array, 2, axis=1)[1]
        self.subunit_id_array = np.array_split(self.subunit_id_array, 2, axis=1)[0]
        new_pos = pygame.Vector2(self.base_pos[0] + (self.base_width_box / 3.3), self.base_pos[1])  # 3.3 because 2 make new unit position overlap
        new_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)  # new unit pos (right)
        base_pos = pygame.Vector2(self.base_pos[0] - (self.base_width_box / 2), self.base_pos[1])
        self.base_pos = rotation_xy(self.base_pos, base_pos, self.radians_angle)  # new position for original unit (left)
        self.base_width_box /= 2
        frontpos = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find new front position of unit
        self.front_pos = rotation_xy(self.base_pos, frontpos, self.radians_angle)
        self.set_target(self.front_pos)

    if self.leader[
        1].subunit.game_id not in new_army_subunit.flat:  # move the left sub-general leader subunit if it not in new one
        self.subunit_id_array, new_army_subunit, new_position = move_leader_subunit(self.leader[1], self.subunit_id_array, new_army_subunit)
        self.leader[1].subunit_pos = new_position[0] * new_position[1]
    self.leader[1].subunit.unit_leader = True  # make the sub-unit of this leader a start_set leader sub-unit

    already_pick = []
    for this_leader in (self.leader[0], self.leader[2], self.leader[3]):  # move other leader subunit to original one if they are in new one
        if this_leader.subunit.game_id not in self.subunit_id_array:
            new_army_subunit, self.subunit_id_array, new_position = move_leader_subunit(this_leader, new_army_subunit,
                                                                                        self.subunit_id_array, already_pick)
            this_leader.subunit_pos = new_position[0] * new_position[1]
            already_pick.append(new_position)

    new_leader = [self.leader[1], leader.Leader(1, 0, 1, self, self.battle.leader_data), leader.Leader(1, 0, 2, self, self.battle.leader_data),
                  leader.Leader(1, 0, 3, self, self.battle.leader_data)]  # create new leader list for new unit

    self.subunit_position_list = []

    self.setup_subunit_position_list()

    # v Sort so the new leader subunit position match what set before
    subunit_sprite = [this_subunit for this_subunit in self.subunit_list if
                      this_subunit.game_id in new_army_subunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for this_id in new_army_subunit.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                new_subunit_sprite.append(this_subunit)

    subunit_sprite = [this_subunit for this_subunit in self.subunit_list if
                      this_subunit.game_id in self.subunit_id_array.flat]
    self.subunit_list = []
    for this_id in self.subunit_id_array.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                self.subunit_list.append(this_subunit)
    # ^ End sort

    # v Reset position of subunit in inspect_ui for both old and new unit
    for sprite in (self.subunit_list, new_subunit_sprite):
        width, height = 0, 0
        subunit_number = 0
        for this_subunit in sprite:
            width += self.battle.icon_sprite_width

            if subunit_number >= len(self.subunit_id_array[0]):
                width = 0
                width += self.battle.icon_sprite_width
                height += self.battle.icon_sprite_height
                subunit_number = 0

            this_subunit.inspect_pos = (width + self.battle.inspect_ui_pos[0], height + self.battle.inspect_ui_pos[1])
            this_subunit.rect = this_subunit.image.get_rect(topleft=this_subunit.inspect_pos)
            this_subunit.pos = pygame.Vector2(this_subunit.rect.centerx, this_subunit.rect.centery)
            subunit_number += 1
    # ^ End reset position

    # v Change the original unit stat and sprite
    original_leader = [self.leader[0], self.leader[2], self.leader[3], leader.Leader(1, 0, 3, self, self.battle.leader_data)]
    for index, this_leader in enumerate(original_leader):  # Also change army position of all leader in that unit
        this_leader.role = index  # Change army position to new one
        this_leader.image_position = this_leader.base_image_position[this_leader.role]
        this_leader.rect = this_leader.image.get_rect(center=this_leader.image_position)
    team_commander = self.team_commander
    self.team_commander = team_commander
    self.leader = original_leader

    add_new_unit(self, add_unit_list=False)

    # Make new unit
    new_game_id = self.battle.all_team_unit["alive"][-1].game_id + 1

    new_unit = unit.Unit(start_pos=new_pos, gameid=new_game_id, squadlist=new_army_subunit, colour=self.colour,
                         player_control=self.player_control, coa=self.coa_list, commander=False, startangle=self.angle, team=self.team)

    self.battle.all_team_unit[self.team].add(new_unit)
    new_unit.team_commander = team_commander
    new_unit.leader = new_leader
    new_unit.subunit_list = new_subunit_sprite

    for this_subunit in new_unit.subunit_list:
        this_subunit.unit = new_unit

    for index, this_leader in enumerate(new_unit.leader):  # Change army position of all leader in new unit
        this_leader.unit = new_unit  # Set leader unit to new one
        this_leader.role = index  # Change army position to new one
        this_leader.image_position = this_leader.base_image_position[this_leader.role]  # Change image pos
        this_leader.rect = this_leader.image.get_rect(center=this_leader.image_position)
        this_leader.leader_role_change(this_leader)  # Change stat based on new army position

    add_new_unit(new_unit)


def add_new_unit(self, add_unit_list=True):
    """
    Split the unit into two units
    :param add_unit_list: unit list to add a new unit into
    :return:
    """
    # generate subunit sprite array for inspect ui
    self.subunit_object_array = np.full(self.unit_size, None)  # array of subunit object(not index)
    found_count = 0  # for subunit_sprite index
    for row in range(0, len(self.subunit_id_array)):
        for column in range(0, len(self.subunit_id_array[0])):
            if self.subunit_id_array[row][column] != 0:
                self.subunit_object_array[row][column] = self.subunit_list[found_count]
                self.subunit_list[found_count].unit_position = (self.subunit_position_list[row][column][0] / 10,
                                                                self.subunit_position_list[row][column][1] / 10)  # position in unit sprite
                found_count += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(self.subunit_list):  # reset leader subunit_pos
        if this_subunit.leader is not None:
            this_subunit.leader.subunit_pos = index

    self.zoom = 11 - self.battle.camera_zoom
    self.new_angle = self.angle

    self.start_set(self.battle.subunit_updater)
    self.set_target(self.front_pos)

    number_pos = (self.base_pos[0] - self.base_width_box,
                  (self.base_pos[1] + self.base_height_box))
    self.number_pos = self.rotation_xy(self.base_pos, number_pos, self.radians_angle)
    self.change_pos_scale()  # find new position for troop number text

    for this_subunit in self.subunit_list:
        this_subunit.start_set(this_subunit.zoom, self.battle.subunit_animation_pool)

    if add_unit_list:
        self.battle.all_team_unit["alive"].append(self)

    number_spite = battleui.TroopNumber(self.battle.screen_scale, self)
    self.battle.troop_number_sprite.add(number_spite)

