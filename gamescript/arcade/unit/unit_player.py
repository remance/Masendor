import pygame


def user_input(self, cursor_pos, mouse_left_up, mouse_right_up, double_mouse_right, target, key_state, other_command=None):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.state not in (99, 100):
        self.rotate_only = False
        self.forced_melee = False
        self.attack_place = False
        self.range_combat_check = False

        new_pos = pygame.Vector2(self.leader_subunit.base_pos)
        self.leader_subunit.new_angle = self.leader_subunit.set_rotate(cursor_pos)
        if key_state is not None:
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
        #     # if self.state == 10:
        #     if key_state is not None and (key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]):
        #         self.rotate_only = True
        #     if key_state is not None and key_state[pygame.K_z]:
        #         self.revert = True

        # self.process_command(pos, double_mouse_right, self.revert, target, other_command)
