import time

def play_animation(self, surface, position, speed, play_list):
    if time.time() - self.first_time >= speed:
        if self.show_frame < len(play_list):
            self.show_frame += 1
        self.first_time = time.time()
    # if self.show_frame > self.end_frame:  # TODO add property
    #     self.show_frame = self.start_frame
    #     while self.show_frame < 10 and play_list[self.show_frame] is False:
    #         self.show_frame += 1

    surface.blit(self.frames[int(self.show_frame)], position)