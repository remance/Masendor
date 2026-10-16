from pygame import Vector2


def fix_camera(self):
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

    self.camera_topleft_corner = (self.camera_pos[0] - self.battle_camera_center[0],
                                  self.camera_pos[1] - self.battle_camera_center[
                                      1])  # calculate top left corner of camera position

    # self.camera.camera_top_bound = self.shown_camera_center_pos[1] - self.camera_center_y
    # self.camera.camera_right_bound = self.shown_camera_center_pos[0] + self.camera_w_center
    # self.camera.camera_bottom_bound = self.shown_camera_center_pos[0] + self.camera_center_y
    self.camera.rect.topleft = self.camera_topleft_corner
