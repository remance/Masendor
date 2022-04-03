import pygame


def user_input(self, mouse_pos, mouse_left_up, mouse_right_up, double_mouse_right, target, key_state, other_command=0):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.state != 100:
        self.rotate_only = False
        self.forced_melee = False
        self.attack_place = False
        self.range_combat_check = False
        # register user keyboard
        leader_subunit = self.leader[0].subunit
        new_pos = pygame.Vector2(leader_subunit.base_pos)
        leader_subunit.new_angle = leader_subunit.set_rotate(mouse_pos)
        if key_state[pygame.K_s]:  # move down
            new_pos[1] += self.run_speed

        elif key_state[pygame.K_w]:  # move up
            new_pos[1] -= self.run_speed

        if key_state[pygame.K_a]:  # move left
            new_pos[0] -= self.run_speed

        elif key_state[pygame.K_d]:  # move right
            new_pos[0] += self.run_speed

        # if new_pos != self.leader[0].subunit.base_pos:
        #     print(new_pos, self.leader[0].subunit.base_pos)
        self.process_command(new_pos, key_state[pygame.K_LSHIFT])
        # self.attack_place = True

        # if mouse_right_up and 1 <= pos[0] < 998 and 1 <= pos[1] < 998:
        #     for subunit in self.subunits:
        #         subunit.attacking = True
        #     # if self.state == 10:
        #     if key_state is not None and (key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]):
        #         self.rotate_only = True
        #     if key_state is not None and key_state[pygame.K_z]:
        #         self.revert = True

        # self.process_command(pos, double_mouse_right, self.revert, target, other_command)
