# Guida per i Contributor — The Legend of Zedda

Questo documento spiega cosa puoi aggiungere al gioco tramite il sistema plugin.

## Struttura di un plugin

```
plugins/
└── tuo_nome/
    ├── plugin.json
    ├── enemies/
    │   └── mio_nemico.py
    ├── weapons/
    │   └── mia_arma.py
    ├── items/
    │   └── mio_oggetto.py
    ├── spells/
    │   └── mia_magia.py
    ├── map_zones/
    │   └── mia_zona.py
    ├── ui/
    │   └── mia_ui.py
    ├── hud/
    │   └── mio_hud.py
    └── graphics/
        ├── monsters/mio_nemico/
        │   ├── idle/0.png
        │   ├── move/0.png
        │   └── attack/0.png
        ├── weapons/mia_arma/
        │   ├── up.png
        │   ├── down.png
        │   ├── left.png
        │   └── right.png
        └── items/mio_oggetto.png
```

## plugin.json

```json
{
    "name": "Nome del tuo plugin",
    "author": "tuo_nome",
    "version": "1.0",
    "contributes": {
        "enemies":   ["enemies/mio_nemico.py"],
        "weapons":   ["weapons/mia_arma.py"],
        "items":     ["items/mio_oggetto.py"],
        "spells":    ["spells/mia_magia.py"],
        "map_zones": ["map_zones/mia_zona.py"],
        "ui":        ["ui/mia_ui.py"],
        "hud":       ["hud/mio_hud.py"]
    }
}
```

---

## Nemici (BaseEnemy) ✅ Completamente integrato

```python
from core.interfaces.base_enemy import BaseEnemy

class Orco(BaseEnemy):
    name         = "orco"          # minuscolo — usato come nome cartella sprite
    health       = 120
    damage       = 18
    speed        = 2.5
    exp_reward   = 30
    aggro_radius = 250.0
    attack_radius = 60.0
    sprite_path  = "graphics/monsters/orco/idle/0.png"   # relativo al plugin

    def attack(self, player):
        player.take_damage(self.damage)

    def on_death(self):
        self.drop_item("Moneta di Bronzo")  # deve corrispondere a item.name
```

**Sprite:** metti le immagini in `graphics/monsters/orco/idle/`, `move/`, `attack/`
con file numerati `0.png`, `1.png`, ecc.

---

## Armi (BaseWeapon) ✅ Completamente integrato

```python
from core.interfaces.base_weapon import BaseWeapon

class SpadaMagica(BaseWeapon):
    name         = "SpadaMagica"
    damage       = 45
    cooldown     = 0.5      # secondi
    weapon_type  = 'melee'  # 'melee' | 'ranged' | 'magic'
    sprite_path  = "graphics/weapons/spada_magica.png"

    def use(self, player, targets):
        for target in targets:
            target.take_damage(self.damage)
```

**Sprite:** metti `up.png`, `down.png`, `left.png`, `right.png` in
`graphics/weapons/SpadaMagica/` (stesso nome della classe).

Il giocatore cicla tra le armi con **Q** — la tua arma apparirà nell'elenco.

---

## Oggetti (BaseItem) ✅ Completamente integrato

```python
from core.interfaces.base_item import BaseItem

class PozioneDiVita(BaseItem):
    name        = "Pozione di Vita"
    description = "Recupera 50 HP."
    item_type   = "consumable"   # consumable | key | treasure | equipment | quest
    stackable   = True
    max_stack   = 10
    sprite_path = "graphics/items/pozione.png"

    def use(self, player):
        player.health = min(player.max_health, player.health + 50)
```

**Spawn:** gli oggetti appaiono automaticamente sulla mappa all'avvio.
Aggiungi `spawn_count = 3` per controllare quante copie spawnano.

---

## Magie (BaseSpell) ⚠️ Registrata, logica da implementare

```python
from core.interfaces.base_spell import BaseSpell

class FulmineDivino(BaseSpell):
    name       = "Fulmine Divino"
    mana_cost  = 30
    damage     = 60
    cooldown   = 2.0
    spell_type = 'offensive'

    def cast(self, player, targets):
        for t in targets:
            t.take_damage(self.damage)
```

---

## Zone Mappa (BaseMapZone) ✅ Integrato sulla mappa mondo

```python
from core.interfaces.base_map_zone import BaseMapZone

class ForestaOscura(BaseMapZone):
    name             = "Foresta Oscura"
    description      = "Una foresta piena di pericoli antichi."
    tilemap_path     = "maps/foresta_oscura.tmx"  # relativo al plugin
    background_music = "foresta_oscura"            # sounds/foresta_oscura.mp3
    map_position     = (280, 520)   # (x, y) su World_of_Zedda.png (1024x1536)
    unlocked         = True

    def on_enter(self, player): pass
    def on_exit(self, player):  pass
```

La zona apparirà automaticamente sulla **mappa mondo** (tasto M).

---

## HUD personalizzato (BaseHUD) ✅ Completamente integrato

```python
from core.interfaces.base_hud import BaseHUD
import pygame

class ManaBarHUD(BaseHUD):
    name     = "Barra Mana"
    position = 'top_left'
    visible  = True

    def draw(self, screen, player):
        # Disegna la tua barra HUD
        pygame.draw.rect(screen, (50, 80, 200), (20, 130, 200, 16))
```

Viene disegnato automaticamente ogni frame sopra il gioco.

---

## UI personalizzata (BaseUI) ✅ Completamente integrato

```python
from core.interfaces.base_ui import BaseUI
import pygame

class ShopUI(BaseUI):
    name    = "Negozio"
    trigger = 'npc_contact'   # manual | npc_contact | zone_enter | item_use

    def draw(self, screen, game_state):
        # Disegna la tua UI
        pass

    def handle_event(self, event, game_state):
        pass
```

Con `trigger = 'zone_enter'` la UI si apre automaticamente entrando nel livello.