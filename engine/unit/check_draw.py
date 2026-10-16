def check_draw(self, dt):
    if not self.invisible:
        camera_rect = self.camera.rect
        surface_rect = self.rect

        if surface_rect.colliderect(camera_rect):
            # TODO maybe add occlusion culling using shadow mini cell,
            #  (create mini black version of all sprites and map to mini screen metrix,
            #  then each cell is marked occluded only if opacity is not 1)
            blit_check = (self.char_id, int(self.pos[0]), int(self.pos[1]), self.direction, self.animation_name,
                          self.show_frame)
            if blit_check not in self.blit_culling_check:
                if self.not_show_delay:
                    self.not_show_delay -= dt
                    if self.not_show_delay < 0:
                        self.not_show_delay = 0
                else:
                    self.blit_culling_check.add(blit_check)
                    if not self.in_drawer:
                        self.battle_camera_drawer.add(self)
                        self.in_drawer = True
            else:  # other character with very close location and same animation exist no need to blit it
                if self.in_drawer:
                    if not self.not_show_delay:
                        self.not_show_delay = 1
                    self.battle_camera_drawer.remove(self)
                    self.in_drawer = False
        elif self.in_drawer:
            self.not_show_delay = 0
            self.battle_camera_drawer.remove(self)
            self.in_drawer = False
    elif self.in_drawer:
        self.battle_camera_drawer.remove(self)
        self.in_drawer = False
