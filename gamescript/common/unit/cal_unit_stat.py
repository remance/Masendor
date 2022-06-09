def cal_unit_stat(self, how_many, all_speed, all_shoot_range, battle_start):
    self.stamina = self.stamina / how_many  # Average stamina of all subunit
    self.morale = self.morale / how_many  # Average morale of all subunit
    self.speed = min(all_speed)  # use the slowest subunit
    self.walk_speed, self.run_speed = self.speed / 2, self.speed
    if self.state in (1, 3, 5):
        self.rotate_speed = self.walk_speed * 50 / (len(self.subunit_id_array[0]) * len(
            self.subunit_id_array))  # rotate speed is based on move speed and unit block size (not subunit total number)
    else:
        self.rotate_speed = self.run_speed * 50 / (len(self.subunit_id_array[0]) * len(self.subunit_id_array))

    if self.rotate_speed > 20:
        self.rotate_speed = 20  # state 10 melee combat rotate is auto placement
    elif self.rotate_speed < 1:  # no less than speed 1, it will be too slow or can't rotate with speed 0
        self.rotate_speed = 1

    if len(all_shoot_range) > 0:
        self.max_range = max(all_shoot_range)  # Max shoot range of all subunit
        self.min_range = min(all_shoot_range)  # Min shoot range of all subunit
    if battle_start:  # Only do once when self start
        self.max_stamina = self.stamina
        self.max_morale = self.morale
        self.max_health = self.troop_number
    self.morale_state = 100
    self.stamina_state = 100
    if self.max_morale != float("inf"):
        self.morale_state = round((self.morale * 100) / self.max_morale)
    if self.max_stamina != float("inf"):
        self.stamina_state = round((self.stamina * 100) / self.max_stamina)
