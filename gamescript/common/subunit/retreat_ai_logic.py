def retreat_ai_logic(self):
    if "move loop" in self.current_action:
        self.interrupt_animation = True
    self.command_action = self.flee_command_action
    self.move_speed = self.run_speed
