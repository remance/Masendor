def ui_mouse_click(self):
    """Mouse over and click ui that is not subunit card and unitbox (topbar and commandbar)"""
    for this_ui in self.ui_updater:
        if this_ui in self.battle_ui_updater and this_ui.rect.collidepoint(self.mouse_pos):
            self.click_any = True
            break
    return self.click_any
