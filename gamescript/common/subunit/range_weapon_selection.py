def range_weapon_selection(self, player_order=False):
    if len(self.ammo_now) > 0 and self.equipped_weapon not in self.ammo_now:
        for weapon_set in self.magazine_count:
            for key, value in self.magazine_count[weapon_set].items():
                if value > 0:
                    if self.equipped_weapon != weapon_set:
                        self.equipped_weapon = weapon_set
                        if player_order:
                            self.player_equipped_weapon = self.equipped_weapon
                        self.swap_weapon()
                    break
