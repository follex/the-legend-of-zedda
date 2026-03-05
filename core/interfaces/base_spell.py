# core/interfaces/base_spell.py
from abc import ABC, abstractmethod

class BaseSpell(ABC):
	"""
	Classe base per tutte le magie.

	Esempio con animazioni:
		sprite_path    = "graphics/fulmine.png"
		animations = {
			'cast':   "graphics/fulmine_cast.png",
			'impact': "graphics/fulmine_impact.png",
		}
	"""

	name:        str   = "Magia Sconosciuta"
	mana_cost:   int   = 20
	damage:      int   = 0
	heal:        int   = 0
	cooldown:    float = 1.0
	spell_type:  str   = "offensive"  # 'offensive'|'defensive'|'heal'|'utility'

	sprite_path:    str = ""
	sound_path:     str = ""

	animations: dict = {}
	animation_frame_duration: int = 80

	VALID_ANIMATION_KEYS = {
		'idle', 'cast', 'impact', 'travel',
	}

	@abstractmethod
	def cast(self, player, targets: list):
		pass

	def on_learn(self, player):
		pass

	def get_current_sprite(self, action: str = 'idle') -> str:
		if self.animations and action in self.animations:
			return self.animations[action]
		return self.sprite_path