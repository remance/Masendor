from pygame import Surface, Rect


class Camera:
    screen_rect = None

    def __init__(self, start_pos):
        self.pos = start_pos  # Starting camara pos
        self.image = Surface((self.screen_rect.width, self.screen_rect.height))  # Camera image

    def update(self, pos, surfaces):
        """Update self camera with sprite blit to camera image"""
        self.image.fill((0, 0, 0))
        self.pos = pos
        camera_w, camera_h = self.image.get_rect().size  # get size of camera
        camera_x = self.pos[0] - camera_w / 2  # Current camera center x
        camera_y = self.pos[1] - camera_h / 2  # Current camera center y
        for surface in surfaces:  # Blit sprite to camara image
            surface_x, surface_y = surface.rect.left, surface.rect.top
            # surface_w, surface_h = surface.image.get_rect().size
            # rect = Rect(surface_x - camera_x, surface_y - camera_y, surface_w,
            #            surface_h)  # get rect that shown inside camera
            # if rect.x + surface_w > 0 and rect.y + surface_h > 0:
            self.image.blit(surface.image, (surface_x - camera_x, surface_y - camera_y))
