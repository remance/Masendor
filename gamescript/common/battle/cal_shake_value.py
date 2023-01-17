def cal_shake_value(self, start_pos, shake_value):
    distance = start_pos.distance_to(self.true_camera_pos)
    if distance < 1:
        distance = 1

    self.screen_shake_value += shake_value / distance * (self.camera_zoom / self.max_camera_zoom)
