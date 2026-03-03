# core/interfaces/base_map_zone.py
from abc import ABC, abstractmethod

class BaseMapZone(ABC):
    """
    Classe base per le zone di mappa.
    Ogni zona è un'area del mondo con la sua tilemap, nemici e oggetti.
    
    Esempio di utilizzo:
        from core.interfaces.base_map_zone import BaseMapZone
        
        class ForestaOscura(BaseMapZone):
            name          = "Foresta Oscura"
            tilemap_path  = "map_zones/foresta_oscura.tmx"
            enemy_spawns  = [
                {'enemy': 'Orco', 'position': (10, 5), 'count': 3},
            ]
            item_spawns = [
                {'item': 'PozioneDiVita', 'position': (15, 8)},
            ]
            
            def on_enter(self, player):
                print("Sei entrato nella Foresta Oscura...")
                
            def on_exit(self, player):
                pass
    """

    name:         str  = "Zona Sconosciuta"
    tilemap_path: str  = ""        # file .tmx creato con Tiled
    background_music: str = ""     # musica di sottofondo opzionale
    is_interior:  bool = False     # è un interno (dungeon, casa, ecc.)?

    # Liste di spawn: il contributor le definisce come attributi di classe
    enemy_spawns: list = []        # [{'enemy': 'NomeClasse', 'position': (x,y), 'count': n}]
    item_spawns:  list = []        # [{'item': 'NomeClasse',  'position': (x,y)}]
    npc_spawns:   list = []        # [{'npc':  'NomeClasse',  'position': (x,y)}]

    @abstractmethod
    def on_enter(self, player):
        """Chiamato quando il player entra nella zona."""
        pass

    @abstractmethod
    def on_exit(self, player):
        """Chiamato quando il player lascia la zona."""
        pass

    def on_first_visit(self, player):
        """Chiamato solo la prima volta che il player visita la zona."""
        pass