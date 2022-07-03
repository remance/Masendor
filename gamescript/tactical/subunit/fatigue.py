def fatigue(self):
    if self.max_stamina > 100:
        self.max_stamina = self.max_stamina - (self.timer * 0.05)  # Max stamina gradually decrease over time - (self.timer * 0.05)
        self.stamina75 = self.max_stamina * 0.75
        self.stamina50 = self.max_stamina * 0.5
        self.stamina25 = self.max_stamina * 0.25
        self.stamina5 = self.max_stamina * 0.05
