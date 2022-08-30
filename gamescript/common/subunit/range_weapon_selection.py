def range_weapon_selection(self):
    if len(self.ammo_now) > 0:
        for weapon_set in self.magazine_count:
            for key, value in self.magazine_count[weapon_set]:
                if value > 0 or self.ammo_now[self.equipped_weapon][key] > 0:
                    if self.equipped_weapon != weapon_set:
                        self.equipped_weapon = weapon_set
                        self.swap_weapon()
                    break
