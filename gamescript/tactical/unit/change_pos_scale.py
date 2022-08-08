def change_pos_scale(self):
    """Change position variable to new camera scale"""
    self.number_pos = (self.base_number_pos[0] * self.screen_scale[0] * (11 - self.zoom),
                       self.base_number_pos[1] * self.screen_scale[1] * (11 - self.zoom))
