def combat_ai_logic(self):
    if self.nearest_enemy[1] < self.melee_distance_zone:  # enemy in subunit's melee zone
        self.in_melee_combat_timer = 3  # consider to be in melee for 3 seconds before reset
        self.attack_target = self.nearest_enemy[0]
        self.new_angle = self.set_rotate(self.attack_target.base_pos)
        if not self.command_action and not self.current_action:  # if melee combat (engaging anyone on any side)
            if self.equipped_weapon != self.melee_weapon_set[0]:  # swap to melee weapon when enemy near
                self.swap_weapon(self.melee_weapon_set[0])
            else:
                for weapon in self.weapon_cooldown:
                    if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon] and \
                            self.attack_target.base_pos.distance_to(self.front_pos) <= self.melee_range[weapon]:
                        self.command_action = self.melee_attack_command_action[weapon]
                        break

    elif not self.in_melee_combat_timer and not self.command_action:  # no nearby enemy melee threat
        self.attack_target = None
        if self.ammo_now:  # range attack
            if self.equipped_weapon not in self.ammo_now:
                if not self.current_action:
                    for this_set in self.range_weapon_set:  # find weapon set with range weapon that has ammo
                        self.swap_weapon(this_set)
                        break

            elif (not self.current_action or "Action " not in self.current_action["name"]) and not self.move_speed or \
                    self.shoot_while_moving:  # Find target to shoot
                if self.shoot_range[0] >= self.nearest_enemy[1] or self.shoot_range[1] >= self.nearest_enemy[1]:  # has enemy in range
                    for weapon in self.ammo_now[self.equipped_weapon]:
                        # can shoot if reload finish, in shoot range and attack pos target exist
                        if self.ammo_now[self.equipped_weapon][weapon] and self.shoot_range[weapon] >= self.nearest_enemy[1]:
                            self.attack_target = self.nearest_enemy[0]  # replace attack_target with enemy unit object
                            self.attack_pos = self.attack_target.base_pos  # replace attack_pos with enemy unit pos
                            if self.move_speed:  # moving
                                if self.check_special_effect("Stationary", weapon=weapon) is False:
                                    # weapon can shoot while moving
                                    if "move loop" in self.current_action and "charge" not in self.current_action:
                                        self.interrupt_animation = True
                                        if "Walk" in self.current_action["Name"]:
                                            self.command_action = self.walk_shoot_command_action[weapon]
                                        elif "Run" in self.current_action["Name"]:
                                            self.command_action = self.run_shoot_command_action[weapon]
                            else:
                                self.command_action = self.range_attack_command_action[weapon]

                            if not self.move_speed:  # only face target when standing still shooting
                                self.new_angle = self.set_rotate(self.attack_target.base_pos)
                            break

        else:
            if self.equipped_weapon != self.melee_weapon_set[0] and not self.current_action:
                self.swap_weapon(self.melee_weapon_set[0])  # swap to melee weapon by default
