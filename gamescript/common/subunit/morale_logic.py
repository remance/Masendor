def morale_logic(self, dt):
    """Morale check"""
    if self.base_morale < self.max_morale:
        if self.base_morale < 0:  # morale cannot be negative
            self.base_morale = 0
        self.base_morale += (
                dt * self.morale_regen)  # Morale replenish
