import pygame
import pygame.freetype


class Camera:
    screen_rect = None

    def __init__(self, startpos, zoom):
        self.zoom = zoom  # Zoom level
        self.pos = startpos  # Starting camara pos
        self.image = pygame.Surface((self.screen_rect.width, self.screen_rect.height))  # Camera image

    def update(self, pos, surfaces, zoom):
        """Update self camera with sprite blit to camera image"""
        self.zoom = zoom
        self.image.fill((0, 0, 0))
        self.pos = pos
        camera_w, camera_h = self.image.get_rect().size  # get size of camera
        camera_x = self.pos[0] - camera_w / 2  # Current camera center x
        camera_y = self.pos[1] - camera_h / 2  # Current camera center y
        for surface in surfaces:  # Blit sprite to camara image
            surface_x, surface_y = surface.rect.left, surface.rect.top
            surface_w, surface_h = surface.image.get_rect().size
            rect = pygame.Rect(surface_x - camera_x, surface_y - camera_y, surface_w, surface_h)  # get rect that shown inside camera
            self.image.blit(surface.image, rect)
