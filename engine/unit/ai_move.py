from math import cos, sin, radians

from pygame import Vector2

follow_distance = 20
melee_follow_distance = 80
stay_formation_distance = 1


def ai_move(self, dt):
    # TODO add condition to check for moving to camp for respawn troop and heal
    if self.leader:  # has higher leader
        if self.is_leader:  # is leader character
            follow_order = self.leader.army_follow_order
        else:  # is troop
            follow_order = self.leader.group_follow_order

        if follow_order in ("Stay Formation", "Stay Here"):
            follow = stay_formation_distance
        else:
            if self.in_melee_combat_timer:
                follow = melee_follow_distance
            else:
                if not self.leader.move_speed:  # try get in formation anyway if leader standing still
                    follow = stay_formation_distance
                else:
                    follow = follow_distance
        if self.charge_target:
            move_target = self.charge_target
            if move_target.distance_to(self.base_pos) < 1:
                self.charge_target = None
        else:
            move_target = self.follow_target
    else:  # movement for army leader
        if self.move_path:
            move_target = self.move_path[0]
        else:
            move_target = self.follow_target
        follow_order = "Free"
        follow = 1

    move_distance = move_target.distance_to(self.base_pos)
    if follow_order != "Free":  # move to assigned location
        if "charge" in self.leader.current_action or self.charge_target:
            # leader charging, charge with leader or has player charge target do not auto move to enemy on its own
            if not self.melee_target or "charge" in self.current_action:
                # keep charging if not stop yet or no enemy in melee distance
                if not self.charge_target:
                    self.ai_charge_timer = 3
                if self.equipped_weapon != self.charge_weapon_set:  # swap to best charge weapon set for charge
                    self.command_action = self.swap_weapon_command_action[self.charge_weapon_set]
                else:  # already equipped charge weapon set
                    # charge movement based on angle instead of formation pos
                    if self.available_move_skill and not self.command_action:  # use move skill first
                        self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                    else:
                        charge_target = None
                        if self.is_leader:
                            if self.nearest_enemy and "range" not in self.group_type:
                                # melee group leader charge to nearby enemy
                                charge_target = self.nearest_enemy[0].base_pos
                        else:  # charge for troop
                            if self.charge_target:
                                charge_target = self.charge_target
                            else:
                                charge_target = Vector2(self.base_pos[0] -
                                                        (self.run_speed * 2 * sin(radians(self.leader.angle))),
                                                        self.base_pos[1] -
                                                        (self.run_speed * 2 * cos(radians(self.leader.angle))))
                        if charge_target and charge_target.distance_to(self.base_pos):
                            self.command_target = charge_target
                            if self.charge_target:
                                if "charge" in self.current_action or "charge" in self.command_action:
                                    if "charge" in self.current_action:
                                        self.command_action = self.charge_command_action[self.current_action["weapon"]]
                                else:  # manual charge interrupt by anything, reset target
                                    self.charge_target = None
                            else:
                                attack_index = self.leader.current_action["weapon"]  # use same weapon side as leader
                                if not self.melee_range[attack_index]:  # weapon not melee one
                                    if attack_index == 0:
                                        attack_index = 1
                                    else:
                                        attack_index = 0
                                self.command_action = self.charge_command_action[attack_index]

        elif "charge" in self.current_action and self.ai_charge_timer:  # follower charging but leader no longer doing it
            # keep charging until timer run out
            self.ai_charge_timer -= dt
            if self.ai_charge_timer < 0:
                self.ai_charge_timer = 0
            else:
                self.command_target = Vector2(self.base_pos[0] - (self.run_speed * 2 * sin(radians(self.angle))),
                                              self.base_pos[1] - (self.run_speed * 2 * cos(radians(self.angle))))
                self.command_action = self.charge_command_action[self.current_action["weapon"]]

        elif not self.command_action and move_distance > follow:
            # too far from follow target pos, start moving toward it
            self.command_target = move_target
            if 0 < move_distance < 20:  # walk if not too far
                self.command_action = self.walk_command_action
            else:  # run if too far
                if move_distance > 50:
                    self.leader.group_too_far = True
                    if self.is_leader:
                        self.leader.army_too_far = True
                if move_distance > 100 and self.available_move_far_skill and not self.command_action:
                    # use move far skill first if leader
                    self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                elif self.available_move_skill and not self.command_action:  # use move skill
                    self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                else:  # no skill to use or can use, now move
                    self.command_action = self.run_command_action

        elif self.melee_target and self.max_melee_range and not self.manual_control:
            # move to enemy nearby when follow_target not too far, only for melee
            move_melee_range = self.max_melee_range - 1  # using max_melee_range only seem to make unit stand too far
            move_distance = self.melee_target.base_pos.distance_to(self.base_pos) - move_melee_range
            if move_distance < follow or self.impetuous:
                # enemy not too far from move_target
                if move_distance > move_melee_range:  # move closer to enemy in range
                    # move to front of near target
                    if move_distance > 100 and self.is_leader and self.available_move_far_skill and not self.command_action:  # use move far skill first if leader
                        self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                    elif self.available_move_skill and not self.command_action:  # use move skill
                        self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                    else:
                        self.command_action = self.run_command_action

                        # move enough to be in melee attack range
                        base_angle = self.set_rotate(self.melee_target.base_pos)
                        self.command_target = Vector2(self.base_pos[0] - (move_distance * sin(radians(base_angle))),
                                                      self.base_pos[1] - (move_distance * cos(radians(base_angle))))

    else:  # free order or unit is army leader, move to attack nearby enemy
        if self.nearest_enemy:
            if self.is_leader and ("range" in self.group_type or not self.group_too_far):
                # group/army leader of ranged troops go to position from ai_leader
                if move_distance > 150:  # distance too far or group/army too far behind, walk first
                    self.command_action = self.walk_command_action
                    self.command_target = move_target
                elif move_distance:  # short distance to move, run
                    self.command_action = self.run_command_action
                    self.command_target = move_target

            elif self.is_leader and self.group_too_far and move_distance > self.charge_melee_range and \
                    self.group_follow_order in ("Stay Formation", "Follow") and not self.melee_target:
                # troop followers too far, stand to wait a bit for them to catch up
                self.command_action = self.walk_command_action
                self.command_target = move_target

            elif not self.melee_target:  # no enemy to hit yet
                if self.max_shoot_range:  # has range weapon, move to maximum shoot range position
                    move_distance = self.nearest_enemy[0].base_pos.distance_to(self.front_pos)
                    max_shoot = self.max_shoot_range
                    if self.leader and self in self.leader.troop_distance_list:  # possible that unit not in list yet from recent change of leader
                        # use distance of formation to make unit not cluster at same distance
                        max_shoot -= self.leader.troop_distance_list[self][1]
                    if move_distance > max_shoot:  # further than can shoot
                        move_distance -= max_shoot
                        if move_distance > 100 and self.is_leader and self.available_move_far_skill and not self.command_action:  # use move far skill first if leader
                            self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                        elif self.available_move_skill and not self.command_action:  # use move skill first
                            self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                        else:
                            angle = self.set_rotate(self.nearest_enemy[0].base_pos)
                            self.command_action = self.run_command_action
                            self.command_target = Vector2(self.base_pos[0] - (move_distance * sin(radians(angle))),
                                                          self.base_pos[1] - (move_distance * cos(radians(angle))))

                else:  # no range weapon, move to melee attack nearest enemy
                    move_melee_range = self.max_melee_range - 1  # using max_melee_range only seem to make unit stand too far
                    move_distance = self.nearest_enemy[0].base_pos.distance_to(self.base_pos) - move_melee_range
                    if move_distance > move_melee_range:  # too far move closer
                        if move_distance > 100 and self.is_leader and self.available_move_far_skill and not self.command_action:
                            # use move far skill first if leader
                            self.skill_command_input(0, self.available_move_far_skill, pos_target=self.base_pos)
                        elif self.available_move_skill and not self.command_action:  # use move skill first
                            self.skill_command_input(0, self.available_move_skill, pos_target=self.base_pos)
                        else:
                            if move_distance > self.charge_melee_range:
                                if move_distance > 200:
                                    self.command_action = self.walk_command_action
                                else:
                                    self.command_action = self.run_command_action
                            else:
                                if move_distance > self.melee_range[0] > 0:
                                    self.command_action = self.charge_command_action[0]
                                else:
                                    self.command_action = self.charge_command_action[1]

                            base_angle = self.set_rotate(self.nearest_enemy[0].base_pos)
                            self.command_target = Vector2(self.base_pos[0] - (move_distance * sin(radians(base_angle))),
                                                          self.base_pos[1] - (move_distance * cos(radians(base_angle))))

            else:  # has nearby enemy to hit in melee combat
                move_distance = self.melee_target.base_pos.distance_to(self.base_pos) - self.max_melee_range
                if move_distance > self.max_melee_range:  # too far move closer to hit enemy
                    if move_distance > 10:
                        if not self.command_action:
                            self.command_action = self.run_command_action
                    else:
                        if not self.command_action:  # walk if not that far
                            self.command_action = self.walk_command_action
                    base_angle = self.set_rotate(self.melee_target.base_pos)
                    self.command_target = Vector2(self.base_pos[0] - (move_distance * sin(radians(base_angle))),
                                                  self.base_pos[1] - (move_distance * cos(radians(base_angle))))

    if not self.current_action and not self.command_action and self.available_idle_skill:  # idle, use idle skill
        self.skill_command_input(0, self.available_idle_skill, pos_target=self.base_pos)
