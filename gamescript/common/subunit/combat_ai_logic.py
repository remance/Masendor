melee_attack_command_action = ({"name": "Action 0", "melee attack": True}, {"name": "Action 1", "melee attack": True})

range_attack_command_action = {True: ({"name": "Action 0", "range attack": True, "arc shot": True},
                                      {"name": "Action 1", "range attack": True, "arc shot": True}),
                               False: ({"name": "Action 0", "range attack": True, "arc shot": False},
                                       {"name": "Action 1", "range attack": True, "arc shot": False})}

range_move_attack_command_action = {True: ({"name": "Action 0", "range attack": True, "move attack": True,
                                            "movable": True, "arc shot": True},
                                           {"name": "Action 1", "range attack": True, "move attack": True,
                                            "movable": True, "arc shot": True}),
                                    False: ({"name": "Action 0", "range attack": True, "move attack": True,
                                             "movable": True, "arc shot": False},
                                            {"name": "Action 1", "range attack": True, "move attack": True,
                                             "movable": True, "arc shot": False})}


def combat_ai_logic(self):
    if self.nearest_enemy[0][1] < self.melee_distance_zone:  # enemy in subunit's melee zone
        self.in_melee_combat_timer = 3  # consider to be in melee for 3 seconds before reset
        self.attack_target = self.nearest_enemy[0][0]
        self.new_angle = self.set_rotate(self.attack_target.base_pos)
        if not self.command_action and not self.current_action:  # if melee combat (engaging anyone on any side)
            if self.equipped_weapon != self.melee_weapon_set[0]:  # swap to melee weapon when enemy near
                self.swap_weapon(self.melee_weapon_set[0])
            else:
                for weapon in self.weapon_cooldown:
                    if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon] and \
                            self.attack_target.base_pos.distance_to(self.front_pos) <= self.melee_range[weapon]:
                        self.command_action = melee_attack_command_action[weapon]
                        break

    elif self.in_melee_combat_timer == 0 and not self.command_action and (not self.current_action or
            "Action " not in self.current_action["name"]):  # no nearby enemy melee threat
        self.attack_target = None
        can_shoot = False
        if self.ammo_now:  # range attack
            if self.equipped_weapon not in self.ammo_now:
                if not self.current_action:
                    for this_set in self.range_weapon_set:  # find weapon set with range weapon that has ammo
                        self.swap_weapon(this_set)
                        break

            elif self.move is False or self.check_special_effect("Shoot While Moving"):  # Find target to shoot
                if self.shoot_range[0] >= self.nearest_enemy[0][1] or self.shoot_range[1] >= self.nearest_enemy[0][1]: # has enemy in range
                    for enemy in self.nearest_enemy:
                        for weapon in self.ammo_now[self.equipped_weapon]:
                            # can shoot if reload finish, in shoot range and attack pos target exist
                            if self.ammo_now[self.equipped_weapon][weapon] > 0 and \
                                    self.shoot_range[weapon] >= enemy[1] and \
                                    (self.move is False or self.check_special_effect("Stationary", weapon=weapon) is False):
                                weapon_arc_shot = self.check_special_effect("Arc Shot", weapon=weapon)
                                if self.check_special_effect("Arc Shot Only",
                                                             weapon=weapon) is False:  # find the closest enemy subunit not block by friend
                                    if self.check_line_of_sight(enemy[0].base_pos) is False:
                                        can_shoot = True
                                        arc_shot = False

                                if can_shoot is False and weapon_arc_shot:  # check for arc shot
                                    can_shoot = True
                                    arc_shot = True

                                if can_shoot:
                                    self.attack_target = enemy[0]  # replace attack_target with enemy unit object
                                    self.attack_pos = self.attack_target.base_pos  # replace attack_pos with enemy unit pos
                                    if self.move:
                                        if self.check_special_effect("Shoot While Moving") and \
                                            self.check_special_effect("Stationary", weapon=weapon) is False:  # shoot while moving
                                            self.command_action = range_move_attack_command_action[arc_shot][weapon]
                                    else:
                                        self.command_action = range_attack_command_action[arc_shot][weapon]

                                    if self.move is False:
                                        self.new_angle = self.set_rotate(self.attack_target.base_pos)
                                    break
                        if can_shoot:  # found target to shoot
                            break

        else:
            if self.equipped_weapon != self.melee_weapon_set[0] and not self.command_action and not self.current_action:
                self.swap_weapon(self.melee_weapon_set[0])  # swap to melee weapon by default
