import gc

import pygame


def start_battle(self, player_unit=None):
    self.error_log.write("\n Map: " + str(self.map_title.name) + ", Source: " +
                         str(self.map_source) + ", Character: " + str(player_unit) + "\n")

    selected_player_unit = player_unit
    if self.enactment:
        selected_player_unit = None

    self.battle.prepare_new_game(self.team_selected, self.map_type,
                                 self.map_selected, self.map_source, selected_player_unit,
                                 self.source_data, self.camp_pos)
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
    #         # if type(item) == unit.Unit or type(item) == unit.Unit or type(item) == leader.Leader:
    #     if type(item) == dict:
    #         print(item, type(item))
    # print(item.current_animation)
    # print(vars(item))
    #         # asdasd
    #     # except NameError:
    #     #     asdasdasd
    #     except:
    #         pass
    # print(gc.get_referrers(self.unit_animation_pool))
