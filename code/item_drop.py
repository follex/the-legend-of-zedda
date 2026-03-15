# code/item_drop.py
import pygame
import os


class ItemDrop(pygame.sprite.Sprite):
	"""
	Sprite di un oggetto posato a terra, raccoglibile dal player.
	Mostra l'icona dell'item con un leggero effetto di bob verticale.
	"""

	BOB_SPEED     = 2.0    # velocità oscillazione verticale
	BOB_AMPLITUDE = 4      # pixel di oscillazione
	PICK_UP_RADIUS = 40    # distanza (pixel) alla quale viene raccolta

	def __init__(self, item_cls, pos, groups):
		super().__init__(groups)

		self.item_cls = item_cls
		self.name     = getattr(item_cls, 'name', item_cls.__name__)

		# ── Sprite ────────────────────────────────────────────────────
		self.image = self._load_image(item_cls)
		self.rect  = self.image.get_rect(center=pos)
		self.hitbox = self.rect.copy()

		# ── Bob ───────────────────────────────────────────────────────
		self._base_y  = float(pos[1])
		self._bob_t   = 0.0

	def _load_image(self, item_cls):
		"""
		Prova a caricare l'icona dell'item.
		Prima cerca sprite_path relativo alla cartella del plugin (_plugin_dir),
		poi relativo alla radice del progetto, infine genera un placeholder colorato.
		"""
		sprite_path = getattr(item_cls, 'sprite_path', '')
		plugin_dir  = getattr(item_cls, '_plugin_dir', None)

		if sprite_path:
			# 1. Prova percorso relativo al plugin
			if plugin_dir:
				full = os.path.join(plugin_dir, sprite_path)
				if os.path.exists(full):
					return pygame.image.load(full).convert_alpha()

			# 2. Prova percorso relativo alla radice del progetto
			base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
			full = os.path.join(base, sprite_path)
			if os.path.exists(full):
				return pygame.image.load(full).convert_alpha()

		# 3. Placeholder: quadrato colorato con iniziale del nome
		return self._make_placeholder()

	def _make_placeholder(self):
		"""Genera un'icona placeholder 32x32 colorata."""
		surf = pygame.Surface((32, 32), pygame.SRCALPHA)
		# Colore in base al tipo
		item_type = getattr(self.item_cls, 'item_type', 'consumable')
		colors = {
			'consumable': (80, 200, 80, 220),
			'key':        (220, 200, 50, 220),
			'treasure':   (220, 160, 30, 220),
			'equipment':  (100, 160, 220, 220),
			'quest':      (220, 80, 80, 220),
		}
		color = colors.get(item_type, (160, 160, 160, 220))
		pygame.draw.rect(surf, color, (0, 0, 32, 32), border_radius=6)
		pygame.draw.rect(surf, (255, 255, 255, 180), (0, 0, 32, 32), 2, border_radius=6)

		# Iniziale del nome
		try:
			font = pygame.font.SysFont('Arial', 18, bold=True)
			letter = self.name[0].upper() if self.name else '?'
			txt = font.render(letter, True, (255, 255, 255))
			surf.blit(txt, txt.get_rect(center=(16, 16)))
		except Exception:
			pass

		return surf

	def update(self, events=[]):
		"""Animazione bob verticale."""
		self._bob_t += self.BOB_SPEED * 0.05
		offset = int(self.BOB_AMPLITUDE * pygame.math.Vector2(0, 1)
		             .rotate(self._bob_t * 57.3).y)   # sin approssimato con rotate
		self.rect.centery = int(self._base_y) + offset
		self.hitbox.center = self.rect.center