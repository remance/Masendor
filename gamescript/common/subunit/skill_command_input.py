def skill_command_input(self, skill_index, available_list):
    self.command_action = {"skill": available_list[skill_index]}
    available_list.pop(skill_index)
