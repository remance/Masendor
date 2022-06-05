import numpy as np
import pygame

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
    from gamescript.tactical.unit import transfer_leader, add_new_unit

    move_leader_subunit = transfer_leader.transfer_leader
    add_new_unit = add_new_unit.add_new_unit

    if how == 0:  # split by row
        new_army_subunit = np.array_split(self.subunit_list, 2)[1]
        self.subunit_list = np.array_split(self.subunit_list, 2)[0]
        new_pos = pygame.Vector2(self.base_pos[0], self.base_pos[1] + (self.base_height_box / 2))
        new_pos = rotation_xy(self.base_pos, new_pos, self.radians_angle)  # new unit pos (back)
        base_pos = pygame.Vector2(self.base_pos[0], self.base_pos[1] - (self.base_height_box / 2))
        self.base_pos = rotation_xy(self.base_pos, base_pos, self.radians_angle)  # new position for original unit (front)
        self.base_height_box /= 2

    else:  # split by column
        new_army_subunit = np.array_split(self.subunit_list, 2, axis=1)[1]
        self.subunit_list = np.array_split(self.subunit_list, 2, axis=1)[0]
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
        self.subunit_list, new_army_subunit, new_position = move_leader_subunit(self.leader[1], self.subunit_list, new_army_subunit)
        self.leader[1].subunit_pos = new_position[0] * new_position[1]
    self.leader[1].subunit.unit_leader = True  # make the sub-unit of this leader a start_set leader sub-unit

    already_pick = []
    for this_leader in (self.leader[0], self.leader[2], self.leader[3]):  # move other leader subunit to original one if they are in new one
        if this_leader.subunit.game_id not in self.subunit_list:
            new_army_subunit, self.subunit_list, new_position = move_leader_subunit(this_leader, new_army_subunit,
                                                                                self.subunit_list, already_pick)
            this_leader.subunit_pos = new_position[0] * new_position[1]
            already_pick.append(new_position)

    new_leader = [self.leader[1], leader.Leader(1, 0, 1, self, self.battle.leader_data), leader.Leader(1, 0, 2, self, self.battle.leader_data),
                  leader.Leader(1, 0, 3, self, self.battle.leader_data)]  # create new leader list for new unit

    self.subunit_position_list = []

    width, height = 0, 0
    subunit_number = 0  # Number of subunit based on the position in row and column
    for this_subunit in self.subunit_list.flat:
        width += self.image_size[0]
        self.subunit_position_list.append((width, height))
        subunit_number += 1
        if subunit_number >= len(self.subunit_list[0]):  # Reach the last subunit in the row, go to the next one
            width = 0
            height += self.image_size[1]
            subunit_number = 0

    # v Sort so the new leader subunit position match what set before
    subunit_sprite = [this_subunit for this_subunit in self.subunits if
                      this_subunit.game_id in new_army_subunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for this_id in new_army_subunit.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                new_subunit_sprite.append(this_subunit)

    subunit_sprite = [this_subunit for this_subunit in self.subunits if
                      this_subunit.game_id in self.subunit_list.flat]
    self.subunits = []
    for this_id in self.subunit_list.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                self.subunits.append(this_subunit)
    # ^ End sort

    # v Reset position of subunit in inspect_ui for both old and new unit
    for sprite in (self.subunits, new_subunit_sprite):
        width, height = 0, 0
        subunit_number = 0
        for this_subunit in sprite:
            width += self.battle.icon_sprite_width

            if subunit_number >= len(self.subunit_list[0]):
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

    add_new_unit(self, self, False)

    # Make new unit
    new_game_id = self.battle.all_team_unit["alive"][-1].game_id + 1

    new_unit = unit.Unit(start_pos=new_pos, gameid=new_game_id, squadlist=new_army_subunit, colour=self.colour,
                         control=self.control, coa=self.coa_list, commander=False, startangle=self.angle, team=self.team)

    self.battle.all_team_unit[self.team].add(new_unit)
    new_unit.team_commander = team_commander
    new_unit.leader = new_leader
    new_unit.subunits = new_subunit_sprite

    for this_subunit in new_unit.subunits:
        this_subunit.unit = new_unit

    for index, this_leader in enumerate(new_unit.leader):  # Change army position of all leader in new unit
        this_leader.unit = new_unit  # Set leader unit to new one
        this_leader.role = index  # Change army position to new one
        this_leader.image_position = this_leader.base_image_position[this_leader.role]  # Change image pos
        this_leader.rect = this_leader.image.get_rect(center=this_leader.image_position)
        this_leader.leader_role_change(this_leader)  # Change stat based on new army position

    add_new_unit(self, new_unit)
