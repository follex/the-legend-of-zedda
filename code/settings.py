# code/settings.py

# Finestra
WIDTH  = 1280
HEIGHT = 720
FPS    = 60
TITLE  = "The Legend of Zedda"

# Tile
TILESIZE = 64

# Colori
WATER_COLOR     = '#71ddee'
UI_BG_COLOR     = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR      = '#EEEEEE'

# Lore
PLAYER_SURNAME   = 'Porceddu'
PRINCESS_NAME    = 'Zedda'
CASTLE_NAME      = 'Castello di Casteddu'
STARTING_VILLAGE = 'Gonnostramatza'

# ── Statistiche per ruolo ─────────────────────────────────────────────
ROLE_DATA = {
    'warrior': {
        'health':        140,
        'attack_power':  35,
        'speed':         4,
        'weapon':        'axe',
        'description':   'Robusto e letale. Più HP e più danno, ma più lento.',
    },
    'archer': {
        'health':        90,
        'attack_power':  22,
        'speed':         6,
        'weapon':        'rapier',
        'description':   'Agile e veloce. Meno HP ma si muove come il vento.',
    },
    'mage': {
        'health':        80,
        'attack_power':  45,
        'speed':         4,
        'weapon':        'sai',
        'description':   'Fragile ma devastante. Il danno più alto di tutti.',
    },
}