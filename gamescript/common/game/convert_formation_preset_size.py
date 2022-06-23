import numpy as np
from PIL import Image


def convert_formation_preset_size(self):
    """
    Convert the default formation preset array to new one with the unit size according to the genre setting,
    use pillow image resize since it is too much trouble to do it manually
    :param self:
    """
    self.troop_data.unit_formation_list = {}
    for key, value in self.troop_data.default_unit_formation_list.items():
        image = Image.fromarray(value)
        image = image.resize((self.unit_size[0], self.unit_size[1]))
        new_value = np.array(image)
        self.troop_data.unit_formation_list[key] = new_value
