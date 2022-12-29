import pygame

weapon_set = ("Main_", "Sub_")

leader_weapon_skill_command_action_0 = {"name": "Leader Weapon Skill 0"}
leader_weapon_skill_command_action_1 = {"name": "Leader Weapon Skill 1"}


def player_input(self, cursor_pos, mouse_left_up=False, mouse_right_up=False, mouse_left_down=False,
                 mouse_right_down=False, double_mouse_right=False, target=None, key_state=None):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.state not in (99, 100):
        self.rotate_only = False
        self.forced_melee = False
        self.attack_place = False

        new_pos = pygame.Vector2(self.leader_subunit.base_pos)
        if not self.leader_subunit.current_action or "hold" in self.leader_subunit.current_action:  # can rotate if not has any action or holding
            self.leader_subunit.new_angle = self.leader_subunit.set_rotate(cursor_pos)

        if key_state is not None:
            if self.input_delay == 0:  # for input that need to have time delay to work properly
                if key_state[pygame.K_DOWN]:
                    self.reposition_leader("down")
                elif key_state[pygame.K_UP]:
                    self.reposition_leader("up")
                elif key_state[pygame.K_LEFT]:
                    self.reposition_leader("left")
                elif key_state[pygame.K_RIGHT]:
                    self.reposition_leader("right")
                elif key_state[pygame.K_1]:  # Use troop weapon skill 1
                    self.issue_order(cursor_pos, other_command="Troop Weapon Skill 0")
                elif key_state[pygame.K_2]:  # Use troop weapon skill 2
                    self.issue_order(cursor_pos, other_command="Troop Weapon Skill 1")
                elif key_state[pygame.K_e]:  # Use leader weapon skill 1
                    self.leader_subunit.command_action = leader_weapon_skill_command_action_0
                elif key_state[pygame.K_r]:  # Use leader weapon skill 2
                    self.leader_subunit.command_action = leader_weapon_skill_command_action_1

            speed = self.walk_speed / 10
            if key_state[pygame.K_LSHIFT]:
                speed = self.run_speed / 10
            if key_state[pygame.K_SPACE]:
                self.rotate_only = True

            if key_state[pygame.K_s]:  # move down
                new_pos[1] += speed

            elif key_state[pygame.K_w]:  # move up
                new_pos[1] -= speed

            if key_state[pygame.K_a]:  # move left
                new_pos[0] -= speed

            elif key_state[pygame.K_d]:  # move right
                new_pos[0] += speed

        if self.rotate_only:
            self.issue_order(cursor_pos, run_command=key_state[pygame.K_LSHIFT])

        elif new_pos == self.leader_subunit.base_pos:
            if "uninterruptible" not in self.leader_subunit.command_action:
                if mouse_left_down or mouse_right_down:
                    action_num = 0
                    str_action_num = "0"
                    if mouse_right_down:
                        action_num = 1
                        str_action_num = "1"
                    if not self.leader_subunit.current_action:  # no current action
                        if self.leader_subunit.equipped_weapon in self.leader_subunit.ammo_now and \
                                action_num in self.leader_subunit.ammo_now[
                            self.leader_subunit.equipped_weapon]:  # range attack
                            if self.leader_subunit.ammo_now[self.leader_subunit.equipped_weapon][action_num] > 0:
                                self.leader_subunit.command_action = {"name": "Action " + str_action_num,
                                                                      "range attack": True, "pos": cursor_pos}
                        else:  # melee attack
                            self.leader_subunit.command_action = {"name": "Action " + str_action_num,
                                                                  "melee attack": True}
                    elif "Action " + str_action_num in self.leader_subunit.current_action[
                        "name"]:  # No new attack command if already doing it
                        if "hold" not in self.leader_subunit.current_action:  # start holding
                            self.leader_subunit.current_action["hold"] = True
                        else:  # holding
                            if "range attack" in self.leader_subunit.current_action:  # update new attack pos
                                self.leader_subunit.current_action["pos"] = cursor_pos

                elif mouse_left_up or mouse_right_up:
                    if "hold" in self.leader_subunit.current_action:  # release holding
                        self.leader_subunit.current_action.pop("hold")

        elif "uninterruptible" not in self.leader_subunit.command_action:
            move = False
            self.leader_subunit.new_angle = self.leader_subunit.set_rotate(new_pos)
            if mouse_left_down or mouse_right_down:
                action_num = 0
                str_action_num = "0"
                if mouse_right_down:
                    action_num = 1
                    str_action_num = "1"
                if self.leader_subunit.equipped_weapon in self.leader_subunit.ammo_now and \
                        action_num in self.leader_subunit.ammo_now[self.leader_subunit.equipped_weapon] and \
                        self.leader_subunit.check_special_effect("Shoot While Moving"):  # range weapon
                    if "range attack" not in self.leader_subunit.current_action:
                        self.leader_subunit.command_action = {"name": "Action " + str_action_num, "range attack": True,
                                                              "pos": cursor_pos, "move attack": True, "movable": True}
                        self.issue_order(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True)
                    elif "move attack" not in self.leader_subunit.current_action:
                        if "hold" in self.leader_subunit.current_action:  # cannot hold shoot while moving
                            self.leader_subunit.current_action.pop("hold")
                        self.leader_subunit.current_action["movable"] = True
                        self.leader_subunit.current_action["move attack"] = True
                        self.leader_subunit.current_action["pos"] = cursor_pos
                        self.issue_order(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True)
                    else:
                        self.leader_subunit.current_action["pos"] = cursor_pos
                        self.issue_order(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True)
                    move = True
                elif key_state[pygame.K_LSHIFT]:  # melee weapon charge
                    self.issue_order(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True,
                                     other_command="Charge Skill " + str_action_num)
                    move = True

            elif mouse_left_up or mouse_right_up:
                action_num = 0
                str_action_num = "0"
                if mouse_right_up:
                    action_num = 1
                    str_action_num = "1"

                if self.leader_subunit.current_action and weapon_set[action_num] in self.leader_subunit.current_action[
                    "name"]:  # perform attack when release charge
                    if "_Charge" in self.leader_subunit.current_action["name"]:
                        self.issue_order(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True,
                                         other_command="Action " + str_action_num)
                    elif "range attack" in self.leader_subunit.current_action:  # update new range attack pos
                        self.leader_subunit.current_action["pos"] = cursor_pos
                        move = True

            else:
                self.issue_order(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True)
                move = True
            if move:
                self.leader_subunit.command_target = new_pos

        # else:  # no new movement register other command
