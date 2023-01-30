from gamescript import subunit
from gamescript.common import utility

rotation_xy = utility.rotation_xy

rotation_list = subunit.rotation_list
rotation_name = subunit.rotation_name
rotation_dict = subunit.rotation_dict


def rotate_logic(self, *args):
    self.new_angle = min(rotation_list, key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation
    self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, subunit can rotate at once
    if self.camera_zoom != self.max_camera_zoom:
        self.rotate()  # rotate sprite to new angle when camera zoom is not at max level since is use troop sprite
    self.sprite_direction = rotation_dict[self.angle]  # find closest in list of rotation for sprite direction
    self.make_front_pos()
