def skill_command_input(self, skill_index, available_list, pos_target=None):
    self.command_action = {"skill": available_list[skill_index]}
    if pos_target:
        self.command_action["pos"] = pos_target
    available_list.pop(skill_index)
