# code/hud.py
import pygame
import os

class HUD:
	def __init__(self, screen, player):
		self.screen = screen
		self.player = player

		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		self.font_large = pygame.font.Font(font_path, 18)
		self.font_small = pygame.font.Font(font_path, 12)

		self.bar_w      = 200
		self.bar_h      = 20
		self.margin     = 20
		self.bar_border = 3

	def _draw_bar(self, x, y, current, maximum, color_fill, color_bg, label):
		bg_rect = pygame.Rect(x, y, self.bar_w, self.bar_h)
		pygame.draw.rect(self.screen, color_bg, bg_rect, border_radius=4)

		if maximum > 0:
			fill_w = int((current / maximum) * self.bar_w)
			fill_w = max(0, fill_w)
			fill_rect = pygame.Rect(x, y, fill_w, self.bar_h)
			pygame.draw.rect(self.screen, color_fill, fill_rect, border_radius=4)

		pygame.draw.rect(self.screen, '#111111', bg_rect, self.bar_border, border_radius=4)

		text = f'{label}  {current}/{maximum}'
		surf = self.font_small.render(text, True, '#EEEEEE')
		self.screen.blit(surf, (x + 6, y + 3))

	def draw(self):
		# ── Calcola larghezza pannello in base al nome ─────────────────
		name_text = f'{self.player.player_name} Porceddu  —  Lv.{self.player.level}'
		name_w    = self.font_small.size(name_text)[0]
		panel_w   = max(260, name_w + 40)

		# ── Pannello sfondo semi-trasparente ──────────────────────────
		panel = pygame.Surface((panel_w, 110), pygame.SRCALPHA)
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

		# ── Barra EXP ─────────────────────────────────────────────────
		self._draw_bar(
			x=self.margin, y=self.margin + 28,
			current=self.player.exp,
			maximum=self.player.exp_to_next,
			color_fill='#f0d080',
			color_bg='#4a3a00',
			label='EXP'
		)

		# ── Nome e livello ────────────────────────────────────────────
		name_surf = self.font_small.render(name_text, True, '#f0d080')
		self.screen.blit(name_surf, (self.margin, self.margin + 56))

		# ── Arma equipaggiata ─────────────────────────────────────────
		weapon_surf = self.font_small.render(
			f'Arma: {self.player.weapon}  ATK: {self.player.attack_power}', True, '#aaaaaa'
		)
		self.screen.blit(weapon_surf, (self.margin, self.margin + 74))