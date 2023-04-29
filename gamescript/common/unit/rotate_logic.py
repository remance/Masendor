from math import radians

from gamescript import unit
from gamescript.common import utility

rotation_xy = utility.rotation_xy

rotation_list = unit.rotation_list
rotation_dict = unit.rotation_dict


def rotate_logic(self, *args):
    self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, unit can rotate at once
    self.radians_angle = radians(360 - self.angle)
    if self.new_angle >= 0:
        sprite_angle = 90
    else:
        sprite_angle = -90
    # sprite_angle = min(rotation_list, key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation
    if self.sprite_direction != rotation_dict[sprite_angle]:
        self.sprite_direction = rotation_dict[sprite_angle]  # find closest in list of rotation for sprite direction
        self.current_animation_direction = self.current_animation[self.sprite_direction]
        self.image = self.current_animation_direction[self.show_frame]["sprite"]
    self.make_front_pos()
