# core/interfaces/base_weapon.py
from abc import ABC, abstractmethod

class BaseWeapon(ABC):
	"""
	Classe base per tutte le armi.

	Esempio senza animazioni:
		sprite_path = "graphics/spada.png"

	Esempio con animazioni:
		sprite_path = "graphics/spada.png"
		animations = {
			'idle':    "graphics/spada_idle.png",
			'attack':  "graphics/spada_attack.png",
		}
	"""

	name:        str   = "Arma Sconosciuta"
	damage:      int   = 10
	cooldown:    float = 0.5
	weapon_type: str   = "melee"   # 'melee' | 'ranged' | 'magic'

	sprite_path: str   = ""
	sound_path:  str   = ""

	animations:  dict  = {}
	animation_frame_duration: int = 100

	VALID_ANIMATION_KEYS = {
		'idle', 'attack', 'shoot', 'cast',
	}

	projectile_speed: float = 0.0
	projectile_range: float = 0.0

	@abstractmethod
	def use(self, player, targets: list):
		"""Logica di utilizzo dell'arma."""
		pass

	def on_equip(self, player):
		pass

	def on_unequip(self, player):
		pass

	def get_current_sprite(self, action: str = 'idle') -> str:
		if self.animations and action in self.animations:
			return self.animations[action]
		return self.sprite_path