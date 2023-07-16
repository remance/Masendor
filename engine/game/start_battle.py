import gc

from pygame.mixer import music


def start_battle(self, map_data, player_unit=None):
    self.error_log.write("\n Map: " + str(self.map_selected) + ", Source: " +
                         str(self.map_source_selected) + ", Character: " + str(player_unit) + "\n")
    self.loading_screen("start")

    music.unload()
    music.set_endevent(self.SONG_END)
    self.battle.prepare_new_game(player_unit)
    self.battle.run_game(map_data)
    music.unload()
    music.set_endevent(self.SONG_END)
    music.load(self.music_list[0])
    music.play(-1)
    gc.collect()  # collect no longer used object in previous battle from memory

    # for when memory leak checking
    # logging.warning(mem_top())
    # print(len(vars(self)))
    # print(len(gc.get_objects()))
    # self.error_log.write(str(new_gc_collect).encode('unicode_escape').decode('unicode_escape'))

    # print(vars(self))
    # from engine.unit.unit import Unit
    # type_count = {}
    # for item in gc.get_objects():
    #     if type(item) not in type_count:
    #         type_count[type(item)] = 1
    #     else:
    #         type_count[type(item)] += 1
    # type_count = sorted({key: value for key, value in type_count.items()}.items(), key=lambda item: item[1],
    #                     reverse=True)
    # print(type_count)
    # print(item.current_animation)
    #     print(vars(item))
    # asdasd
    # except NameError:
    #     asdasdasd
    # except:
    #     pass
    # print(gc.get_referrers(self.unit_animation_pool))
