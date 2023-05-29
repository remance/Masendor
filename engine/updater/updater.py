from pygame.sprite import LayeredUpdates


class ReversedLayeredUpdates(LayeredUpdates):
    def __init__(self):
        LayeredUpdates.__init__(self)

    def add_internal(self, sprite, layer=None):
        """
        Change add internal to order the sprite list from top to bottom instead of the original bottom to top

        """
        self.spritedict[sprite] = self._init_rect

        if layer is None:
            try:
                layer = sprite.layer
            except AttributeError:
                layer = self._default_layer
                setattr(sprite, "_layer", layer)
        elif hasattr(sprite, "_layer"):
            setattr(sprite, "_layer", layer)

        sprites = self._spritelist  # speedup
        sprites.reverse()  # revert to bottom to top first so no need to change algorithm below
        sprites_layers = self._spritelayers
        sprites_layers[sprite] = layer

        # add the sprite at the right position
        # bisect algorithmus
        leng = len(sprites)
        low = mid = 0
        high = leng - 1
        while low <= high:
            mid = low + (high - low) // 2
            if sprites_layers[sprites[mid]] <= layer:
                low = mid + 1
            else:
                high = mid - 1
        # linear search to find final position
        while mid < leng and sprites_layers[sprites[mid]] <= layer:
            mid += 1
        sprites.insert(mid, sprite)
        sprites.reverse()  # revert to top to bottom

    def remove_internal(self, sprite):
        """
        For removing a sprite from this group internally.

        :param sprite: The sprite we are removing.
        """
        lost_rect = self.spritedict[sprite]
        if lost_rect:
            self.lostsprites.append(lost_rect)
        sprite.event = False
        sprite.event_press = False
        sprite.event_hold = False
        sprite.mouse_over = False
        del self.spritedict[sprite]