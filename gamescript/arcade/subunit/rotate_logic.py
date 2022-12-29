from gamescript import subunit
from gamescript.common import utility

rotation_xy = utility.rotation_xy

rotation_list = subunit.rotation_list
rotation_name = subunit.rotation_name
rotation_dict = subunit.rotation_dict


def rotate_logic(self, *args):
    self.new_angle = min(rotation_list, key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation
    self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, subunit can rotate at once
    if self.zoom != 10:
        self.rotate()  # rotate sprite to new angle
    self.sprite_direction = rotation_dict[self.angle]  # find closest in list of rotation for sprite direction
    self.front_pos = self.make_front_pos()  # generate new pos related to side
    self.front_height = self.height_map.get_height(self.front_pos)
