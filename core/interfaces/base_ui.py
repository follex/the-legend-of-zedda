# core/interfaces/base_ui.py
from abc import ABC, abstractmethod
import pygame

class BaseUI(ABC):
    """
    Classe base per elementi di menu e interfaccia utente.
    (schermata pausa, inventario, negozio, dialoghi, ecc.)
    
    Esempio di utilizzo:
        from core.interfaces.base_ui import BaseUI
        
        class MenuNegozio(BaseUI):
            name    = "Negozio di Gonnostramatza"
            trigger = "npc_contact"   # si apre al contatto con un NPC
            
            def draw(self, screen, game_state):
                # disegna il menu del negozio
                pass
                
            def handle_event(self, event, game_state):
                # gestisce i click/tasti nel menu
                pass
    """

    name:    str = "UI Sconosciuta"
    # Quando si apre: 'manual' | 'npc_contact' | 'zone_enter' | 'item_use'
    trigger: str = "manual"

    @abstractmethod
    def draw(self, screen: pygame.Surface, game_state: dict):
        """Disegna l'elemento UI sullo schermo."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event, game_state: dict):
        """Gestisce gli input mentre l'UI è aperta."""
        pass

    def on_open(self, game_state: dict):
        """Chiamato quando l'UI viene aperta."""
        pass

    def on_close(self, game_state: dict):
        """Chiamato quando l'UI viene chiusa."""
        pass