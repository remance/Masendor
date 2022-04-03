import math
import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy


def rotate_logic(self, dt):
    if self.angle != self.new_angle and self.charging is False and self.state != 10 and self.stamina > 0 and self.collide is False:
        self.rotate_cal = abs(self.new_angle - self.angle)  # amount of angle left to rotate
        self.rotate_check = 360 - self.rotate_cal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
        self.move_rotate = True
        self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
        if self.angle < 0:  # negative angle (rotate to left side)
            self.radians_angle = math.radians(-self.angle)

        # Rotate logic to continuously rotate based on angle and shortest length
        rotate_tiny = self.rotate_speed * dt  # rotate little by little according to time
        if self.new_angle > self.angle:  # rotate to angle more than the current one
            if self.rotate_cal > 180:  # rotate with the smallest angle direction
                self.angle -= rotate_tiny
                self.rotate_check -= rotate_tiny
                if self.rotate_check <= 0:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
            else:
                self.angle += rotate_tiny
                if self.angle > self.new_angle:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        elif self.new_angle < self.angle:  # rotate to angle less than the current one
            if self.rotate_cal > 180:  # rotate with the smallest angle direction
                self.angle += rotate_tiny
                self.rotate_check -= rotate_tiny
                if self.rotate_check <= 0:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
            else:
                self.angle -= rotate_tiny
                if self.angle < self.new_angle:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        # ^^ End rotate tiny
        self.set_subunit_target()  # generate new pos related to side

    elif self.move_rotate and abs(self.angle - self.new_angle) < 1:  # Finish
        self.move_rotate = False
        if self.rotate_only is False:  # continue moving to base_target after finish rotate
            self.set_subunit_target(self.base_target)
        else:
            self.state = 0  # idle state
            self.process_command(self.base_target, other_command=1)
            self.rotate_only = False  # reset rotate only condition


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
        unit_topleft = pygame.Vector2(target[0] - self.base_width_box,
                                      target[1])  # get the top left corner of sprite to generate subunit position

        for subunit in self.subunits:  # generate position of each subunit
            if subunit.state != 99 or (subunit.state == 99 and self.retreat_start):
                subunit.new_angle = self.new_angle
                new_target = unit_topleft + subunit.unit_position
                if reset_path:
                    subunit.command_target.append(pygame.Vector2(
                        rotation_xy(target, new_target, self.radians_angle)))
                else:
                    subunit.command_target = pygame.Vector2(
                        rotation_xy(target, new_target, self.radians_angle))  # rotate according to sprite current rotation
