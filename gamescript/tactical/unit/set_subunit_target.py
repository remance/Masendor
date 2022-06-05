import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy


def set_subunit_target(self, target="rotate", reset_path=False, *args):
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
