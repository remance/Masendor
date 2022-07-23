def camera_zoom_change(self):
    self.camera_pos[0] = self.base_camera_pos[0] * self.camera_zoom
    self.camera_pos[1] = self.base_camera_pos[1] * self.camera_zoom
    self.show_map.change_scale(self.camera_zoom)
    if self.game_state == "battle":  # only have delay in battle mode
        self.map_scale_delay = 0.001
    self.camera_fix()
