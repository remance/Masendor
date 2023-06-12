from pygame import Vector2


def camera_fix(self):
    if self.true_camera_pos[0] > self.max_camera[0]:  # camera cannot go further than max x
        self.true_camera_pos[0] = self.max_camera[0]
    elif self.true_camera_pos[0] < 0:  # camera cannot go less than 0 x
        self.true_camera_pos[0] = 0

    if self.true_camera_pos[1] > self.max_camera[1]:  # same for y
        self.true_camera_pos[1] = self.max_camera[1]
    elif self.true_camera_pos[1] < 0:
        self.true_camera_pos[1] = 0

    self.camera_pos = Vector2(self.true_camera_pos * self.screen_scale[0],
                              self.true_camera_pos * self.screen_scale[1]) * 5

    self.camera_topleft_corner = (self.camera_pos[0] - self.center_screen[0],
                                  self.camera_pos[1] - self.center_screen[
                                      1])  # calculate top left corner of camera position
