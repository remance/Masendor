def troop_loss(self, loss):
    self.troop_number -= loss
    self.battle.team_troop_number[self.team] -= loss
