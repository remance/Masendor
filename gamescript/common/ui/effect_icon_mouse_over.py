def effect_icon_mouse_over(self, icon_list, mouse_right):
    effect_mouse_over = False
    for icon in icon_list:
        if icon.rect.collidepoint(self.mouse_pos):
            self.single_text_popup.pop(self.mouse_pos, self.troop_card_ui.value2[icon.icon_type][icon.game_id]["Name"])
            self.battle_ui_updater.add(self.single_text_popup)
            effect_mouse_over = True
            if mouse_right:
                if icon.icon_type == "trait":
                    section = 7
                elif icon.icon_type == "skill":
                    section = 6
                elif icon.icon_type == "status":
                    section = 5  # Status effect
                self.popout_lorebook(section, icon.game_id)
            break
    return effect_mouse_over
