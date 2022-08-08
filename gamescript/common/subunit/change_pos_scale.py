def change_pos_scale(self):
    """Change position variable to new camera scale"""
    self.pos = (self.base_pos[0] * self.screen_scale[0] * self.zoom,
                self.base_pos[1] * self.screen_scale[1] * self.zoom)
    self.rect.center = self.pos
    self.dmg_rect.center = self.pos
