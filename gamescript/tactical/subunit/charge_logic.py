def charge_logic(self, parent_state):
    if self.state in (4, 13) and parent_state != 10 and self.attacking and self.unit.move_rotate is False and \
            self.base_pos.distance_to(self.base_target) < 50:  # charge skill only when running to melee

        self.charge_momentum += self.timer * (self.speed / 50)
        if self.charge_momentum >= 5:
            self.use_skill(0)  # Use charge skill
            self.unit.charging = True
            self.charge_momentum = 5

    elif self.charge_momentum > 1:  # reset charge momentum if charge skill not active
        self.charge_momentum -= self.timer * (self.speed / 50)
        if self.charge_momentum <= 1:
            self.unit.charging = False
            self.charge_momentum = 1
