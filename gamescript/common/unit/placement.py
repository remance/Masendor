import math

import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy


def placement(self, mouse_pos, mouse_right, mouse_right_down, double_mouse_right):
    if double_mouse_right:  # move unit to new pos
        self.base_pos = mouse_pos

    elif mouse_right or mouse_right_down:  # rotate unit
        self.angle = self.set_rotate(mouse_pos)
        self.new_angle = self.angle
        self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
        if self.angle < 0:  # negative angle (rotate to left side)
            self.radians_angle = math.radians(-self.angle)

    front_pos = (self.base_pos[0], (self.base_pos[1] - self.unit_box_height))  # find front position of unit
    self.front_pos = rotation_xy(self.base_pos, front_pos, self.radians_angle)
    number_pos = (self.base_pos[0] - self.unit_box_width,
                  (self.base_pos[1] + self.unit_box_height))  # find position for number text
    self.base_number_pos = rotation_xy(self.base_pos, number_pos, self.radians_angle)
    self.change_pos_scale()

    self.base_target = self.base_pos
    self.command_target = self.base_target  # reset command base_target
    unit_topleft = pygame.Vector2(self.base_pos[0] - self.unit_box_width,
                                  # get the top left corner of sprite to generate subunit position
                                  self.base_pos[1] - self.unit_box_height)

    for subunit in self.subunit_list:  # generate position of each subunit
        new_target = unit_topleft + subunit.pos_in_unit
        subunit.base_pos = pygame.Vector2(
            rotation_xy(self.base_pos, new_target,
                        self.radians_angle))  # rotate according to sprite current rotation
        subunit.hitbox_rect.center = self.base_pos
        subunit.zoom_scale()
        subunit.angle = self.angle
        subunit.rotate()

    self.issue_order(self.base_pos, double_mouse_right, self.revert, self.base_target, 1)
