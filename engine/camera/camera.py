from pygame import Surface


class Camera:
    def __init__(self, screen, camera_size):
        self.image = Surface.subsurface(screen, (screen.get_rect().width * 0.1, screen.get_rect().height * 0.1,
                                                 camera_size[0], camera_size[1]))  # Camera image
        camera_w, camera_h = self.image.get_rect().size  # get size of camera
        self.camera_w_center = camera_w / 2
        self.camera_h_center = camera_h / 2

        self.rect = self.image.get_rect(topleft=(screen.get_rect().width * 0.1, screen.get_rect().height * 0.1))

    def update(self, pos, blit_objects, out_surfaces):
        """Update self camera with sprite blit to camera image"""
        image = self.image
        image.fill((0, 0, 0))
        camera_left_bound = pos[0] - self.camera_w_center
        camera_top_bound = pos[1] - self.camera_h_center
        rect = self.rect
        for blit_object in blit_objects:  # Blit sprite to camara image
            surface_rect = blit_object.rect

            surface_left_x, surface_top_y = surface_rect.topleft

            if surface_rect.colliderect(rect):
                # only blit if image in camera at all
                image.blit(blit_object.image, (surface_left_x - camera_left_bound,
                                               surface_top_y - camera_top_bound))

        for surface in out_surfaces:  # surface that get blit with pos on screen instead of in battle
            self.image.blit(surface.image, surface.rect)
