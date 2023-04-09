from typing import Dict, Any, Optional

import pygame

from pygame_gui._constants import UI_TEXT_EFFECT_FINISHED, TEXT_EFFECT_BOUNCE
from pygame_gui.core.interfaces.text_owner_interface import IUITextOwnerInterface
from pygame_gui.core.text.text_effects.text_effect import TextEffect
from pygame_gui.core.text.text_line_chunk import TextLineChunkFTFont


class BounceEffect(TextEffect):
    """
    A bounce effect
    """
    def __init__(self, text_owner: IUITextOwnerInterface,
                 params: Optional[Dict[str, Any]] = None,
                 text_sub_chunk: Optional[TextLineChunkFTFont] = None):
        super().__init__()
        self.text_owner = text_owner
        self.text_sub_chunk = text_sub_chunk
        self.loop = True
        self.bounce_max_height = 5
        self.time_to_complete_bounce = 0.5
        self.time_acc = 0.0
        self.bounce_height = 0
        self.text_changed = False
        self.text_owner.set_text_offset_pos((0, 0), self.text_sub_chunk)
        self._load_params(params)

    def _load_params(self, params: Optional[Dict[str, Any]]):
        if params is not None:
            if 'loop' in params:
                if isinstance(params['loop'], bool):
                    self.loop = params['loop']
                elif isinstance(params['loop'], str):
                    self.loop = bool(int(params['loop']))
                else:
                    self.loop = bool(params['loop'])
            if 'bounce_max_height' in params:
                self.bounce_max_height = int(params['bounce_max_height'])
            if 'time_to_complete_bounce' in params:
                self.time_to_complete_bounce = float(params['time_to_complete_bounce'])

    def update(self, time_delta: float):
        """
        Updates the effect with amount of time passed since the last call to update.

        :param time_delta: time in seconds since last frame.
        """
        self.time_acc += time_delta
        if self.time_acc < self.time_to_complete_bounce:

            bounce_progress = self.time_acc / max(self.time_to_complete_bounce, 0.000001)
            if bounce_progress < 0.5:
                bounce_height = int(((bounce_progress * 2) ** 2) * self.bounce_max_height)
            else:
                bounce_height = int((((1-bounce_progress) * 2) ** 2) * self.bounce_max_height)

            if bounce_height != self.bounce_height:
                self.bounce_height = max(bounce_height, 0)
                self.text_changed = True
        elif self.loop:
            self.time_acc = 0.0
        else:
            # finished effect
            self.text_owner.stop_finished_effect(self.text_sub_chunk)

            event_data = {'ui_element': self.text_owner,
                          'ui_object_id': self.text_owner.get_object_id(),
                          'effect': TEXT_EFFECT_BOUNCE}
            if self.text_sub_chunk is not None:
                event_data['effect_tag_id'] = self.text_sub_chunk.effect_id
            pygame.event.post(pygame.event.Event(UI_TEXT_EFFECT_FINISHED, event_data))

    def has_text_changed(self) -> bool:
        """
        Lets us know when the effect has changed enough to warrant us
        redrawing the text.

        :return: True if it is is time to redraw our text.
        """
        if self.text_changed:
            self.text_changed = False
            return True
        else:
            return False

    def apply_effect(self):
        """
        Apply the effect to the text
        """
        self.text_owner.set_text_offset_pos((0, -self.bounce_height),
                                            self.text_sub_chunk)
