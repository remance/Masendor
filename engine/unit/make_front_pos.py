from math import cos, sin

from pygame import Vector2

from engine import utility

rotation_xy = utility.rotation_xy


def make_front_pos(self):
    """create new pos for front side of sprite"""
    self.front_pos = Vector2(self.base_pos[0] + (self.hitbox_front_distance * sin(self.radians_angle)),
                             self.base_pos[1] - (self.hitbox_front_distance * cos(self.radians_angle)))
    self.front_height = self.get_height(self.front_pos)
