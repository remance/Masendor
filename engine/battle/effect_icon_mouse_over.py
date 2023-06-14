from engine.lorebook.lorebook import Lorebook

status_section = Lorebook.status_section
skill_section = Lorebook.skill_section


def effect_icon_mouse_over(self, icon_list, mouse_right):
    effect_mouse_over = False
    for icon in icon_list:
        if icon in self.ui_updater and icon.rect.collidepoint(self.self.player1_battle_cursor.pos):
            self.text_popup.popup(self.player1_battle_cursor.rect, icon.name)
            self.add_ui_updater(self.text_popup)
            effect_mouse_over = True
            break
    return effect_mouse_over
