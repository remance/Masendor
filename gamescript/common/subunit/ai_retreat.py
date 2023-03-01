def ai_retreat(self):
    if "movable" in self.current_action and "flee" not in self.current_action and \
            "uninterruptible" not in self.current_action:
        self.interrupt_animation = True
    if not self.command_action:
        self.command_action = self.flee_command_action
        self.move_speed = self.run_speed
