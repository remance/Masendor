def reset_animation(self):
    """
    Reset animation variable, used for animation that take utmost priority like die
    :param self: Object of the animation sprite
    """
    self.show_frame = 0
    self.animation_timer = 0
    self.interrupt_animation = True
