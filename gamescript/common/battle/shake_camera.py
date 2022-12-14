import random


def shake_camera(self):
    self.shown_camera_pos = (self.shown_camera_pos[0] + random.uniform(-1, 1) * self.screen_shake_value,
                             self.shown_camera_pos[1] + random.uniform(-1, 1) * self.screen_shake_value)
