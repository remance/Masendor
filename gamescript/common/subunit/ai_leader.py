def ai_leader(self):
    self.follow_target = self.nearest_enemy[0].base_pos
    self.command_target = self.nearest_enemy[0].base_pos
