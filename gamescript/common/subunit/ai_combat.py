from random import getrandbits

opposite_index = (1, 0)


def ai_combat(self):
    if "charge" not in self.current_action:
        if self.nearest_enemy[1] < self.melee_distance_zone:  # enemy in subunit's melee zone
            self.attack_subunit = self.nearest_enemy[0]
            self.in_melee_combat_timer = 3  # consider to be in melee for 3 seconds before reset

        if "hold" in self.current_action:  # already perform an attack with holding
            weapon = self.current_action["weapon"]
            target_distance = self.nearest_enemy[0].base_pos.distance_to(self.front_pos)
            if ((weapon in self.equipped_block_weapon and self.take_melee_dmg) or \
                    weapon in self.equipped_charge_block_weapon) and \
                    target_distance <= self.melee_range[weapon] or \
                    (target_distance > self.melee_def_range[weapon] and self.hold_timer > 3):
                # block take melee dmg or in charge block
                # with enemy in range to hit or block too long when no enemy near, release to attack back
                self.current_action = self.melee_attack_command_action[weapon]
                self.release_timer = self.hold_timer
                return

            if self.hold_timer > 1:
                if (self.equipped_timing_start_weapon[weapon] and
                    self.hold_timer > self.equipped_timing_start_weapon[weapon]) or \
                        weapon in self.equipped_power_weapon:  # wait till timing reach
                    if "range attack" in self.current_action:
                        self.current_action = self.range_attack_command_action[weapon]
                        self.release_timer = self.hold_timer
                    else:
                        if self.attack_subunit.base_pos.distance_to(self.front_pos) <= self.melee_range[weapon]:
                            # enemy in range to hit
                            self.current_action = self.melee_attack_command_action[weapon]
                            self.release_timer = self.hold_timer
                    return
        else:
            if self.in_melee_combat_timer > 0 and self.attack_subunit:  # enemy in subunit's melee zone
                if not self.current_action:  # only rotate to enemy when no current action
                    self.new_angle = self.set_rotate(self.attack_subunit.base_pos)
                if "weapon" not in self.current_action:
                    if self.equipped_weapon != self.melee_weapon_set[0]:  # swap to melee weapon when enemy near
                        self.swap_weapon(self.melee_weapon_set[0])
                    else:
                        if self.available_enemy_near_skill:  # use enemy near skill first
                            self.skill_command_input(0, self.available_enemy_near_skill, pos_target=self.attack_subunit.base_pos)
                        elif self.available_melee_skill:  # then consider melee skill
                            self.skill_command_input(0, self.available_melee_skill, pos_target=self.attack_subunit.base_pos)
                        else:
                            for weapon in self.weapon_cooldown:
                                if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon]:
                                    if self.attack_subunit.base_pos.distance_to(self.front_pos) <= self.melee_range[weapon]:
                                        if weapon in self.equipped_block_weapon and self.weapon_cooldown[opposite_index[weapon]] > 1:  # consider blocking first
                                            self.command_action = self.melee_hold_command_action[weapon]
                                        elif (weapon in self.equipped_power_weapon or self.equipped_timing_start_weapon[weapon]) and not not getrandbits(1):
                                            # random chance to hold
                                            self.command_action = self.melee_hold_command_action[weapon]
                                        else:  # perform normal attack
                                            self.command_action = self.melee_attack_command_action[weapon]

                                        # leader troop and unit melee condition skill check
                                        if self.unit_leader and not self.unit_leader.player_control and \
                                                not self.unit_leader.command_action and \
                                                not self.unit_leader.current_action:
                                            if self.unit_leader.available_unit_melee_skill:
                                                self.unit_leader.skill_command_input(0, self.unit_leader.available_unit_melee_skill, pos_target=self.base_pos)
                                        elif self.leader and not self.leader.player_control and \
                                                not self.leader.command_action and not self.leader.current_action:
                                            if self.leader.available_troop_melee_skill:
                                                self.leader.skill_command_input(0, self.leader.available_troop_melee_skill, pos_target=self.base_pos)

                                    else:  # still too far consider using chargeblock
                                        if weapon in self.equipped_charge_block_weapon:  # consider blocking first
                                            self.command_action = self.melee_hold_command_action[weapon]
                                    return

            elif not self.in_melee_combat_timer and "weapon" not in self.current_action and not self.manual_shoot:
                # no nearby enemy melee threat
                self.attack_subunit = None
                if self.ammo_now:  # range attack
                    if self.equipped_weapon not in self.ammo_now:
                        if not self.current_action:
                            for this_set in self.range_weapon_set:  # find weapon set with range weapon that has ammo
                                self.swap_weapon(this_set)
                                return
                    else:
                        if "range attack" not in self.current_action and "range attack" not in self.command_action and \
                                (not self.move_speed or self.shoot_while_moving):  # Find target to shoot
                            if self.shoot_range[0] >= self.nearest_enemy[1] or self.shoot_range[1] >= self.nearest_enemy[1]:  # has enemy in range
                                if self.available_range_skill:  # use range skill first
                                    self.skill_command_input(0, self.available_range_skill, pos_target=self.base_pos)
                                else:
                                    for weapon in self.ammo_now[self.equipped_weapon]:
                                        # can shoot if reload finish, in shoot range and attack pos target exist
                                        if self.ammo_now[self.equipped_weapon][weapon] > 0 and self.shoot_range[weapon] >= self.nearest_enemy[1]:
                                            self.attack_subunit = self.nearest_enemy[0]  # replace with enemy object
                                            self.attack_pos = self.attack_subunit.base_pos  # replace with enemy pos
                                            if self.move_speed:  # moving
                                                if not self.check_special_effect("Stationary", weapon=weapon):
                                                    # weapon can shoot while moving
                                                    if "movable" in self.current_action and "charge" not in self.current_action:
                                                        self.show_frame = 0  # just restart frame
                                                        if "walk" in self.current_action:
                                                            self.current_action = self.range_walk_command_action[weapon]
                                                        elif "run" in self.current_action:
                                                            self.current_action = self.range_run_command_action[weapon]
                                            else:
                                                if self.equipped_timing_start_weapon[weapon] or weapon in self.equipped_power_weapon:
                                                    # consider using hold for power or timing
                                                    self.command_action = self.range_hold_command_action[weapon]
                                                else:
                                                    self.command_action = self.range_attack_command_action[weapon]
                                                self.new_angle = self.set_rotate(self.attack_subunit.base_pos)

                                            if self.unit_leader and not self.unit_leader.player_control and not self.unit_leader.command_action and not self.unit_leader.current_action:
                                                if self.unit_leader.available_unit_range_skill:
                                                    self.unit_leader.skill_command_input(0, self.unit_leader.available_unit_range_skill, pos_target=self.base_pos)
                                            elif self.leader and not self.leader.player_control and not self.leader.command_action and not self.leader.current_action:
                                                if self.leader.available_troop_range_skill:
                                                    self.leader.skill_command_input(0, self.leader.available_troop_range_skill, pos_target=self.base_pos)

                                            return

                else:
                    if self.equipped_weapon != self.melee_weapon_set[0] and not self.current_action:
                        self.swap_weapon(self.melee_weapon_set[0])  # swap to melee weapon by default
