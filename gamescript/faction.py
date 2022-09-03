import pygame.freetype


class Faction(pygame.sprite.Sprite):
    faction_list = None

    def __init__(self, faction_id):
        self.game_id = faction_id
        self.name = self.faction_list[self.game_id][0]
        self.image = self.faction_list.images[faction_id]
