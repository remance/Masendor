import gc

from pygame.mixer import music


def start_battle(self, player_unit=None):
    self.error_log.write("\n Map: " + str(self.map_selected) + ", Source: " +
                         str(self.map_source_selected) + ", Character: " + str(player_unit) + "\n")

    music.unload()
    music.set_endevent(self.SONG_END)
    self.battle.prepare_new_game(player_unit)
    self.battle.run_game()
    music.unload()
    music.set_endevent(self.SONG_END)
    music.load(self.music_list[0])
    music.play(-1)
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
