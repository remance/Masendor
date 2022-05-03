import math
import numpy as np
import pygame

from gamescript.common import utility

rotation_xy = utility.rotation_xy

rotation_list = (-90, -120, -45, 0, 90, 45, 120, 180)


def rotate_logic(self, *args):
    if self.angle != self.new_angle and self.charging is False:
        self.new_angle = min(rotation_list,
                             key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation

        self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, subunit can rotate at once
        self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
        self.set_subunit_target()  # generate new pos related to side


def revert_move(self):
    """Not use in arcade mode"""
    pass


def set_target(self, pos):
    """set new base_target, scale base_target from base_target according to zoom scale"""
    self.base_target = pygame.Vector2(pos)  # Set new base base_target
    self.set_subunit_target(target=self.base_target)


def movement_logic(self):
    pass


def set_subunit_target(self, target="rotate", leader_move=False, *args):
    """
    generate all four side, hitbox and subunit positions
    :param self: unit object
    :param target: "rotate" for simply rotate whole unit but not move or tuple/vector2 pos for target position to move
    :param leader_move: set for leader subunit as well or not
    :param reset_path: True will reset subunit command queue
    """
    if target == "rotate":  # rotate unit before
        # calculate new target from leader position
        unit_target = self.leader_subunit.base_pos - (self.leader_subunit.unit_position[0] - self.base_width_box,
                                                      self.leader_subunit.unit_position[1] - self.base_height_box)
        unit_target = pygame.Vector2(
                    rotation_xy(self.leader_subunit.base_pos, unit_target, self.radians_angle))
        # get the top left corner of sprite to generate subunit position
        unit_topleft = pygame.Vector2(unit_target[0] - self.base_width_box,
                                      unit_target[1] - self.base_height_box)
    else:  # moving unit to specific target position
        # calculate new target from leader target and position in unit
        unit_target = target - (self.leader_subunit.unit_position[0] - self.base_width_box,
                                self.leader_subunit.unit_position[1])
        unit_target = pygame.Vector2(
                    rotation_xy(self.leader_subunit.base_pos, unit_target, self.radians_angle))
        # get the top left corner of sprite to generate subunit position, use only width since target is for front
        unit_topleft = pygame.Vector2(unit_target[0] - self.base_width_box,
                                      unit_target[1])

    for subunit in self.subunits:  # generate position of each subunit
        if subunit.unit_leader is False or leader_move:
            new_target = unit_topleft + subunit.unit_position
            subunit.command_target = pygame.Vector2(
                rotation_xy(unit_target, new_target, self.radians_angle))  # rotate according to sprite current rotation


def move_leader(self, how):
    """Use static number for maximum array size here, arcade mode accept only 5x5 unit so maximum at 4"""
    leader_position = np.where(np.asarray(self.subunit_list) == str(self.leader_subunit.game_id))  # position of leader
    old_leader_position = ([leader_position[0][0]], [leader_position[1][0]])
    old_unit_position = (leader_position[0][0] * 5) + leader_position[1][0]

    if how == "up" and leader_position[0][0] != 0:  # move up and not already at top row
        leader_position[0][0] -= 1
    elif how == "down" and leader_position[0][0] != 4:  # move down and not already at bottom row
        leader_position[0][0] += 1
        if len(self.subunit_list) < leader_position[0][0] + 1:  # add new row
            self.subunit_list = np.vstack((self.subunit_list, np.array([0, 0, 0, 0, 0])))
    elif how == "left" and leader_position[1][0] != 0:  # move left and not already at max left column
        leader_position[1][0] -= 1
    elif how == "right" and leader_position[1][0] != 4:  # move right and not already at max right column
        leader_position[1][0] += 1
        if len(self.subunit_list[0]) < leader_position[1][0] + 1:  # add new column
            self.subunit_list = np.column_stack((self.subunit_list, np.array([0, 0, 0, 0, 0])))
    new_unit_position = (leader_position[0][0] * 5) + leader_position[1][0]

    if leader_position != old_leader_position:
        old_subunit = self.subunits_array[leader_position[0][0]][leader_position[1][0]]
        self.subunits_array[leader_position[0][0]][leader_position[1][0]] = self.leader_subunit
        self.subunits_array[old_leader_position[0][0]][old_leader_position[1][0]] = old_subunit
        self.subunit_list[leader_position[0][0]][leader_position[1][0]] = str(self.leader_subunit.game_id)

        self.leader_subunit.unit_position = (self.subunit_position_list[new_unit_position][0] / 10,
                                             self.subunit_position_list[new_unit_position][1] / 10)
        if old_subunit is not None:
            self.subunit_list[old_leader_position[0][0]][old_leader_position[1][0]] = str(old_subunit.game_id)
            old_subunit.unit_position = (self.subunit_position_list[old_unit_position][0] / 10,
                                         self.subunit_position_list[old_unit_position][1] / 10)
        else:
            self.subunit_list[old_leader_position[0][0]][old_leader_position[1][0]] = 0

        # old_subunit_list = self.subunit_list[~np.all(self.subunit_list == 0, axis=1)]  # remove whole empty column in subunit list
        # self.subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == 0, axis=0)]  # remove whole empty row in subunit list

        self.base_width_box, self.base_height_box = len(self.subunit_list[0]) * (self.image_size[0] + 10) / 20, \
                                                    len(self.subunit_list) * (self.image_size[1] + 2) / 20
        self.set_subunit_target()
        self.setup_frontline()
        if self.control:
            self.battle.change_inspect_subunit()
        self.input_delay = 0.5
