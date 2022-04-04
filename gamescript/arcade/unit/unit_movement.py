import math
import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy

rotation_list = (-90, -120, -45, 0, 90, 45, 120, 180)


def rotate_logic(self, *args):
    if self.angle != self.new_angle and self.charging is False and self.state != 10 and self.stamina > 0 and self.collide is False:
        self.new_angle = min(rotation_list,
                             key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation

        self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, subunit can rotate at once
        # ^^ End rotate tiny
        self.set_subunit_target()  # generate new pos related to side


def revert_move(self):
    """Only subunit will rotate to move, not the entire unit"""
    self.new_angle = self.angle
    self.move_rotate = False  # will not rotate to move
    self.revert = True
    new_angle = self.set_rotate()
    for subunit in self.subunits:
        subunit.new_angle = new_angle


def set_target(self, pos):
    """set new base_target, scale base_target from base_target according to zoom scale"""
    self.base_target = pygame.Vector2(pos)  # Set new base base_target
    self.set_subunit_target(self.base_target)


def set_subunit_target(self, target="rotate", reset_path=False):
    """
    generate all four side, hitbox and subunit positions
    :param self: unit object
    :param target: "rotate" for simply rotate whole unit but not move or tuple/vector2 pos for target position to move
    :param reset_path: True will reset subunit command queue
    """
    if target == "rotate":  # rotate unit before moving
        unit_topleft = pygame.Vector2(self.base_pos[0] - self.base_width_box,  # get the top left corner of sprite to generate subunit position
                                      self.base_pos[1] - self.base_height_box)
        for subunit in self.subunits:  # generate position of each subunit
            if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                new_target = unit_topleft + subunit.unit_position
                if reset_path:
                    subunit.command_target.append(pygame.Vector2(
                        rotation_xy(self.base_pos, new_target, self.radians_angle)))
                else:
                    subunit.command_target = pygame.Vector2(
                        rotation_xy(self.base_pos, new_target, self.radians_angle))  # rotate according to sprite current rotation
                    subunit.new_angle = self.new_angle

    else:  # moving unit to specific target position
        unit_target = pygame.Vector2(target[0] - (self.base_width_box - self.leader_subunit.unit_position[0]),
                                     target[1] - (self.base_height_box - self.leader_subunit.unit_position[1]))
        unit_topleft = pygame.Vector2(unit_target[0] - self.base_width_box,
                                      unit_target[1])  # get the top left corner of sprite to generate subunit position

        for subunit in self.subunits:  # generate position of each subunit
            if subunit.unit_leader is False and (subunit.state != 99 or (subunit.state == 99 and self.retreat_start)):
                subunit.new_angle = self.new_angle
                new_target = unit_topleft + subunit.unit_position
                if reset_path:
                    subunit.command_target.append(pygame.Vector2(
                        rotation_xy(unit_target, new_target, self.radians_angle)))
                else:
                    subunit.command_target = pygame.Vector2(
                        rotation_xy(unit_target, new_target, self.radians_angle))  # rotate according to sprite current rotation
            elif subunit.unit_leader:
                subunit.new_angle = self.new_angle
                subunit.command_target = target