def kill_effect_icon(self):
    for icon in self.skill_icons.sprites():
        icon.kill()
        del icon
