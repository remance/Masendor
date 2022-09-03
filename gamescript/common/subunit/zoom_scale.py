import pygame


def zoom_scale(self):
    """camera zoom change and rescale the sprite and position scale
    sprite with the closest zoom will be scale in the play animation function instead"""
    self.use_animation_sprite = False
    if self.zoom != self.max_zoom:
        if self.zoom > 1:
            self.inspect_image_original = self.inspect_image_original3.copy()  # reset image for new scale
            dim = pygame.Vector2(self.inspect_image_original.get_width() * self.zoom / self.max_zoom,
                                 self.inspect_image_original.get_height() * self.zoom / self.max_zoom)
            self.image = pygame.transform.scale(self.inspect_image_original, (int(dim[0]), int(dim[1])))
            if self.unit.selected and self.state != 100:
                self.selected_inspect_image_original = pygame.transform.scale(self.selected_inspect_image_original2,
                                                                              (int(dim[0]), int(dim[1])))
        else:  # furthest zoom
            self.inspect_image_original = self.far_image.copy()
            self.image = self.inspect_image_original.copy()
            if self.unit.selected and self.state != 100:
                self.selected_inspect_image_original = self.far_selected_image.copy()
        self.inspect_image_original = self.image.copy()
        self.inspect_image_original2 = self.image.copy()
        self.rotate()
    elif self.zoom == self.max_zoom:  # TODO add weapon specific action condition
        self.use_animation_sprite = True
    self.change_pos_scale()
