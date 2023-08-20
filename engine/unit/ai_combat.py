from random import getrandbits

opposite_index = (1, 0)


def ai_combat(self):
    self.melee_target = None
    self.nearest_enemy = self.near_enemy[0]
    melee_distance_check = self.melee_distance_zone
    if self.manual_control and not self.take_melee_dmg:  # during manual aim, reduce melee zone distance
        melee_distance_check = 5

    if self.nearest_enemy[0].alive:
        if self.nearest_enemy[1] < melee_distance_check:  # enemy in unit's melee zone
            self.melee_target = self.nearest_enemy[0]
            self.in_melee_combat_timer = 2  # consider to be in melee for 2 seconds before reset
    else:  # find new enemy that not dead
        self.near_enemy.pop(0)
        while self.near_enemy and not self.near_enemy[0][0].alive:
            self.near_enemy.pop(0)
        if self.near_enemy:
            self.nearest_enemy = self.near_enemy[0]
            if self.nearest_enemy[1] < melee_distance_check or (self.leader and self.leader.in_melee_combat_timer):
                self.melee_target = self.nearest_enemy[0]
                self.in_melee_combat_timer = 2  # consider to be in melee for 2 seconds before reset

    if "hold" in self.current_action:  # already perform an attack with holding
        weapon = self.current_action["weapon"]
        target_distance = self.nearest_enemy[0].base_pos.distance_to(self.base_pos)
        if self.hold_timer > 5 or \
                (((weapon in self.equipped_block_weapon and self.take_melee_dmg) or
                  weapon in self.equipped_charge_block_weapon) and target_distance <= self.melee_range[weapon] or
                 (target_distance > self.melee_def_range[weapon] and self.hold_timer > 3)):
            # block take melee dmg or in charge block
            # with enemy in range to hit or block too long when no enemy near, release to attack back
            # AI will not hold longer than 5 seconds no matter what
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
                    if not self.melee_target or \
                            self.melee_target.base_pos.distance_to(self.base_pos) <= self.melee_range[weapon]:
                        # enemy in range to hit or no enemy, release hold
                        self.current_action = self.melee_attack_command_action[weapon]
                        self.release_timer = self.hold_timer
                return
    else:  # not already holding attack
        # if self.leader and self.leader:
        #     for weapon in self.weapon_cooldown:
        #         if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon]:
        #             if weapon in self.equipped_block_weapon
        if self.in_melee_combat_timer and self.melee_target:  # enemy in unit's melee zone
            if not self.current_action:  # only rotate to enemy when no current action
                self.new_angle = self.set_rotate(self.melee_target.base_pos)
            if "weapon" not in self.current_action and "weapon" not in self.command_action:
                # not about to do attack action already
                if self.equipped_weapon != self.melee_weapon_set:  # swap to melee weapon when enemy near
                    self.command_action = self.swap_weapon_command_action[self.melee_weapon_set]
                else:
                    if self.available_enemy_near_skill:  # use enemy near skill first
                        self.skill_command_input(0, self.available_enemy_near_skill,
                                                 pos_target=self.melee_target.base_pos)
                    elif self.available_melee_skill:  # then consider melee skill
                        self.skill_command_input(0, self.available_melee_skill,
                                                 pos_target=self.melee_target.base_pos)
                    else:  # no skill to use, check for melee attack
                        for weapon in self.weapon_cooldown:
                            if self.weapon_cooldown[weapon] >= self.weapon_speed[weapon]:
                                if self.melee_target.base_pos.distance_to(self.base_pos) <= self.melee_range[weapon]:
                                    # leader troop and unit melee condition skill check
                                    if self.group_leader and not self.group_leader.player_control and \
                                            not self.group_leader.command_action:
                                        if self.group_leader.available_unit_melee_skill:
                                            self.group_leader.skill_command_input(0,
                                                                                  self.group_leader.available_unit_melee_skill,
                                                                                  pos_target=self.base_pos)
                                    elif self.leader and not self.leader.player_control and \
                                            not self.leader.command_action:
                                        if self.leader.available_troop_melee_skill:
                                            self.leader.skill_command_input(0,
                                                                            self.leader.available_troop_melee_skill,
                                                                            pos_target=self.base_pos)

                                    elif weapon in self.equipped_block_weapon and \
                                            self.weapon_cooldown[opposite_index[weapon]] > 1:  # consider blocking first
                                        self.command_action = self.melee_hold_command_action[weapon]
                                    elif (weapon in self.equipped_power_weapon or self.equipped_timing_start_weapon[
                                        weapon]) and not not getrandbits(1):
                                        # random chance to hold
                                        self.command_action = self.melee_hold_command_action[weapon]
                                    else:  # perform normal attack
                                        self.command_action = self.melee_attack_command_action[weapon]

                                else:  # still too far consider using charge_block weapon
                                    if weapon in self.equipped_charge_block_weapon:  # consider blocking first
                                        self.command_action = self.melee_hold_command_action[weapon]
                                return

        elif self.ammo_now and not self.in_melee_combat_timer:
            if "weapon" not in self.current_action and "weapon" not in self.command_action and not self.manual_control:
                # no nearby enemy melee threat and has range weapon to shoot
                if self.equipped_weapon not in self.ammo_now:
                    if not self.command_action:
                        for this_set in self.range_weapon_set:  # find weapon set with range weapon that has ammo
                            self.command_action = self.swap_weapon_command_action[this_set]
                            return
                else:
                    if "range attack" not in self.current_action and "range attack" not in self.command_action and \
                            (not self.move_speed or self.shoot_while_moving):  # Find target to shoot
                        if self.max_shoot_range >= self.nearest_enemy[1]:  # has enemy in shoot range
                            if self.available_range_skill:  # use range skill first
                                self.skill_command_input(0, self.available_range_skill, pos_target=self.base_pos)
                            else:
                                for weapon in self.ammo_now[self.equipped_weapon]:
                                    # can shoot if reload finish, in shoot range and attack pos target exist
                                    if self.ammo_now[self.equipped_weapon][weapon] and \
                                            self.shoot_range[weapon] >= self.nearest_enemy[1]:
                                        if self.move_speed:  # moving
                                            if not self.check_special_effect("Stationary", weapon=weapon):
                                                # weapon can shoot while moving
                                                if "movable" in self.current_action:
                                                    self.interrupt_animation = True  # stop current move animation
                                                    if "walk" in self.current_action:
                                                        self.command_action = self.range_walk_command_action[weapon]
                                                    elif "run" in self.current_action:
                                                        self.command_action = self.range_run_command_action[weapon]
                                        else:
                                            if self.equipped_timing_start_weapon[
                                                weapon] or weapon in self.equipped_power_weapon:
                                                # consider using hold for power or timing
                                                self.command_action = self.range_hold_command_action[weapon]
                                            else:
                                                self.command_action = self.range_attack_command_action[weapon]
                                            self.new_angle = self.set_rotate(self.nearest_enemy[0].base_pos)

                                        if self.group_leader and not self.group_leader.player_control and \
                                                not self.group_leader.command_action and \
                                                not self.group_leader.current_action:
                                            if self.group_leader.available_unit_range_skill:
                                                self.group_leader.skill_command_input(0,
                                                                                      self.group_leader.available_unit_range_skill,
                                                                                      pos_target=self.base_pos)
                                        elif self.leader and not self.leader.player_control and not self.leader.command_action and not self.leader.current_action:
                                            if self.leader.available_troop_range_skill:
                                                self.leader.skill_command_input(0,
                                                                                self.leader.available_troop_range_skill,
                                                                                pos_target=self.base_pos)

                                        return

        else:
            if self.equipped_weapon != self.melee_weapon_set and not self.current_action:
                # swap to melee weapon by default
                self.command_action = self.swap_weapon_command_action[self.melee_weapon_set]
