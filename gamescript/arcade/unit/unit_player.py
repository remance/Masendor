import pygame


def player_input(self, cursor_pos, mouse_left_up, mouse_right_up, double_mouse_right, target, key_state, other_command=None):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.state not in (99, 100):
        self.rotate_only = False
        self.forced_melee = False
        self.attack_place = False
        self.range_combat_check = False

        if self.leader_subunit.current_action is None:
            new_pos = pygame.Vector2(self.leader_subunit.base_pos)
            self.leader_subunit.new_angle = self.leader_subunit.set_rotate(cursor_pos)
            if mouse_left_up:
                self.leader_subunit.current_action = "action 1"
            elif mouse_right_up:
                self.leader_subunit.current_action = "action 2"

            elif key_state is not None:
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

                if new_pos != self.leader_subunit.base_pos:
                    self.leader_subunit.base_target = new_pos
                    self.leader_subunit.new_angle = self.leader_subunit.set_rotate(new_pos)
                    self.process_command(new_pos, run_command=key_state[pygame.K_LSHIFT], revert_move=True)
                elif self.rotate_only:
                    self.process_command(cursor_pos, run_command=key_state[pygame.K_LSHIFT])
                # elif key_state[pygame.K_q]:  # Use leader skill 1
                #     self.leader_subunit.current_action = "leader skill 1"
                # elif key_state[pygame.K_e]:  # Use leader skill 2
                #     self.leader_subunit.current_action = "leader skill 2"
                # elif key_state[pygame.K_1]:  # Use troop skill 1
                #     self.leader_subunit.current_action = "troop skill 1"
                # elif key_state[pygame.K_2]:  # Use troop skill 2
                #     self.leader_subunit.current_action = "troop skill 2"

