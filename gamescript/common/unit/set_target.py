import pygame


def set_target(self, pos):
    """set new base_target, scale base_target from base_target according to zoom scale"""
    self.base_target = pygame.Vector2(pos)  # Set new base base_target
    self.set_subunit_target(target=self.base_target)
