def change_pause_update(self, pause, updater, except_list=()):
    for item in updater:
        if item not in except_list:
            item.pause = pause
