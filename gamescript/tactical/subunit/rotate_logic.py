import math

from gamescript import subunit
from gamescript.common import utility

rotation_xy = utility.rotation_xy

rotation_list = subunit.rotation_list
rotation_name = subunit.rotation_name
rotation_dict = subunit.rotation_dict


def rotate_logic(self, dt):
    rotate_cal = abs(self.new_angle - self.angle)  # amount of angle left to rotate
    rotate_check = 360 - rotate_cal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
    self.radians_angle = math.radians(360 - self.angle)  # for all side rotate
    if self.angle < 0:  # negative angle (rotate to left side)
        self.radians_angle = math.radians(-self.angle)

    rotate_tiny = self.rotate_speed * dt  # rotate little by little according to time
    if self.new_angle > self.angle:  # rotate to angle more than the current one
        if rotate_cal > 180:  # rotate with the smallest angle direction
            self.angle -= rotate_tiny
            rotate_check -= rotate_tiny
            if rotate_check <= 0:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        else:
            self.angle += rotate_tiny
            if self.angle > self.new_angle:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
    elif self.new_angle < self.angle:  # rotate to angle less than the current one
        if rotate_cal > 180:  # rotate with the smallest angle direction
            self.angle += rotate_tiny
            rotate_check -= rotate_tiny
            if rotate_check <= 0:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        else:
            self.angle -= rotate_tiny
            if self.angle < self.new_angle:
                self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle

    if self.camera_zoom != self.max_camera_zoom:
        self.rotate()  # rotate sprite to new angle
    self.sprite_direction = rotation_dict[min(rotation_list,
                                              key=lambda x: abs(
                                                  x - self.angle))]  # find closest in list of rotation for sprite direction
    self.front_pos = self.make_front_pos()  # generate new pos related to side
    self.front_height = self.height_map.get_height(self.front_pos)
