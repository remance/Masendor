def leader_command_ui_mouse_over(self, mouse_right):  # TODO make it so button and leader popup not show at same time
    """process user mouse input on leader portrait in command ui"""
    leader_mouse_over = False
    for this_leader in self.leader_now:
        if this_leader.rect.collidepoint(self.mouse_pos):
            if this_leader.unit.commander:
                army_position = self.leader_level[this_leader.role]
            else:
                army_position = self.leader_level[this_leader.role + 4]

            self.leader_popup.pop(self.mouse_pos, army_position + ": " + this_leader.name)  # popup leader name when mouse over
            self.battle_ui_updater.add(self.leader_popup)
            leader_mouse_over = True

            if mouse_right:
                self.popout_lorebook(8, this_leader.leader_id)
            break
    return leader_mouse_over
