# core/interfaces/base_weapon.py
from abc import ABC, abstractmethod

class BaseWeapon(ABC):
    """
    Classe base per tutte le armi.
    
    Esempio di utilizzo:
        from core.interfaces.base_weapon import BaseWeapon
        
        class SpadaDiFuoco(BaseWeapon):
            name        = "Spada di Fuoco"
            damage      = 40
            weapon_type = "melee"
            sprite_path = "graphics/spada_fuoco.png"
            
            def use(self, player, targets):
                for t in targets:
                    t.on_hit(self.damage)
    """

    name:        str   = "Arma Sconosciuta"
    damage:      int   = 10
    cooldown:    float = 0.5       # secondi tra un attacco e l'altro
    sprite_path: str   = ""
    sound_path:  str   = ""        # suono opzionale all'uso

    # Tipo: 'melee' | 'ranged' | 'magic'
    weapon_type: str   = "melee"

    # Solo per armi ranged
    projectile_speed:  float = 0.0
    projectile_range:  float = 0.0

    @abstractmethod
    def use(self, player, targets: list):
        """Logica di utilizzo dell'arma."""
        pass

    def on_equip(self, player):
        """Chiamato quando il player equipaggia l'arma."""
        pass

    def on_unequip(self, player):
        """Chiamato quando il player rimuove l'arma."""
        pass