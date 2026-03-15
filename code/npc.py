# code/npc.py
import pygame
import os


class NPC(pygame.sprite.Sprite):
	"""
	Personaggio non giocabile con dialogo.
	Quando il player si avvicina appare un indicatore [!] sopra l'NPC.
	Premendo SPACE vicino all'NPC si apre il dialogo.
	"""

	TALK_RADIUS    = 80    # distanza in pixel per attivare il dialogo
	INDICATOR_BOB  = 4     # pixel di oscillazione dell'indicatore [!]

	def __init__(self, name, pos, groups, dialogue_lines, sprite_path=None,
	             color=(180, 140, 80), on_talk=None):
		"""
		name           : nome dell'NPC (mostrato sopra di lui)
		pos            : posizione (x, y) in pixel
		groups         : sprite groups
		dialogue_lines : lista di stringhe per il dialogo
		sprite_path    : percorso immagine opzionale
		color          : colore placeholder se niente sprite
		on_talk        : callback chiamata la prima volta che si parla
		"""
		super().__init__(groups)

		self.npc_name       = name
		self.dialogue_lines = dialogue_lines
		self.on_talk        = on_talk
		self._talked        = False   # ha già parlato con il player?

		# ── Sprite ────────────────────────────────────────────────────
		self.image = self._load_image(sprite_path, color)
		self.rect  = self.image.get_rect(center=pos)
		self.hitbox = self.rect.inflate(-10, -10)

		# ── Animazione indicatore ─────────────────────────────────────
		self._bob_t      = 0.0
		self._base_y     = float(pos[1])
		self._player_near = False

		# Font
		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		try:
			self._font_name = pygame.font.Font(font_path, 10)
			self._font_ind  = pygame.font.Font(font_path, 16)
		except Exception:
			self._font_name = pygame.font.SysFont('Arial', 10)
			self._font_ind  = pygame.font.SysFont('Arial', 16, bold=True)

	def _load_image(self, sprite_path, color):
		if sprite_path and os.path.exists(sprite_path):
			try:
				return pygame.image.load(sprite_path).convert_alpha()
			except Exception:
				pass
		# Placeholder — figura stilizzata colorata
		surf = pygame.Surface((48, 64), pygame.SRCALPHA)
		# Corpo
		pygame.draw.rect(surf, color, (12, 20, 24, 32), border_radius=4)
		# Testa
		pygame.draw.circle(surf, color, (24, 14), 12)
		# Occhi
		pygame.draw.circle(surf, (40, 30, 20), (20, 13), 2)
		pygame.draw.circle(surf, (40, 30, 20), (28, 13), 2)
		# Bordo
		pygame.draw.circle(surf, (0, 0, 0, 100), (24, 14), 12, 1)
		return surf

	def check_player_proximity(self, player):
		"""Aggiorna _player_near in base alla distanza dal player."""
		dist = pygame.math.Vector2(self.rect.center).distance_to(
		       pygame.math.Vector2(player.rect.center))
		self._player_near = dist <= self.TALK_RADIUS

	def try_talk(self, dialogue_ui):
		"""
		Chiamato quando il player preme SPACE vicino all'NPC.
		Ritorna True se ha aperto un dialogo.
		"""
		if not self._player_near or dialogue_ui.visible:
			return False

		def on_close():
			if not self._talked and self.on_talk:
				self.on_talk()
			self._talked = True

		dialogue_ui.open(self.dialogue_lines, on_close=on_close)
		return True

	def update(self, events=[]):
		"""Animazione bob dell'indicatore."""
		self._bob_t += 0.08
		# nessun bob sul rettangolo principale — solo sull'indicatore in draw()

	def draw_indicator(self, screen, camera_offset):
		"""
		Disegna il nome e l'indicatore [!] sopra l'NPC.
		Chiamato da Level dopo custom_draw.
		"""
		screen_pos = pygame.math.Vector2(self.rect.topleft) - camera_offset

		# Nome NPC
		name_surf = self._font_name.render(self.npc_name, True, (240, 220, 120))
		name_x    = screen_pos.x + self.rect.width // 2 - name_surf.get_width() // 2
		name_y    = screen_pos.y - 22
		screen.blit(name_surf, (name_x, name_y))

		# Indicatore [!] quando il player è vicino
		if self._player_near and not self._talked:
			bob    = int(self.INDICATOR_BOB * abs(
			         pygame.math.Vector2(1, 0).rotate(self._bob_t * 57.3).x))
			ind    = self._font_ind.render('!', True, (255, 220, 50))
			ind_x  = screen_pos.x + self.rect.width // 2 - ind.get_width() // 2
			ind_y  = screen_pos.y - 42 - bob
			# Cerchio sfondo
			cx = int(ind_x + ind.get_width() // 2)
			cy = int(ind_y + ind.get_height() // 2)
			pygame.draw.circle(screen, (200, 60, 60), (cx, cy), 12)
			pygame.draw.circle(screen, (240, 100, 100), (cx, cy), 12, 2)
			screen.blit(ind, (ind_x, ind_y))