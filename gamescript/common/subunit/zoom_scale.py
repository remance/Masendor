import pygame


def zoom_scale(self):
    """camera zoom change and rescale the sprite and position scale
    sprite with the closest zoom will be scale in the play animation function instead"""
    self.use_animation_sprite = False
    if self.zoom != self.max_zoom:
        if self.zoom > 1:
            self.inspect_base_image = self.inspect_base_image3.copy()  # reset image for new scale
            dim = pygame.Vector2(self.inspect_base_image.get_width() * self.zoom / self.max_zoom,
                                 self.inspect_base_image.get_height() * self.zoom / self.max_zoom)
            self.image = pygame.transform.scale(self.inspect_base_image, (int(dim[0]), int(dim[1])))
            if self.unit.selected and self.state != 100:
                self.selected_inspect_base_image = pygame.transform.scale(self.selected_inspect_base_image2,
                                                                          (int(dim[0]), int(dim[1])))
        else:  # furthest zoom
            self.inspect_base_image = self.far_image.copy()
            self.image = self.inspect_base_image.copy()
            if self.unit.selected and self.state != 100:
                self.selected_inspect_base_image = self.far_selected_image.copy()
        self.inspect_base_image = self.image.copy()
        self.inspect_base_image2 = self.image.copy()
        self.rotate()
    elif self.zoom == self.max_zoom:  # TODO add weapon specific action condition
        self.use_animation_sprite = True
    self.change_pos_scale()
