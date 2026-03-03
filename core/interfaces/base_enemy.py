# core/interfaces/base_enemy.py
from abc import ABC, abstractmethod

class BaseEnemy(ABC):
    """
    Classe base per tutti i nemici.
    Ogni contributor DEVE implementare i metodi astratti.
    
    Esempio di utilizzo:
        from core.interfaces.base_enemy import BaseEnemy
        
        class Orco(BaseEnemy):
            name    = "Orco della Foresta"
            health  = 120
            damage  = 25
            speed   = 2
            sprite_path = "graphics/orco.png"
            
            def attack(self, player):
                player.take_damage(self.damage)
                
            def on_death(self):
                self.drop_item("chiave_arrugginita")
    """

    # ── Attributi obbligatori (il contributor li definisce come variabili di classe)
    name:        str   = "Nemico Sconosciuto"
    health:      int   = 100
    damage:      int   = 10
    speed:       float = 2.0
    sprite_path: str   = ""        # percorso relativo alla cartella del plugin
    exp_reward:  int   = 10        # esperienza guadagnata dal player alla morte

    # ── Attributi opzionali
    can_fly:        bool  = False
    is_boss:        bool  = False
    aggro_radius:   float = 200.0  # distanza entro cui aggredisce il player
    attack_radius:  float = 50.0   # distanza entro cui attacca

    @abstractmethod
    def attack(self, player):
        """Logica di attacco al player."""
        pass

    @abstractmethod
    def on_death(self):
        """Cosa succede quando il nemico muore (drop oggetti, suoni, ecc.)."""
        pass

    # ── Metodi con comportamento di default (il contributor può sovrascriverli)
    def on_spawn(self):
        """Chiamato quando il nemico appare nella mappa."""
        pass

    def on_hit(self, damage: int):
        """Chiamato quando il nemico riceve un colpo."""
        self.health -= damage

    def drop_item(self, item_name: str):
        """Segnala al registry di spawnare un oggetto alla posizione del nemico."""
        from core.event_bus import event_bus
        event_bus.emit('enemy_drop_item', {
            'enemy': self.name,
            'item':  item_name
        })