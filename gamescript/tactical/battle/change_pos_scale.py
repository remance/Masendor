def change_pos_scale(self):
    """Change position variable to new camera scale"""
    self.true_number_pos = self.number_pos * (11 - self.camera_zoom)
