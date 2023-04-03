import pygame


def player_input(self, cursor_pos, mouse_left_up=False, mouse_right_up=False, mouse_left_down=False,
                 mouse_right_down=False, key_state=None):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.alive:
        new_pos = pygame.Vector2(self.base_pos)
        if not self.current_action or "hold" in self.current_action:  # can rotate if not has any action or holding
            self.new_angle = self.set_rotate(cursor_pos)
        if "uncontrollable" not in self.current_action and "uncontrollable" not in self.command_action:
            if key_state:
                if self.battle.player_char_input_delay == 0 and not self.current_action:  # for input that need to have time delay to work properly
                    if key_state[pygame.K_1] and self.equipped_weapon != 0:  # Swap to primary weapon
                        self.swap_weapon(0)
                        self.battle.player_char_input_delay = 1
                    elif key_state[pygame.K_2] and self.equipped_weapon != 1:  # Swap to secondary weapon
                        self.swap_weapon(1)
                        self.battle.player_char_input_delay = 1
                    elif key_state[pygame.K_q]:  # Use input skill 1
                        self.command_action = self.skill_command_action_0
                        self.battle.player_char_input_delay = 1
                    elif key_state[pygame.K_e]:  # Use input skill 2
                        self.command_action = self.skill_command_action_1
                        self.battle.player_char_input_delay = 1
                    elif key_state[pygame.K_r]:  # Use input skill 3
                        self.command_action = self.skill_command_action_2
                        self.battle.player_char_input_delay = 1
                    elif key_state[pygame.K_t]:  # Use input skill 4
                        self.command_action = self.skill_command_action_3
                        self.battle.player_char_input_delay = 1

                if not self.current_action or "movable" in self.current_action:
                    speed = self.walk_speed
                    if key_state[pygame.K_LSHIFT]:
                        speed = self.run_speed

                    if key_state[pygame.K_s]:  # move down
                        new_pos[1] += speed

                    elif key_state[pygame.K_w]:  # move up
                        new_pos[1] -= speed

                    if key_state[pygame.K_a]:  # move left
                        new_pos[0] -= speed

                    elif key_state[pygame.K_d]:  # move right
                        new_pos[0] += speed

                    if new_pos != self.base_pos:
                        if not self.current_action:
                            self.command_action = self.walk_command_action
                            if key_state[pygame.K_LSHIFT]:
                                self.command_action = self.run_command_action
                            self.move_speed = speed
                        elif "movable" in self.current_action and "weapon" not in self.current_action:
                            # Already walking or running but not attacking, replace current action with new one
                            if key_state[pygame.K_LSHIFT]:
                                if "walk" in self.current_action:  # change to run animation
                                    self.interrupt_animation = True
                                self.current_action = self.run_command_action
                            else:
                                if "run" in self.current_action:
                                    self.interrupt_animation = True
                                self.current_action = self.walk_command_action
                            self.move_speed = speed
                        elif "hold" in self.current_action:  # cancel hold animation by moving
                            self.interrupt_animation = True

                    self.command_target = new_pos

            if not self.move_speed:  # attack while stationary
                if mouse_left_up or mouse_right_up:
                    action_num = 0
                    if mouse_right_up:
                        action_num = 1
                    if "hold" in self.current_action:  # release holding
                        self.release_timer = self.hold_timer
                        if "melee attack" in self.current_action:
                            self.current_action = self.melee_attack_command_action[action_num]
                        elif "range attack" in self.current_action:
                            self.current_action = self.range_attack_command_action[action_num]

                elif mouse_left_down or mouse_right_down:
                    action_num = 0
                    str_action_num = "0"
                    if mouse_right_down:
                        action_num = 1
                        str_action_num = "1"
                    if not self.current_action:  # no current action
                        if self.equipped_weapon in self.ammo_now and \
                                action_num in self.ammo_now[self.equipped_weapon]:  # range attack
                            if self.ammo_now[self.equipped_weapon][action_num] > 0:
                                self.command_action = self.range_attack_command_action[action_num]
                                self.attack_pos = cursor_pos
                        elif self.weapon_cooldown[action_num] >= self.weapon_speed[action_num]:  # melee attack
                            self.command_action = self.melee_attack_command_action[action_num]
                            self.attack_pos = cursor_pos

                    elif "Action " + str_action_num in self.current_action["name"] and \
                            "movable" not in self.current_action:  # already attacking
                        self.attack_pos = cursor_pos
                        if "hold" not in self.current_action:  # start holding
                            if "melee attack" in self.current_action:
                                self.current_action = self.melee_hold_command_action[action_num]
                            elif "range attack" in self.current_action:
                                self.current_action = self.range_hold_command_action[action_num]

            else:  # attack while moving
                if mouse_left_up or mouse_right_up:  # perform attack
                    action_num = 0
                    if mouse_right_up:
                        action_num = 1

                    if "hold" in self.current_action:  # release holding
                        self.release_timer = self.hold_timer
                        if "melee attack" in self.current_action:
                            self.current_action = self.melee_attack_command_action[action_num]
                        elif "range attack" in self.current_action:
                            self.current_action = self.range_attack_command_action[action_num]

                    elif "charge" in self.current_action:
                        self.interrupt_animation = True
                        self.command_action = self.melee_attack_command_action[action_num]
                        self.attack_pos = cursor_pos

                    elif "range attack" in self.current_action:  # update new range attack pos
                        self.attack_pos = cursor_pos

                elif mouse_left_down or mouse_right_down:
                    action_num = 0
                    str_action_num = "0"
                    if mouse_right_down:
                        action_num = 1
                        str_action_num = "1"
                    if self.equipped_weapon in self.ammo_now and \
                            action_num in self.ammo_now[self.equipped_weapon]:  # range weapon
                        if self.ammo_now[self.equipped_weapon][action_num] > 0 and \
                                self.shoot_while_moving and \
                                not self.check_special_effect("Stationary", weapon=action_num):
                            if "range attack" not in self.current_action:  # start move shooting
                                self.interrupt_animation = True
                                if "walk" in self.current_action:
                                    self.command_action = self.range_walk_command_action[action_num]
                                elif "run" in self.current_action:
                                    self.command_action = self.range_run_command_action[action_num]
                                self.attack_pos = cursor_pos
                                self.move_speed = speed
                            else:  # already move shooting, update pos
                                self.attack_pos = cursor_pos
                    elif key_state[pygame.K_LSHIFT]:  # melee weapon charge
                        if "charge" not in self.current_action:  # start charge animation
                            self.interrupt_animation = True
                            self.command_action = self.charge_command_action[action_num]
                            self.move_speed = self.run_speed

                    elif self.current_action and "Action " + str_action_num in self.current_action[
                        "name"]:  # No new attack command if already doing it
                        if "hold" not in self.current_action:  # start holding
                            if "melee attack" in self.current_action:
                                self.current_action = self.melee_hold_command_action[action_num]
                            elif "range attack" in self.current_action:
                                self.current_action = self.range_hold_command_action[action_num]
                        else:  # holding, update new attack pos
                            self.attack_pos = cursor_pos

                    else:  # normal melee attack
                        self.interrupt_animation = True
                        self.command_action = self.melee_attack_command_action[action_num]
                        self.attack_pos = cursor_pos
