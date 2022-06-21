infinity = float("inf")


def morale_logic(self, dt, parent_state):
    # v Morale check
    if self.max_morale != infinity:
        if self.base_morale < self.max_morale:
            if self.state != 99:  # If not missing start_set leader can replenish morale
                self.base_morale += (dt * self.stamina_state_cal * self.morale_regen)  # Morale replenish based on stamina

            if self.base_morale < 0:  # morale cannot be negative
                self.base_morale = 0

        elif self.base_morale > self.max_morale:
            self.base_morale -= dt  # gradually reduce morale that exceed the starting max amount

        if self.state in (95, 99):  # disobey or broken state, morale gradually decrease until recover
            self.base_morale -= dt * self.mental
