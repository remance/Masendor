def change_pos_scale(self):
    """Change position variable to new camera scale"""
    self.pos = (self.base_pos[0] * self.screen_scale[0] * self.camera_zoom,
                self.base_pos[1] * self.screen_scale[1] * self.camera_zoom)
    self.rect.center = self.pos
