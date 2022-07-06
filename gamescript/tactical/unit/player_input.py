import pygame


def player_input(self, cursor_pos, mouse_left_up=False, mouse_right_up=False, mouse_left_down=False,
                 mouse_right_down=False, double_mouse_right=False, target=None, key_state=None,
                 other_command=None):
    """other_command is special type of command such as stop all action, raise flag, decimation, duel and so on"""
    if self.player_control and self.state not in (95, 97, 98, 99, 100):
        self.revert = False
        self.retreat_start = False  # reset retreat
        self.rotate_only = False
        self.forced_melee = False
        self.attack_target = None
        self.base_attack_pos = 0
        self.attack_place = False

        # register user keyboard
        if mouse_right_up and 1 <= cursor_pos[0] < 998 and 1 <= cursor_pos[1] < 998:
            if self.state in (10, 96) and target is None:
                self.process_retreat(cursor_pos)  # retreat
            else:
                for subunit in self.subunit_list:
                    subunit.attacking = True
                # if self.state == 10:
                if key_state is not None:
                    if key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]:
                        self.rotate_only = True
                    if key_state[pygame.K_z]:
                        self.revert = True
                    if key_state[pygame.K_LCTRL] or key_state[pygame.K_RCTRL]:
                        self.forced_melee = True
                    if key_state[pygame.K_LALT] or key_state[pygame.K_RALT]:
                        self.attack_place = True
                self.issue_order(cursor_pos, double_mouse_right, self.revert, target)
        elif other_command is not None:
            self.issue_order(cursor_pos, double_mouse_right, self.revert, target, other_command)
