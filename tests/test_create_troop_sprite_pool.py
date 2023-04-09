from unittest.mock import patch

def test_pickleable_surface():
    import pickle
    import pygame
    #from gamescript.common.game.create_troop_sprite_pool import PickleableSurface
    from gamescript.create_troop_sprite_pool_methods import PickleableSurface
    import io

    surface = pygame.Surface((64,)*2)
    pygame.draw.circle( surface, 'red', (32,32), 32  )
    ps = PickleableSurface( surface )

    handle = io.BytesIO()
    pickle.dump(ps,handle)
   

    handle.seek(0)

    ps2 = pickle.load(handle)

    s1 = surface
    s2 = ps2.surface

    for x in range(64):
        for y in range(64):
            assert s1.get_at( (x,y) ) == s2.get_at((x,y))

   

@patch("gamescript.create_troop_sprite_pool_methods.PickleableSurface.__eq__", 
        lambda self,other : self.surface == other.surface)
def test_recursive_surface_to_pickleable_surface():
    import pygame
    from gamescript.create_troop_sprite_pool_methods import recursive_cast_surface_to_pickleable_surface
    from gamescript.create_troop_sprite_pool_methods import PickleableSurface

    surface = pygame.Surface((64,)*2)
    pygame.draw.circle( surface, 'red', (32,32), 32  )
 


    _dict = {
        "a":{
            "b": surface
        }
    }


    recursive_cast_surface_to_pickleable_surface(_dict)

    assert _dict == {
        "a": {
            "b": PickleableSurface(surface)
        }
    }




