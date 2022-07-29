import pygame

from gamescript.common import utility

rotation_xy = utility.rotation_xy


def set_subunit_target(self, target="rotate", leader_move=False, *args):
    """
    generate all four side, hitbox and subunit positions
    :param self: unit object
    :param target: "rotate" for simply rotate whole unit but not move or tuple/vector2 pos for target position to move
    :param leader_move: set for leader subunit as well or not
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

    for subunit in self.alive_subunit_list:  # generate position of each subunit
        if subunit.unit_leader is False or leader_move:
            new_target = unit_topleft + subunit.unit_position
            subunit.command_target = pygame.Vector2(
                rotation_xy(unit_target, new_target, self.radians_angle))  # rotate according to sprite current rotation
