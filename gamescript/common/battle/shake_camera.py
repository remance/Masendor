from random import uniform


def shake_camera(self):
    self.shown_camera_pos = (self.shown_camera_pos[0] + uniform(-1, 1) * self.screen_shake_value,
                             self.shown_camera_pos[1] + uniform(-1, 1) * self.screen_shake_value)
