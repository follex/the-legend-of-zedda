# core/interfaces/base_spell.py
from abc import ABC, abstractmethod

class BaseSpell(ABC):
    """
    Classe base per tutte le magie.
    
    Esempio di utilizzo:
        from core.interfaces.base_spell import BaseSpell
        
        class Fulmine(BaseSpell):
            name        = "Fulmine"
            mana_cost   = 30
            damage      = 60
            spell_type  = "offensive"
            sprite_path = "graphics/fulmine.png"
            
            def cast(self, player, targets):
                if player.mana >= self.mana_cost:
                    player.mana -= self.mana_cost
                    for t in targets:
                        t.on_hit(self.damage)
    """

    name:        str   = "Magia Sconosciuta"
    mana_cost:   int   = 20
    damage:      int   = 0
    heal:        int   = 0         # se è una magia curativa
    cooldown:    float = 1.0
    sprite_path: str   = ""
    sound_path:  str   = ""
    animation_path: str = ""       # animazione dell'effetto

    # Tipo: 'offensive' | 'defensive' | 'heal' | 'utility'
    spell_type:  str   = "offensive"

    @abstractmethod
    def cast(self, player, targets: list):
        """Logica di lancio della magia."""
        pass

    def on_learn(self, player):
        """Chiamato quando il player impara la magia."""
        pass