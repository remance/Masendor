from gamescript.common import utility

list_scroll = utility.list_scroll


def mouse_scrolling_process(self, mouse_scroll_up, mouse_scroll_down):
    if self.event_log.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at event log
        if mouse_scroll_up:
            self.event_log.current_start_row -= 1
            if self.event_log.current_start_row < 0:  # can go no further than the first log
                self.event_log.current_start_row = 0
            else:
                self.event_log.recreate_image()  # recreate event_log image
                self.event_log.scroll.change_image(new_row=self.event_log.current_start_row)
        elif mouse_scroll_down:
            self.event_log.current_start_row += 1
            if self.event_log.current_start_row + self.event_log.max_row_show - 1 < self.event_log.len_check and \
                    self.event_log.len_check > 9:
                self.event_log.recreate_image()
                self.event_log.scroll.change_image(new_row=self.event_log.current_start_row)
            else:
                self.event_log.current_start_row -= 1

