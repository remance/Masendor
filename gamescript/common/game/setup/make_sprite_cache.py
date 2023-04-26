import threading


def make_sprite_cache(self, who_todo):
    p = threading.Thread(target=self.create_troop_sprite_pool,
                         args=(self, who_todo),
                         daemon=True)
    p.start()
