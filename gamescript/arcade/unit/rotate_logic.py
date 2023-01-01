import math

from gamescript.common import utility

rotation_xy = utility.rotation_xy

# "l_side", "l_sidedown", "l_sideup", "front", "r_side", "r_sideup", "r_sidedown", "back", "back"
rotation_list = (-90, -120, -45, 0, 90, 45, 120, 180)


def rotate_logic(self, *args):
    if self.angle != self.new_angle and self.charging is False:
        self.new_angle = min(rotation_list,
                             key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation

        self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, subunit can rotate at once
        self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
        self.set_subunit_target()  # generate new pos related to side
