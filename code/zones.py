# code/zones.py
"""
Registro di tutte le zone del mondo di Zedda.
Ogni zona ha:
  name         — nome visualizzato
  description  — testo nel pannello info
  map_file     — percorso del file .tmx (relativo alla radice del progetto)
  map_position — (x, y) sull'immagine originale World_of_Zedda.png (1024x1536)
  unlocked     — se il giocatore può viaggiarci (default True)

Le coordinate map_position si riferiscono all'immagine 1024x1536.
Gonnostramatza è nel Campidano centrale → (390, 680)
Il Castello di Casteddu è in basso a destra → (680, 1200)
"""

BASE_ZONES = [
    {
        'name':         'Gonnostramatza',
        'description':  'Un piccolo villaggio della Marmilla, immerso tra le pianure '
                        'del Campidano. Punto di partenza dell\'avventura. '
                        'Il Vecchio Saggio custodisce qui antichi segreti.',
        'map_file':     'data/maps/gonnostramatza.tmx',
        'map_position': (390, 680),
        'unlocked':     True,
    },
    {
        'name':         'Castello di Casteddu',
        'description':  'L\'imponente castello dove la Principessa Zedda è tenuta '
                        'prigioniera. Le sue torri gotiche si ergono minacciose '
                        'sul cielo del sud. Solo i più coraggiosi osano avvicinarsi.',
        'map_file':     'data/maps/castello_casteddu.tmx',
        'map_position': (680, 1200),
        'unlocked':     False,   # sbloccato avanzando nella quest
    },
]


def get_all_zones():
    """Ritorna la lista completa delle zone, incluse quelle dai plugin."""
    zones = list(BASE_ZONES)

    # Aggiunge zone dai plugin (BaseMapZone con map_position definito)
    try:
        from core.registry import registry
        plugin_zones = registry.get_all('map_zones')
        for name, cls in plugin_zones.items():
            pos = getattr(cls, 'map_position', None)
            if pos:
                zones.append({
                    'name':         getattr(cls, 'name', name),
                    'description':  getattr(cls, 'description', ''),
                    'map_file':     getattr(cls, 'tilemap_path', ''),
                    'map_position': pos,
                    'unlocked':     getattr(cls, 'unlocked', True),
                })
    except Exception:
        pass

    return zones