import gc

import pygame


def start_battle(self, char_selected=None):
    self.error_log.write("\n Map: " + str(self.map_title.name) + ", Source: " +
                         str(self.source_name_list[self.map_source]) + ", Character: " + str(char_selected) + "\n")

    start_char_selected = char_selected
    if self.enactment:
        start_char_selected = None

    if self.map_type == "preset":
        map_data = self.map_data[self.map_title.name]
    elif self.map_type == "custom":
        map_data = self.custom_map_data["info"]

    self.battle.prepare_new_game(self.ruleset, self.ruleset_folder, self.team_selected, self.map_type,
                                 self.map_selected, self.map_source, start_char_selected,
                                 map_data, self.camp_pos[self.map_source])
    self.battle.run_game()
    pygame.mixer.music.unload()
    pygame.mixer.music.set_endevent(self.SONG_END)
    pygame.mixer.music.load(self.music_list[0])
    pygame.mixer.music.play(-1)
    gc.collect()  # collect no longer used object in previous battle from memory

    # for when memory leak checking
    # print(gc.get_objects())
    # print(vars(self))
    # for item in gc.get_objects():
    # #     try:
    #         # if type(item) == unit.Unit or type(item) == subunit.Subunit or type(item) == leader.Leader:
    #     if type(item) == dict:
    #         print(item, type(item))
    # print(item.current_animation)
    # print(vars(item))
    #         # asdasd
    #     # except NameError:
    #     #     asdasdasd
    #     except:
    #         pass
    # print(gc.get_referrers(self.subunit_animation_pool))
