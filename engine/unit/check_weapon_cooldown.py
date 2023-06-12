def check_weapon_cooldown(self, dt):
    for weapon in self.weapon_cooldown:
        if self.equipped_weapon in self.ammo_now and weapon in self.ammo_now[self.equipped_weapon]:
            if self.ammo_now[self.equipped_weapon][weapon] == 0:
                if self.weapon_cooldown[weapon] < self.weapon_speed[weapon]:  # only increase cooldown when reloading
                    self.weapon_cooldown[weapon] += dt
                else:  # finish reload, add ammo
                    self.ammo_now[self.equipped_weapon][weapon] = self.magazine_size[self.equipped_weapon][weapon]
                    self.magazine_count[self.equipped_weapon][weapon] -= 1
                    self.weapon_cooldown[weapon] = 0  # reset cooldown
        elif self.weapon_cooldown[weapon] < self.weapon_speed[weapon]:
            self.weapon_cooldown[weapon] += dt
