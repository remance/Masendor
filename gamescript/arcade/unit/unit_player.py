import pygame


def player_input(self, cursor_pos, mouse_left_up, mouse_right_up, mouse_left_down, mouse_right_down,
                 double_mouse_right, target, key_state,  *args):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.state not in (99, 100):
        self.rotate_only = False
        self.forced_melee = False
        self.attack_place = False
        self.range_combat_check = False

        new_pos = pygame.Vector2(self.leader_subunit.base_pos)
        self.leader_subunit.new_angle = self.leader_subunit.set_rotate(cursor_pos)

        if key_state is not None:
            if self.input_delay == 0:  # for input that need to have time delay to work properly
                if key_state[pygame.K_DOWN]:
                    self.move_leader("down")
                elif key_state[pygame.K_UP]:
                    self.move_leader("up")
                elif key_state[pygame.K_LEFT]:
                    self.move_leader("left")
                elif key_state[pygame.K_RIGHT]:
                    self.move_leader("right")
                elif key_state[pygame.K_1]:  # Use troop weapon skill 1
                    self.process_command(cursor_pos, other_command="Troop Weapon Skill 0")
                elif key_state[pygame.K_2]:  # Use troop weapon skill 2
                    self.process_command(cursor_pos, other_command="Troop Weapon Skill 1")
                elif key_state[pygame.K_3]:  # Use troop skill 1
                    self.process_command(cursor_pos, other_command="Troop Skill 0")
                elif key_state[pygame.K_4]:  # Use troop skill 2
                    self.process_command(cursor_pos, other_command="Troop Skill 1")

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

            elif key_state[pygame.K_q]:  # Use leader skill 1
                self.leader_subunit.command_action = ("Leader skill 0", )
            elif key_state[pygame.K_e]:  # Use leader skill 2
                self.leader_subunit.command_action = ("Leader skill 1", )

        if new_pos != self.leader_subunit.base_pos:
            self.leader_subunit.base_target = new_pos
            self.leader_subunit.new_angle = self.leader_subunit.set_rotate(new_pos)
            if mouse_left_down and key_state[pygame.K_LSHIFT]:
                self.process_command(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True,
                                     other_command="Charge Skill 0")
            elif mouse_right_down and key_state[pygame.K_LSHIFT]:
                self.process_command(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True,
                                     other_command="Charge Skill 1")
            else:
                self.process_command(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True)
        elif self.rotate_only:
            self.process_command(cursor_pos, run_command=key_state[pygame.K_LSHIFT])
        else:  # no new movement register other
            if mouse_left_up or mouse_left_down:
                self.leader_subunit.command_action = ("Action 0", )
            elif mouse_right_up or mouse_right_down:
                self.leader_subunit.command_action = ("Action 1", )
