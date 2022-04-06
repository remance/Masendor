import pygame

rotation_list = (90, 120, 45, 0, -90, -45, -120, 180, -180)
rotation_name = ("l_side", "l_sidedown", "l_sideup", "front", "r_side", "r_sideup", "r_sidedown", "back", "back")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}


def rotate(self):
    """rotate sprite image may use when subunit can change direction independently of unit, this is not use
    for animation sprite"""
    if self.zoom != self.max_zoom:
        self.image = pygame.transform.rotate(self.inspect_image_original, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
    if self.unit.selected and self.state != 100:
        self.selected_inspect_image = pygame.transform.rotate(self.selected_inspect_image_original, self.angle)
        self.image.blit(self.selected_inspect_image, self.selected_inspect_image_rect)