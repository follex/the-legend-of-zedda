# code/weapon.py
import pygame
import os


def _get_weapon_cls(weapon_name):
	"""Cerca la classe arma nel Registry. Ritorna None se non trovata."""
	try:
		from core.registry import registry
		return registry.get('weapons', weapon_name)
	except Exception:
		return None


def _make_placeholder(direction, color=(180, 140, 60)):
	"""Genera uno sprite arma placeholder per direzione."""
	if direction in ('left', 'right'):
		surf = pygame.Surface((48, 16), pygame.SRCALPHA)
	else:
		surf = pygame.Surface((16, 48), pygame.SRCALPHA)
	surf.fill(color)
	pygame.draw.rect(surf, (220, 200, 80), surf.get_rect(), 2)
	return surf


class Weapon(pygame.sprite.Sprite):
	def __init__(self, player, groups):
		super().__init__(groups)
		self.sprite_type = 'weapon'

		direction = player.status.split('_')[0]

		self.image = self._load_image(player.weapon, direction)

		# Posiziona l'arma vicino al player in base alla direzione
		if direction == 'right':
			self.rect = self.image.get_rect(
				midleft=player.rect.midright + pygame.math.Vector2(0, 16))
		elif direction == 'left':
			self.rect = self.image.get_rect(
				midright=player.rect.midleft + pygame.math.Vector2(0, 16))
		elif direction == 'down':
			self.rect = self.image.get_rect(
				midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
		elif direction == 'up':
			self.rect = self.image.get_rect(
				midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))
		else:
			self.rect = self.image.get_rect(center=player.rect.center)

	def _load_image(self, weapon_name, direction):
		"""
		Cerca lo sprite arma in questo ordine:
		1. Cartella plugin (_plugin_dir/graphics/weapons/nome/direzione.png)
		2. Cartella globale (graphics/weapons/nome/direzione.png)
		3. Placeholder colorato
		"""
		# 1. Cerca nei plugin
		cls = _get_weapon_cls(weapon_name)
		if cls is not None:
			plugin_dir = getattr(cls, '_plugin_dir', None)
			if plugin_dir:
				path = os.path.join(plugin_dir, 'graphics', 'weapons',
				                    weapon_name, f'{direction}.png')
				if os.path.exists(path):
					return pygame.image.load(path).convert_alpha()

			# Prova anche sprite_path diretto nella classe
			sprite_path = getattr(cls, 'sprite_path', '')
			if sprite_path and plugin_dir:
				full = os.path.join(plugin_dir, sprite_path)
				if os.path.exists(full):
					return pygame.image.load(full).convert_alpha()

		# 2. Cerca nella cartella globale
		base = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'graphics', 'weapons', weapon_name
		)
		path = os.path.join(base, f'{direction}.png')
		if os.path.exists(path):
			return pygame.image.load(path).convert_alpha()

		# 3. Placeholder
		return _make_placeholder(direction)