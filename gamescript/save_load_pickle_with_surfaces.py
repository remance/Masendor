# This game make use of store data (cache) in pickles. These data contain Surfaces.
# Surfaces can not directly be stored in pickles. The save_pickle_with_surfaces
# and load_pickle_with_surfaces methods in this file make use of a solution that
# makes store pickles through a wrapper class possible.

import pygame
import pickle


def save_pickle_with_surfaces(file_path, data):
    recursive_cast_surface_to_pickleable_surface(data)

    with open(file_path, "wb") as handle:
        pickle.dump(data, handle)


def load_pickle_with_surfaces(file_path):
    with open(file_path, "rb") as handle:
        data = pickle.load(handle)

    recursive_cast_pickleable_surface_to_surface(data)
    return data

# NOTE: PickleableSurface is far from perfect but it works for what is required.
#       This class has hardcoded format (RGBA) and does not take flags into account
#       and maybe more.
class PickleableSurface:

    def __init__(self, surface):
        self.surface = surface

    def __getstate__(self):
        return (pygame.image.tobytes(self.surface, "RGBA"), self.surface.get_size())

    def __setstate__(self, state):
        self.surface = pygame.image.frombytes(state[0], state[1], "RGBA")

# ---
# these methods below works what it is required to handle at this moment but it is not guaranteed
# for all data structures.

def recursive_cast_surface_to_pickleable_surface(data):
    f = recursive_cast_surface_to_pickleable_surface
    if type(data) == dict:
        for k, v in data.items():
            if type(v) == dict:
                f(v)
            elif type(v) == pygame.Surface:
                data[k] = PickleableSurface(v)
            elif type(v) == tuple:
                data[k] = tuple([c if type(c) != pygame.Surface else PickleableSurface(c) for c in data[k]])
    elif type(data) == tuple:
        for v in data:
            f(v)


def recursive_cast_pickleable_surface_to_surface(data):
    f = recursive_cast_pickleable_surface_to_surface
    if type(data) == dict:
        for k, v in data.items():
            if type(v) == dict:
                f(v)
            if type(v) == PickleableSurface:
                data[k] = v.surface
            elif type(v) == tuple:
                data[k] = tuple([c if type(c) != PickleableSurface else c.surface for c in data[k]])
    elif type(data) == tuple:
        for v in data:
            f(v)

# ---
