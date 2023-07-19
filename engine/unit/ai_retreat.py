def ai_retreat(self):
    if "hold" in self.current_action:  # stop any hold animation
        self.interrupt_animation = True
    self.command_action = self.flee_command_action
