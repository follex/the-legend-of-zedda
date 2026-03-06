# code/hud.py
import pygame
import os

class HUD:
	def __init__(self, screen, player):
		self.screen = screen
		self.player = player

		# ── Font ──────────────────────────────────────────────────────
		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		self.font_large  = pygame.font.Font(font_path, 18)
		self.font_small  = pygame.font.Font(font_path, 12)

		# ── Dimensioni barra ──────────────────────────────────────────
		self.bar_w      = 200
		self.bar_h      = 20
		self.margin     = 20
		self.bar_border = 3

	def _draw_bar(self, x, y, current, maximum, color_fill, color_bg, label):
		"""Disegna una barra con sfondo, riempimento e etichetta."""
		# Sfondo scuro
		bg_rect = pygame.Rect(x, y, self.bar_w, self.bar_h)
		pygame.draw.rect(self.screen, color_bg, bg_rect, border_radius=4)

		# Riempimento proporzionale
		if maximum > 0:
			fill_w = int((current / maximum) * self.bar_w)
			fill_w = max(0, fill_w)
			fill_rect = pygame.Rect(x, y, fill_w, self.bar_h)
			pygame.draw.rect(self.screen, color_fill, fill_rect, border_radius=4)

		# Bordo
		pygame.draw.rect(self.screen, '#111111', bg_rect, self.bar_border, border_radius=4)

		# Etichetta con valori
		text = f'{label}  {current}/{maximum}'
		surf = self.font_small.render(text, True, '#EEEEEE')
		self.screen.blit(surf, (x + 6, y + 3))

	def draw(self):
		# ── Pannello sfondo semi-trasparente ──────────────────────────
		panel = pygame.Surface((260, 80), pygame.SRCALPHA)
		panel.fill((0, 0, 0, 140))
		self.screen.blit(panel, (self.margin - 10, self.margin - 10))

		# ── Barra HP ──────────────────────────────────────────────────
		self._draw_bar(
			x=self.margin, y=self.margin,
			current=self.player.health,
			maximum=self.player.max_health,
			color_fill='#c0392b',
			color_bg='#4a0000',
			label='HP'
		)

		# ── Nome personaggio ──────────────────────────────────────────
		name_surf = self.font_small.render(
			f'{self.player.player_name} Porceddu', True, '#f0d080'
		)
		self.screen.blit(name_surf, (self.margin, self.margin + 28))

		# ── Arma equipaggiata ─────────────────────────────────────────
		weapon_surf = self.font_small.render(
			f'Arma: {self.player.weapon}', True, '#aaaaaa'
		)
		self.screen.blit(weapon_surf, (self.margin, self.margin + 46))