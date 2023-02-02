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
        unit_topleft = pygame.Vector2(self.base_pos[0] - self.unit_box_width,
                                      # get the top left corner of sprite to generate subunit position
                                      self.base_pos[1] - self.unit_box_height)
        target = self.base_pos

    else:  # moving unit to specific target position
        unit_topleft = pygame.Vector2(target[0] - self.unit_box_width,
                                      target[1])  # get the top left corner of sprite to generate subunit position

    for subunit in self.alive_subunit_list:  # generate position of each subunit
        if subunit.broken is False:
            subunit.new_angle = self.new_angle
            new_target = unit_topleft + subunit.pos_in_unit
            if reset_path:
                subunit.command_target.append(pygame.Vector2(
                    rotation_xy(target, new_target, self.radians_angle)))
            else:
                subunit.command_target = pygame.Vector2(
                    rotation_xy(target, new_target,
                                self.radians_angle))  # rotate according to sprite current rotation
