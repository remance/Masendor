import pygame


def unit_icon_mouse_over(self, mouse_up, mouse_right):
    """
    process user mouse input on unit icon
    :param self: battle object
    :param mouse_up: left click for select unit
    :param mouse_right: right click for go to unit position on map
    :return:
    """
    self.click_any = True
    if self.game_state == "battle" or (
            self.game_state == "editor" and self.subunit_build not in self.battle_ui_updater):
        for icon in self.unit_icon:
            if icon.rect.collidepoint(self.mouse_pos):
                if mouse_up:
                    self.current_selected = icon.unit
                    self.current_selected.just_selected = True
                    self.current_selected.selected = True

                    if self.before_selected is None:  # add back the pop up ui, so it gets shown when click subunit with none selected before
                        self.battle_ui_updater.add(self.unitstat_ui, self.command_ui)  # add leader and top ui
                        self.battle_ui_updater.add(self.inspect_button)  # add inspection ui open/close button

                        self.add_behaviour_ui(self.current_selected)

                elif mouse_right:
                    self.base_camera_pos = pygame.Vector2(icon.unit.base_pos[0] * self.screen_scale[0],
                                                          icon.unit.base_pos[1] * self.screen_scale[1])
                    self.camera_pos = self.base_camera_pos * self.camera_zoom
                break
    return self.click_any
