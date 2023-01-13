import pygame


def zoom_scale(self):
    """camera zoom change and rescale the sprite and position scale
    sprite with the closest zoom will be scale in the play animation function instead"""
    self.use_animation_sprite = False
    if self.camera_zoom != self.max_camera_zoom:
        if self.camera_zoom > 1:
            self.inspect_base_image = self.inspect_base_image3.copy()  # reset image for new scale
            dim = pygame.Vector2(self.inspect_base_image.get_width() * self.camera_zoom / self.max_camera_zoom,
                                 self.inspect_base_image.get_height() * self.camera_zoom / self.max_camera_zoom)
            self.image = pygame.transform.smoothscale(self.inspect_base_image, (int(dim[0]), int(dim[1])))
            if self.unit.selected and self.state != 100:
                self.selected_inspect_base_image = pygame.transform.smoothscale(self.selected_inspect_base_image2,
                                                                                (int(dim[0]), int(dim[1])))
        else:  # furthest zoom
            self.inspect_base_image = self.far_image.copy()
            self.image = self.inspect_base_image.copy()
            if self.unit.selected and self.state != 100:
                self.selected_inspect_base_image = self.far_selected_image.copy()
        self.inspect_base_image = self.image.copy()
        self.inspect_base_image2 = self.image.copy()
        self.rotate()
    elif self.camera_zoom == self.max_camera_zoom:  # TODO add weapon specific action condition
        self.use_animation_sprite = True
    self.change_pos_scale()
