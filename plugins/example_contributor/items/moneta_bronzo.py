# plugins/example_contributor/items/moneta.py
from core.interfaces.base_item import BaseItem

class MonetaDiBronzo(BaseItem):
    name        = "Moneta di Bronzo"
    description = "Una moneta consumata dal tempo. Vale poco, ma è pur sempre denaro."
    item_type   = "treasure"
    stackable   = True
    max_stack   = 99
    sprite_path = "graphics/items/moneta_bronzo_48.png"  # opzionale

    def use(self, player):
        pass  # le monete non si "usano", si accumulano
