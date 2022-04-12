import math
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


def set_subunit_target(self, target="rotate", *args):
    """
    generate all four side, hitbox and subunit positions
    :param self: unit object
    :param target: "rotate" for simply rotate whole unit but not move or tuple/vector2 pos for target position to move
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
                                self.leader_subunit.unit_position[1] - self.base_height_box)
        # get the top left corner of sprite to generate subunit position, use only width since target is for front
        unit_topleft = pygame.Vector2(unit_target[0] - self.base_width_box,
                                      unit_target[1])

    for subunit in self.subunits:  # generate position of each subunit
        if subunit.unit_leader is False:
            subunit.angle = self.angle
            new_target = unit_topleft + subunit.unit_position
            subunit.command_target = pygame.Vector2(
                rotation_xy(unit_target, new_target, self.radians_angle))  # rotate according to sprite current rotation