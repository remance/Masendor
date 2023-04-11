from unittest.mock import patch


def test_pickleable_surface():
    import pickle
    import pygame
    import io
    from gamescript.save_load_pickle_with_surfaces import PickleableSurface

    surface1 = pygame.Surface((64,)*2)
    pygame.draw.circle(surface1, 'red', (32, 32), 32)
    pickleable_surface1 = PickleableSurface(surface1)

    handle = io.BytesIO()
    pickle.dump(pickleable_surface1, handle)

    handle.seek(0)

    pickleable_surface2 = pickle.load(handle)

    s1 = surface1
    s2 = pickleable_surface2.surface

    # NOTE: better looking solution is to make two dicts and just assert them
    for x in range(64):
        for y in range(64):
            assert s1.get_at((x, y)) == s2.get_at((x, y))


@patch("gamescript.save_load_pickle_with_surfaces.PickleableSurface.__eq__",
       lambda self, other: self.surface == other.surface)
def test_recursive_surface_to_pickleable_surface():
    import pygame
    from gamescript.save_load_pickle_with_surfaces import recursive_cast_surface_to_pickleable_surface
    from gamescript.save_load_pickle_with_surfaces import PickleableSurface

    surface = pygame.Surface((64,)*2)
    pygame.draw.circle(surface, 'red', (32, 32), 32)

    data = {
        "a": {
            "b": surface
        }
    }

    recursive_cast_surface_to_pickleable_surface(data)

    assert data == {
        "a": {
            "b": PickleableSurface(surface)
        }
    }
