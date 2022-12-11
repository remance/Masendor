def popout_lorebook(self, section, game_id):
    """open and draw enclycopedia at the specified subsection,
    used for when user right click at icon that has encyclopedia section"""
    self.game_state = "menu"
    self.battle_menu.mode = "encyclopedia"
    self.battle_ui_updater.add(self.encyclopedia_stuff)

    self.encyclopedia.change_section(section, self.lore_name_list, self.subsection_name, self.tag_filter_name,
                                     self.lore_name_list.scroll, self.filter_tag_list,
                                     self.filter_tag_list.scroll, self.page_button, self.battle_ui_updater)
    self.encyclopedia.change_subsection(game_id, self.page_button, self.battle_ui_updater)
    self.lore_name_list.scroll.change_image(new_row=self.encyclopedia.current_subsection_row)
