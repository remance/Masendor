def effect_icon_mouse_over(self, icon_list, mouse_right):
    effect_mouse_over = False
    for icon in icon_list:
        if icon.rect.collidepoint(self.mouse_pos):
            check_value = self.troop_card_ui.value2[icon.icon_type]
            self.effect_popup.pop(self.mouse_pos, check_value[icon.game_id])
            self.battle_ui_updater.add(self.effect_popup)
            effect_mouse_over = True
            if mouse_right:
                if icon.icon_type == 0:  # Trait
                    section = 7
                elif icon.icon_type == 1:  # Skill
                    section = 6
                else:
                    section = 5  # Status effect
                self.popout_lorebook(section, icon.game_id)
            break
    return effect_mouse_over