from pygame import Surface, Rect


class Camera:
    def __init__(self, start_pos, screen_rect):
        self.pos = start_pos  # Starting camara pos
        self.image = Surface(screen_rect.size)  # Camera image

    def update(self, pos, surfaces):
        """Update self camera with sprite blit to camera image"""
        self.image.fill((0, 0, 0))
        self.pos = pos
        camera_w, camera_h = self.image.get_rect().size  # get size of camera
        camera_x = self.pos[0] - camera_w / 2  # Current camera center x
        camera_y = self.pos[1] - camera_h / 2  # Current camera center y
        for surface in surfaces:  # Blit sprite to camara image
            surface_x, surface_y = surface.rect.left, surface.rect.top
            surface_w, surface_h = surface.rect.size
            if surface_x + surface_w > 0 and surface_y + surface_h > 0:
                self.image.blit(surface.image, (surface_x - camera_x, surface_y - camera_y))
