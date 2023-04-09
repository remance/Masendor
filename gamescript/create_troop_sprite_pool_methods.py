import pygame

class PickleableSurface:

    def __init__(self, surface):
        self.surface = surface

    def __getstate__(self):
        return ( pygame.image.tobytes(self.surface,"RGBA"), self.surface.get_size() )



    def __setstate__(self, state):
        self.surface = pygame.image.frombytes(state[0],state[1],"RGBA")




def recursive_cast_surface_to_pickleable_surface(_dict):

    for k,v in _dict.items():
        if type(v) == dict:
            recursive_cast_surface_to_pickleable_surface(v)
        elif type(v) == pygame.Surface:
            _dict[k] = PickleableSurface(v)
        elif type(v) == tuple:
            _dict[k] = tuple([ c if type(c) != pygame.Surface else PickleableSurface(c) for c in _dict[k]])


def recursive_cast_pickleable_surface_to_surface(_dict):

    for k,v in _dict.items():
        if type(v) == dict:
            recursive_cast_pickleable_surface_to_surface(v)
        if type(v) == PickleableSurface:
            _dict[k] = v.surface
        elif type(v) == tuple:
            _dict[k] = tuple([ c if type(c) != PickleableSurface else c.surface for c in _dict[k]])


