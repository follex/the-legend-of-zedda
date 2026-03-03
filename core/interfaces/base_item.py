# core/interfaces/base_item.py
from abc import ABC, abstractmethod

class BaseItem(ABC):
    """
    Classe base per tutti gli oggetti (pozioni, chiavi, tesori, ecc.).
    
    Esempio di utilizzo:
        from core.interfaces.base_item import BaseItem
        
        class PozioneDiVita(BaseItem):
            name        = "Pozione di Vita"
            item_type   = "consumable"
            sprite_path = "graphics/pozione_vita.png"
            
            def use(self, player):
                player.health = min(player.max_health, player.health + 50)
    """

    name:        str  = "Oggetto Sconosciuto"
    description: str  = ""
    sprite_path: str  = ""
    stackable:   bool = True       # può avere più copie nello stesso slot
    max_stack:   int  = 99

    # Tipo: 'consumable' | 'key' | 'treasure' | 'equipment' | 'quest'
    item_type:   str  = "consumable"

    @abstractmethod
    def use(self, player):
        """Cosa succede quando il player usa l'oggetto."""
        pass

    def on_pickup(self, player):
        """Chiamato quando il player raccoglie l'oggetto."""
        from core.event_bus import event_bus
        event_bus.emit('item_picked_up', {
            'item':   self.name,
            'player': player
        })

    def on_drop(self, player):
        """Chiamato quando il player lascia cadere l'oggetto."""
        pass