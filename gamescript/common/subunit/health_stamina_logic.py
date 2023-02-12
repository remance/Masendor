import random

infinity = float("inf")


def health_stamina_logic(self, dt):
    """Health and stamina calculation"""
    if self.health != infinity:
        if self.hp_regen > 0 and self.health < self.max_health:  # hp regen cannot regen beyond max hp
            self.health += self.hp_regen * dt  # regen hp back based on time and regen stat
            if self.health > self.max_health:
                self.health = self.max_health  # Cannot exceed max health
        elif self.hp_regen < 0:  # negative regen
            self.health += self.hp_regen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)

        if self.health < 0:
            self.health = 0  # can't have negative hp
        elif self.health > self.max_health:
            self.health = self.max_health  # hp can't exceed max hp (would increase number of troop)

    if self.stamina != infinity:
        if self.stamina < self.max_stamina:
            if self.stamina < 0:
                self.stamina = 0
            self.stamina = self.stamina + (dt * self.stamina_regen)  # regen
        else:  # stamina cannot exceed the max stamina
            self.stamina = self.max_stamina


