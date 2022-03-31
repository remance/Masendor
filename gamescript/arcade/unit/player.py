import pygame


def user_input(self, pos, mouse_left_up, mouse_right_up, double_mouse_right, target, key_state, other_command=0):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.state not in (95, 97, 98, 99):
        self.rotate_only = False
        self.forced_melee = False
        self.attack_place = False
        self.range_combat_check = False

        # register user keyboard
        if key_state is not None:
            new_pos = self.leader[0].subunit.base_pos
            if key_state[pygame.K_s]:  # move down
                new_pos[1] += self.run_speed

            elif key_state[pygame.K_w]:  # move up
                new_pos[1] -= self.run_speed

            if key_state[pygame.K_a]:  # move left
                new_pos[0] -= self.run_speed

            elif key_state[pygame.K_d]:  # move right
                new_pos[0] += self.run_speed

            if new_pos != self.leader[0].subunit.base_pos:
                self.process_command(pos, True)
            self.attack_place = True

        if mouse_right_up and 1 <= pos[0] < 998 and 1 <= pos[1] < 998:
            for subunit in self.subunits:
                subunit.attacking = True
            # if self.state == 10:
            if key_state is not None and (key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]):
                self.rotate_only = True
            if key_state is not None and key_state[pygame.K_z]:
                self.revert = True
            self.process_command(pos, double_mouse_right, self.revert, target)
        elif other_command != 0:
            self.process_command(pos, double_mouse_right, self.revert, target, other_command)
