def range_weapon_selection(self, allow_swap):
    prefer_weapon = 0
    for key, value in self.magazine_count[self.equipped_weapon]:
        if value > 0 or self.ammo_now[self.equipped_weapon][key] > 0:
            prefer_weapon
            break
    if allow_swap:
        unequipped_weapon = 0
        if self.equipped_weapon == 0:
            unequipped_weapon = 1
        if any(value > 0 for value in self.magazine_count[unequipped_weapon].values()):
            prefer_weapon = 0
            self.equipped_weapon = unequipped_weapon
            self.swap_weapon()
            for key, value in self.magazine_count[self.equipped_weapon]:
                if value > 0 or self.ammo_now[self.equipped_weapon][key] > 0:
                    break
