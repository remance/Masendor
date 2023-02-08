import math

from gamescript import subunit
from gamescript.common import utility

rotation_xy = utility.rotation_xy

rotation_list = subunit.rotation_list
rotation_dict = subunit.rotation_dict


def rotate_logic(self, *args):
    self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, subunit can rotate at once
    self.radians_angle = math.radians(360 - self.angle)
    sprite_angle = min(rotation_list, key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation
    self.sprite_direction = rotation_dict[sprite_angle]  # find closest in list of rotation for sprite direction
    self.make_front_pos()
