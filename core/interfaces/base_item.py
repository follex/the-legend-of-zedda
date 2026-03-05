# core/interfaces/base_item.py
from abc import ABC, abstractmethod

class BaseItem(ABC):
	"""
	Classe base per tutti gli oggetti.

	Gli oggetti di solito hanno solo sprite_path statico.
	Le animazioni sono opzionali (es. un oggetto che brilla/pulsa).

	Esempio con animazione:
		sprite_path = "graphics/pozione.png"
		animations = {
			'idle': "graphics/pozione_glow.png",   # spritesheet con effetto luce
		}
	"""

	name:        str  = "Oggetto Sconosciuto"
	description: str  = ""
	item_type:   str  = "consumable"  # 'consumable'|'key'|'treasure'|'equipment'|'quest'
	stackable:   bool = True
	max_stack:   int  = 99

	sprite_path: str  = ""

	animations:  dict = {}
	animation_frame_duration: int = 200

	VALID_ANIMATION_KEYS = {
		'idle', 'pickup',
	}

	@abstractmethod
	def use(self, player):
		pass

	def on_pickup(self, player):
		from core.event_bus import event_bus
		event_bus.emit('item_picked_up', {'item': self.name, 'player': player})

	def on_drop(self, player):
		pass

	def get_current_sprite(self, action: str = 'idle') -> str:
		if self.animations and action in self.animations:
			return self.animations[action]
		return self.sprite_path