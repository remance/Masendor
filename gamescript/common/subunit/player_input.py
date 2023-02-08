import pygame


def player_input(self, cursor_pos, mouse_left_up=False, mouse_right_up=False, mouse_left_down=False,
                 mouse_right_down=False, double_mouse_right=False, target=None, key_state=None):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.alive:
        new_pos = pygame.Vector2(self.base_pos)
        if not self.current_action or "hold" in self.current_action:  # can rotate if not has any action or holding
            self.new_angle = self.set_rotate(cursor_pos)

        if "uncontrollable" not in self.current_action:
            if key_state is not None:
                if self.battle.player_char_input_delay == 0 and not self.current_action:  # for input that need to have time delay to work properly
                    if key_state[pygame.K_1]:  # Swap to primary weapon
                        self.swap_weapon(0)
                    elif key_state[pygame.K_2]:  # Swap to secondary weapon
                        self.swap_weapon(1)
                    # elif key_state[pygame.K_1]:  # Use troop weapon skill 1
                    #     self.issue_order(cursor_pos, other_command="Troop Weapon Skill 0")
                    # elif key_state[pygame.K_2]:  # Use troop weapon skill 2
                    #     self.issue_order(cursor_pos, other_command="Troop Weapon Skill 1")
                    if key_state[pygame.K_e]:  # Use leader weapon skill 1
                        self.command_action = self.weapon_skill_command_action_0
                    elif key_state[pygame.K_r]:  # Use leader weapon skill 2
                        self.command_action = self.weapon_skill_command_action_1

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

                self.command_target = new_pos
                if new_pos != self.base_pos:
                    self.command_action = self.walk_command_action.copy()
                    if key_state[pygame.K_LSHIFT]:
                        self.command_action = self.run_command_action.copy()
                    self.command_action["move speed"] = speed

            if new_pos == self.base_pos:  # attack while stationary
                if "uncontrollable" not in self.current_action and "uncontrollable" not in self.command_action:
                    if mouse_left_down or mouse_right_down:
                        action_num = 0
                        str_action_num = "0"
                        if mouse_right_down:
                            action_num = 1
                            str_action_num = "1"
                        if not self.current_action:  # no current action
                            if self.equipped_weapon in self.ammo_now and \
                                    action_num in self.ammo_now[self.equipped_weapon]:  # range attack
                                if self.ammo_now[self.equipped_weapon][action_num] > 0:
                                    self.command_action = self.range_attack_command_action[action_num].copy()
                                    self.command_action["pos"] = cursor_pos
                            else:  # melee attack
                                self.command_action = self.melee_attack_command_action[action_num].copy()
                                self.command_action["pos"] = cursor_pos

                        elif "Action " + str_action_num in self.current_action["name"]:  # already attacking
                            self.current_action["pos"] = cursor_pos
                            if "hold" not in self.current_action:  # start holding
                                self.current_action["hold"] = True

                    elif mouse_left_up or mouse_right_up:
                        if "hold" in self.current_action:  # release holding
                            self.current_action.pop("hold")

            elif "uncontrollable" not in self.current_action and "uncontrollable" not in self.command_action:  # attack while moving
                self.new_angle = self.set_rotate(new_pos)
                if mouse_left_down or mouse_right_down:
                    action_num = 0
                    str_action_num = "0"
                    if mouse_right_down:
                        action_num = 1
                        str_action_num = "1"
                    if self.equipped_weapon in self.ammo_now and \
                            action_num in self.ammo_now[self.equipped_weapon] and \
                            self.check_special_effect("Shoot While Moving"):  # range weapon
                        if self.ammo_now[self.equipped_weapon][action_num] > 0:
                            if "range attack" not in self.current_action:
                                self.command_action = self.move_shoot_command_action[action_num].copy()
                                self.command_action["pos"] = cursor_pos
                                self.command_action["move speed"] = speed
                            elif "move attack" not in self.current_action:
                                if "hold" in self.current_action:  # cannot hold shoot while moving
                                    self.current_action.pop("hold")
                                self.current_action["movable"] = True
                                self.current_action["move attack"] = True
                                self.current_action["pos"] = cursor_pos
                            else:
                                self.current_action["pos"] = cursor_pos
                    elif key_state[pygame.K_LSHIFT]:  # melee weapon charge
                        if "uncontrollable" not in self.command_action:
                            self.state = 4
                            self.command_action = self.charge_command_action
                            self.command_action["move speed"] = speed

                    elif not self.current_action:  # normal melee attack
                        self.command_action = self.melee_attack_command_action[action_num].copy()
                        self.command_action["pos"] = cursor_pos

                    elif "Action " + str_action_num in self.current_action[
                        "name"]:  # No new attack command if already doing it
                        if "hold" not in self.current_action:  # start holding
                            self.current_action["hold"] = True
                        else:  # holding, update new attack pos
                            self.current_action["pos"] = cursor_pos

                elif mouse_left_up or mouse_right_up:
                    action_num = 0
                    str_action_num = "0"
                    if mouse_right_up:
                        action_num = 1
                        str_action_num = "1"

                    if "hold" in self.current_action and \
                            "Action " + str_action_num in self.current_action["name"]:  # release holding
                        self.current_action.pop("hold")

                    if self.current_action and str_action_num in self.current_action[
                        "name"]:  # perform attack when release charge
                        if "_Charge" in self.current_action["name"]:
                            self.command_action = self.melee_attack_command_action[action_num].copy()
                            self.command_action["pos"] = cursor_pos
                        elif "range attack" in self.current_action:  # update new range attack pos
                            self.current_action["pos"] = cursor_pos
