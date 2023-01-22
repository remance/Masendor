def check_weapon_cooldown(self, dt):
    for weapon in self.weapon_cooldown:
        if self.weapon_cooldown[weapon] < self.weapon_speed[weapon]:
            self.weapon_cooldown[weapon] += dt
        else:
            if self.equipped_weapon in self.ammo_now and weapon in self.ammo_now[self.equipped_weapon] and \
                    self.ammo_now[self.equipped_weapon][weapon] == 0:  # finish reload, add ammo
                self.ammo_now[self.equipped_weapon][weapon] = self.magazine_size[self.equipped_weapon][weapon]
                self.magazine_count[self.equipped_weapon][weapon] -= 1
                self.weapon_cooldown[weapon] = 0  # reset cooldown
