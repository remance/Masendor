def leader_command_ui_mouse_over(self, mouse_right):
    """process user mouse input on leader portrait in command ui"""
    leader_mouse_over = False
    for this_leader in self.leader_now:
        if this_leader.rect.collidepoint(self.mouse_pos):
            if this_leader.unit.commander:
                army_position = self.leader_level[this_leader.role]
            else:
                army_position = self.leader_level[this_leader.role + 4]

            self.single_text_popup.pop(self.mouse_pos,
                                       army_position + ": " + this_leader.name)  # popup leader name when mouse over
            self.battle_ui_updater.add(self.single_text_popup)
            leader_mouse_over = True

            if mouse_right and this_leader.leader_id != 0:
                self.popout_lorebook(self.main.encyclopedia.leader_section, this_leader.leader_id)
            break
    return leader_mouse_over
