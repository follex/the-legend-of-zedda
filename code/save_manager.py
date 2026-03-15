# code/save_manager.py
"""
Gestisce il salvataggio e caricamento del gioco su file JSON.

Struttura del file di salvataggio (save.json):
{
    "version": 1,
    "player": {
        "name":        "Ale",
        "gender":      "female",
        "role":        "warrior",
        "level":       3,
        "exp":         240,
        "exp_to_next": 337,
        "health":      120,
        "max_health":  160,
        "base_attack": 50,
        "weapon":      "axe"
    },
    "inventory": [
        {"class_name": "MonetaDiBronzo", "quantity": 5},
        null,
        ...
    ],
    "quest": {
        "quest_id":     "main_quest",
        "status":       "active",
        "current_step": 1
    }
}
"""

import json
import os

SAVE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'save.json'
)
SAVE_VERSION = 1


# ── Salvataggio ───────────────────────────────────────────────────────────────

def save(player, quest=None, level=None):
    """
    Salva lo stato corrente del gioco.
    player : oggetto Player
    quest  : oggetto Quest (opzionale)
    level  : oggetto Level (opzionale, per salvare stato mappa)
    """
    data = {
        'version':   SAVE_VERSION,
        'player':    _serialize_player(player),
        'inventory': _serialize_inventory(player),
        'quest':     _serialize_quest(quest),
        'map':       _serialize_map(level),
    }

    path = os.path.abspath(SAVE_FILE)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f'[SAVE] Partita salvata in {path}')
        return True
    except Exception as e:
        print(f'[SAVE] Errore durante il salvataggio: {e}')
        return False


def _serialize_player(player):
    return {
        'name':        player.player_name,
        'gender':      getattr(player, 'gender', 'male'),
        'role':        player.role,
        'level':       player.level,
        'exp':         player.exp,
        'exp_to_next': player.exp_to_next,
        'health':      player.health,
        'max_health':  player.max_health,
        'base_attack': player.base_attack,
        'weapon':      player.weapon,
        'pos':         list(player.rect.center),
    }


def _serialize_inventory(player):
    """Serializza solo gli slot pieni come lista di {index, class_name, quantity}."""
    result = []
    for i, slot in enumerate(player.inventory):
        if slot is not None:
            result.append({
                'index':      i,
                'class_name': slot.item_cls.__name__,
                'quantity':   slot.quantity,
            })
    return result


def _serialize_quest(quest):
    if quest is None:
        return None
    return {
        'quest_id':     quest.quest_id,
        'status':       quest.status,
        'current_step': quest.current_step,
    }


# ── Caricamento ───────────────────────────────────────────────────────────────

def exists():
    """Ritorna True se esiste un file di salvataggio."""
    return os.path.exists(os.path.abspath(SAVE_FILE))


def load():
    """
    Carica il file di salvataggio.
    Ritorna un dizionario con i dati, oppure None se non esiste o è corrotto.
    """
    path = os.path.abspath(SAVE_FILE)
    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get('version') != SAVE_VERSION:
            print(f'[SAVE] Versione save non compatibile: {data.get("version")}')
            return None

        print(f'[SAVE] Partita caricata da {path}')
        return data

    except Exception as e:
        print(f'[SAVE] Errore durante il caricamento: {e}')
        return None


def delete():
    """Elimina il file di salvataggio."""
    path = os.path.abspath(SAVE_FILE)
    if os.path.exists(path):
        os.remove(path)
        print('[SAVE] File di salvataggio eliminato.')


def _serialize_map(level):
    """Serializza lo stato corrente della mappa: nemici vivi e item presenti."""
    if level is None:
        return None

    # Nemici ancora vivi — salva nome e posizione
    enemies = []
    for enemy in level.enemy_sprites:
        enemies.append({
            'name': enemy.name,
            'pos':  list(enemy.rect.center),
            'health': enemy.health,
        })

    # Item ancora presenti sulla mappa
    items = []
    for drop in level.item_sprites:
        items.append({
            'class_name': drop.item_cls.__name__,
            'pos':        list(drop.rect.center),
        })

    return {
        'enemies': enemies,
        'items':   items,
    }


def apply_to_player(save_data, player):
    """
    Applica i dati del save a un oggetto Player già creato.
    Da chiamare dopo aver creato il Level e il Player.
    """
    if save_data is None:
        return

    p = save_data.get('player', {})

    # Posizione
    pos = p.get('pos', None)
    if pos:
        player.rect.center  = tuple(pos)
        player.hitbox.center = tuple(pos)

    player.level       = p.get('level',       1)
    player.exp         = p.get('exp',          0)
    player.exp_to_next = p.get('exp_to_next',  100)
    player.health      = p.get('health',       player.max_health)
    player.max_health  = p.get('max_health',   player.max_health)
    player.base_attack = p.get('base_attack',  player.base_attack)
    player.weapon      = p.get('weapon',       player.weapon)

    # Ricalcola attack_power con l'arma caricata
    from player import WEAPON_DATA
    weapon_dmg         = WEAPON_DATA.get(player.weapon, WEAPON_DATA['sword'])['damage']
    player.attack_power = player.base_attack + weapon_dmg


def apply_inventory(save_data, player):
    """
    Ripristina l'inventario del player dai dati del save.
    Richiede che i plugin siano già caricati nel Registry.
    """
    if save_data is None:
        return

    inventory_data = save_data.get('inventory', [])
    if not inventory_data:
        return

    try:
        from core.registry import registry
        from player import InventorySlot
    except Exception as e:
        print(f'[SAVE] Errore import per inventario: {e}')
        return

    all_items = registry.get_all('items')
    class_map = {cls.__name__: cls for cls in all_items.values()}

    # Azzera l'inventario prima di ripristinarlo
    player.inventory = [None] * len(player.inventory)

    for slot_data in inventory_data:
        i          = slot_data.get('index', 0)
        class_name = slot_data.get('class_name', '')
        quantity   = slot_data.get('quantity', 1)

        if i >= len(player.inventory):
            continue

        item_cls = class_map.get(class_name)
        if item_cls:
            player.inventory[i] = InventorySlot(item_cls, quantity)
        else:
            print(f'[SAVE] Classe item non trovata: {class_name} (plugin rimosso?)')


def apply_quest(save_data, quest):
    """Ripristina lo stato della quest dai dati del save."""
    if save_data is None or quest is None:
        return

    q = save_data.get('quest')
    if not q:
        return

    if q.get('quest_id') != quest.quest_id:
        return

    from quest import ACTIVE, COMPLETED, NOT_STARTED
    status = q.get('status', NOT_STARTED)
    if status in (ACTIVE, COMPLETED, NOT_STARTED):
        quest.status       = status
        quest.current_step = q.get('current_step', 0)


def apply_map(save_data, level):
    """
    Ripristina lo stato della mappa:
    - Rimuove tutti i nemici e item spawnati normalmente
    - Rispawna solo quelli salvati (con HP e posizione originali)
    """
    if save_data is None:
        return

    map_data = save_data.get('map')
    if not map_data:
        return

    # ── Ripristina nemici ────────────────────────────────────────────
    # Rimuovi tutti i nemici attuali
    for enemy in list(level.enemy_sprites):
        enemy.kill()

    # Rispawna solo i nemici salvati
    from enemy import Enemy
    for e in map_data.get('enemies', []):
        enemy = Enemy(
            name=e['name'],
            pos=tuple(e['pos']),
            groups=[level.visible_sprites, level.enemy_sprites],
            obstacle_sprites=level.obstacle_sprites,
            player=level.player,
        )
        # Ripristina HP (potrebbero essere stati feriti prima del save)
        enemy.health = e.get('health', enemy.health)

    # ── Ripristina item ──────────────────────────────────────────────
    # Rimuovi tutti gli item attuali
    for drop in list(level.item_sprites):
        drop.kill()

    # Rispawna solo gli item salvati
    try:
        from core.registry import registry
        from item_drop import ItemDrop
        all_items = registry.get_all('items')
        class_map = {cls.__name__: cls for cls in all_items.values()}

        for item_data in map_data.get('items', []):
            class_name = item_data.get('class_name', '')
            pos        = tuple(item_data.get('pos', [640, 480]))
            item_cls   = class_map.get(class_name)
            if item_cls:
                ItemDrop(item_cls, pos, [level.visible_sprites, level.item_sprites])
            else:
                print(f'[SAVE] Item non trovato: {class_name}')
    except Exception as e:
        print(f'[SAVE] Errore ripristino item: {e}')