# core/interfaces/base_hud.py
from abc import ABC, abstractmethod
import pygame

class BaseHUD(ABC):
    """
    Classe base per elementi dell'HUD (visibili durante il gioco).
    (barre HP/mana, icone armi, minimappa, notifiche, ecc.)
    
    Esempio di utilizzo:
        from core.interfaces.base_hud import BaseHUD
        
        class BarraMana(BaseHUD):
            name     = "Barra Mana"
            position = "bottom_left"
            
            def draw(self, screen, player):
                # disegna la barra del mana
                pass
    """

    name: str = "HUD Sconosciuto"
    # Posizione suggerita: 'top_left' | 'top_right' | 'bottom_left' |
    #                      'bottom_right' | 'top_center' | 'bottom_center'
    position: str = "top_left"
    visible:  bool = True

    @abstractmethod
    def draw(self, screen: pygame.Surface, player):
        """Disegna l'elemento HUD. Chiamato ad ogni frame."""
        pass

    def on_player_update(self, player):
        """Chiamato quando i dati del player cambiano (HP, mana, ecc.)."""
        pass