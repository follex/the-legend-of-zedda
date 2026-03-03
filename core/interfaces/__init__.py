# core/interfaces/__init__.py
from .base_enemy    import BaseEnemy
from .base_weapon   import BaseWeapon
from .base_spell    import BaseSpell
from .base_item     import BaseItem
from .base_map_zone import BaseMapZone
from .base_ui       import BaseUI
from .base_hud      import BaseHUD

__all__ = [
    'BaseEnemy', 'BaseWeapon', 'BaseSpell',
    'BaseItem',  'BaseMapZone', 'BaseUI', 'BaseHUD'
]