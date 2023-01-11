import pygame


def rotate(self):
    """rotate sprite image may use when subunit can change direction independently of unit, this is not use
    for animation sprite"""
    if self.camera_zoom != self.max_camera_zoom:
        self.image = pygame.transform.rotate(self.inspect_base_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        if self.unit.selected and self.state != 100:
            self.selected_inspect_image = pygame.transform.rotate(self.selected_inspect_base_image, self.angle)
            self.image.blit(self.selected_inspect_image, self.selected_inspect_image_rect)
