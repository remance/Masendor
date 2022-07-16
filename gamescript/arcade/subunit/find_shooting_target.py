def find_shooting_target(self, unit_state):
    """Get nearby enemy target from nearby_enemy list if not targeting anything yet"""
    self.attack_target = list(self.unit.nearby_enemy.keys())[0]  # replace attack_target with enemy unit object
    self.attack_pos = self.attack_target.base_pos  # replace attack_pos with enemy unit pos
    for shoot_range in self.shoot_range:
        if shoot_range >= self.attack_pos.distance_to(self.base_pos):
            self.state = 11
            if unit_state in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif unit_state in (2, 4, 6):  # Run and shoot
                self.state = 13

