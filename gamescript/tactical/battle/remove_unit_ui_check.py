def remove_unit_ui_check(self, mouse_left_up):
    """Remove the unit ui when click at empty space"""
    if mouse_left_up and self.current_selected is not None and self.click_any is False:  # not click at any unit while has selected unit
        self.current_selected = None  # reset last_selected
        self.before_selected = None  # reset before selected unit after remove last selected
        self.remove_unit_ui()
        if self.game_state == "editor" and self.slot_display_button.event == 0:  # add back ui again for when unit editor ui displayed
            self.battle_ui_updater.add(self.unit_editor_stuff, self.leader_now)
