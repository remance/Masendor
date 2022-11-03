from gamescript import battleui


def effect_icon_blit(self):
    """For blitting all status effect icon"""
    screen_rect = self.screen_rect

    position = self.troop_card_ui.rect.topleft
    position = [position[0] + 70, position[1] + 140]
    start_row = position[0]

    for icon in self.effect_icon.sprites():
        icon.kill()

    for status in self.troop_card_ui.value2["status"]:
        self.effect_icon.add(
            battleui.SkillCardIcon(self.status_images["0"], (position[0], position[1]), "status", game_id=status))
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row
