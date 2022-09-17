from gamescript import battleui


def trait_skill_icon_blit(self):
    """For blitting skill and trait icon into subunit info ui"""
    screen_rect = self.screen_rect

    position = self.troop_card_ui.rect.topleft
    position = [position[0] + 70, position[1] + 60]  # start position
    start_row = position[0]

    for icon in self.skill_icon.sprites():
        icon.kill()

    for trait in self.troop_card_ui.value2[0]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.trait_images["0"], (position[0], position[1]), 0,
                                   game_id=trait))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row

    position = self.troop_card_ui.rect.topleft
    position = [position[0] + 70, position[1] + 100]
    start_row = position[0]

    for skill in self.troop_card_ui.value2[1]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.skill_images["0"], (position[0], position[1]), 1,
                                   game_id=skill))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row
