def change_pos_scale(self):
    """Change position variable to new camera scale"""
    self.number_pos = (self.base_number_pos[0] * self.screen_scale[0] * self.camera_zoom,
                       self.base_number_pos[1] * self.screen_scale[1] * self.camera_zoom)
