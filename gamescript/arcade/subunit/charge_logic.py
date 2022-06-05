def charge_logic(self, *args):
    if self.state == 4 and self.charge_momentum < 5:
        self.charge_momentum += self.timer * (self.speed / 50)

    elif self.charge_momentum > 1:  # reset charge momentum if charge skill not active
        self.charge_momentum -= self.timer * (self.speed / 50)
        if self.charge_momentum <= 1:
            self.charge_momentum = 1
