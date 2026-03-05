# core/interfaces/base_enemy.py
from abc import ABC, abstractmethod

class BaseEnemy(ABC):
	"""
	Classe base per tutti i nemici.

	Animazioni (opzionali):
		Se 'animations' è vuoto, il motore usa 'sprite_path' come immagine statica.
		Se 'animations' è popolato, il motore cicla i fotogrammi dello spritesheet
		in base all'azione corrente del nemico.

	Esempio senza animazioni (immagine statica):
		sprite_path = "graphics/goblin.png"

	Esempio con animazioni:
		sprite_path = "graphics/goblin.png"   # fallback statico
		animations = {
			'idle':        "graphics/goblin_idle.png",
			'walk_down':   "graphics/goblin_walk_down.png",
			'walk_up':     "graphics/goblin_walk_up.png",
			'walk_left':   "graphics/goblin_walk_left.png",
			'walk_right':  "graphics/goblin_walk_right.png",
			'attack':      "graphics/goblin_attack.png",
			'hit':         "graphics/goblin_hit.png",
			'death':       "graphics/goblin_death.png",
		}
	"""

	# ── Attributi obbligatori ──────────────────────────────────────────
	name:        str   = "Nemico Sconosciuto"
	health:      int   = 100
	damage:      int   = 10
	speed:       float = 2.0
	exp_reward:  int   = 10

	# ── Grafica ────────────────────────────────────────────────────────
	sprite_path: str   = ""        # immagine statica (sempre obbligatoria come fallback)

	animations:  dict  = {}        # dizionario azione → percorso spritesheet (opzionale)
	animation_frame_duration: int = 120   # millisecondi per fotogramma

	# Chiavi valide per il dizionario animations
	VALID_ANIMATION_KEYS = {
		'idle',
		'walk_down', 'walk_up', 'walk_left', 'walk_right',
		'attack', 'cast', 'shoot',
		'hit', 'death',
	}

	# ── Attributi opzionali ────────────────────────────────────────────
	can_fly:       bool  = False
	is_boss:       bool  = False
	aggro_radius:  float = 200.0
	attack_radius: float = 50.0

	@abstractmethod
	def attack(self, player):
		"""Logica di attacco al player."""
		pass

	@abstractmethod
	def on_death(self):
		"""Cosa succede quando il nemico muore."""
		pass

	def on_spawn(self):
		"""Chiamato quando il nemico appare nella mappa."""
		pass

	def on_hit(self, damage: int):
		"""Chiamato quando il nemico riceve un colpo."""
		self.health -= damage

	def drop_item(self, item_name: str):
		"""Segnala al registry di spawnare un oggetto."""
		from core.event_bus import event_bus
		event_bus.emit('enemy_drop_item', {
			'enemy': self.name,
			'item':  item_name
		})

	def get_current_sprite(self, action: str = 'idle') -> str:
		"""
		Restituisce il percorso dell'immagine per l'azione richiesta.
		Se le animazioni non sono definite o l'azione non esiste,
		ritorna sprite_path come fallback statico.
		"""
		if self.animations and action in self.animations:
			return self.animations[action]
		return self.sprite_path