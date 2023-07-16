infinity = float("inf")


def health_stamina_logic(self, dt):
    """Health and stamina calculation"""
    if self.health != infinity:
        self.health += self.hp_regen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)

        if self.health < 0:
            self.health = 0  # can't have negative hp
        elif self.health > self.max_health:
            self.health = self.max_health  # hp can't exceed max hp

    if self.stamina != infinity:
        if self.stamina < self.max_stamina:
            self.stamina += (self.stamina_regen * dt)  # regen
            if self.stamina < 0:
                self.stamina = 0
            elif self.stamina > self.max_stamina:  # stamina cannot exceed the max stamina
                self.stamina = self.max_stamina
