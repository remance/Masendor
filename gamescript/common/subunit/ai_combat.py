def ai_combat(self):
    if "charge" not in self.current_action:
        if self.nearest_enemy[1] < self.melee_distance_zone:  # enemy in subunit's melee zone
            self.in_melee_combat_timer = 3  # consider to be in melee for 3 seconds before reset
            self.attack_target = self.nearest_enemy[0]
            if not self.command_action and not self.current_action:  # if melee combat (engaging anyone on any side)
                self.new_angle = self.set_rotate(self.attack_target.base_pos)
                if self.equipped_weapon != self.melee_weapon_set[0]:  # swap to melee weapon when enemy near
                    self.swap_weapon(self.melee_weapon_set[0])
                else:
                    if self.available_enemy_near_skill:  # use enemy near skill first
                        self.command_action = {"skill": self.available_enemy_near_skill[0]}
                    elif self.available_melee_skill:  # then consider melee skill
                        self.command_action = {"skill": self.available_melee_skill[0]}
                    else:
                        for weapon in self.weapon_cooldown:
                            if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon] and \
                                    self.attack_target.base_pos.distance_to(self.front_pos) <= self.melee_range[weapon]:
                                self.command_action = self.melee_attack_command_action[weapon]

                                if self.unit_leader and not self.unit_leader.command_action and not self.unit_leader.current_action:
                                    if self.unit_leader.available_unit_melee_skill:
                                        self.unit_leader.command_action = {"skill": self.unit_leader.available_unit_melee_skill[0]}
                                elif self.leader and not self.leader.command_action and not self.leader.current_action:
                                    if self.leader.available_troop_melee_skill:
                                        self.leader.command_action = {"skill": self.leader.available_troop_melee_skill[0]}

                                break

        elif not self.in_melee_combat_timer and not self.command_action and not self.manual_shoot:
            # no nearby enemy melee threat
            self.attack_target = None
            if self.ammo_now:  # range attack
                if self.equipped_weapon not in self.ammo_now:
                    if not self.current_action:
                        for this_set in self.range_weapon_set:  # find weapon set with range weapon that has ammo
                            self.swap_weapon(this_set)
                            break
                else:
                    if self.available_range_skill:  # use range skill first
                        self.command_action = {"skill": self.available_range_skill[0]}
                    elif "range attack" not in self.current_action and "range attack" not in self.command_action and \
                            (not self.move_speed or self.shoot_while_moving):  # Find target to shoot
                        if self.shoot_range[0] >= self.nearest_enemy[1] or self.shoot_range[1] >= self.nearest_enemy[1]:  # has enemy in range
                            for weapon in self.ammo_now[self.equipped_weapon]:
                                # can shoot if reload finish, in shoot range and attack pos target exist
                                if self.ammo_now[self.equipped_weapon][weapon] > 0 and self.shoot_range[weapon] >= self.nearest_enemy[1]:
                                    self.attack_target = self.nearest_enemy[0]  # replace attack_target with enemy unit object
                                    self.attack_pos = self.attack_target.base_pos  # replace attack_pos with enemy unit pos
                                    if self.move_speed:  # moving
                                        if not self.check_special_effect("Stationary", weapon=weapon):
                                            # weapon can shoot while moving
                                            if "movable" in self.current_action and "charge" not in self.current_action:
                                                self.interrupt_animation = True
                                                if "walk" in self.current_action:
                                                    self.command_action = self.walk_shoot_command_action[weapon]
                                                elif "run" in self.current_action:
                                                    self.command_action = self.run_shoot_command_action[weapon]
                                    else:
                                        self.command_action = self.range_attack_command_action[weapon]
                                        self.new_angle = self.set_rotate(self.attack_target.base_pos)

                                    if self.unit_leader and not self.unit_leader.command_action and not self.unit_leader.current_action:
                                        if self.unit_leader.available_unit_range_skill:
                                            self.unit_leader.command_action = {
                                                "skill": self.unit_leader.available_unit_range_skill[0]}
                                    elif self.leader and not self.leader.command_action and not self.leader.current_action:
                                        if self.leader.available_troop_range_skill:
                                            self.leader.command_action = {
                                                "skill": self.leader.available_troop_range_skill[0]}

                                    break

            else:
                if self.equipped_weapon != self.melee_weapon_set[0] and not self.current_action:
                    self.swap_weapon(self.melee_weapon_set[0])  # swap to melee weapon by default
