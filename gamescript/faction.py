import pygame


class Faction(pygame.sprite.Sprite):
    faction_list = None

    def __init__(self, faction_id):
        self.game_id = faction_id
        self.name = self.faction_list[self.game_id][0]
        self.religion = None
        self.government_type = None
        self.population = 0
        self.language_list = {}
        self.culture = {}
        self.technology = {}
        self.capital = None
        self.city = []
        self.image = self.faction_list.images[faction_id]
