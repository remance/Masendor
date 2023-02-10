import math
import pygame

from gamescript.common import utility

rotation_xy = utility.rotation_xy


def make_front_pos(self):
    """create new pos for front side of sprite"""
    self.front_pos = pygame.Vector2(self.base_pos[0] - (2 * math.sin(self.radians_angle)),
                                    self.base_pos[1] - (2 * math.cos(self.radians_angle)))
    self.front_height = self.get_height(self.front_pos)
