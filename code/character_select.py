# character_select.py
import pygame
import sys
from settings import *

class CharacterSelect:
	def __init__(self, screen):
		self.screen = screen
		self.font_title  = pygame.font.SysFont('georgia', 64, bold=True)
		self.font_option = pygame.font.SysFont('georgia', 36)
		self.font_small  = pygame.font.SysFont('georgia', 28)
		self.font_desc   = pygame.font.SysFont('georgia', 22)

		self.selected_gender = None
		self.selected_role   = None

		self.gender_buttons = [
			{'label': '♂ Maschio', 'value': 'male',   'rect': None},
			{'label': '♀ Femmina', 'value': 'female', 'rect': None},
		]
		self.role_buttons = [
			{'label': '⚔ Guerriero', 'value': 'warrior', 'rect': None},
			{'label': '🏹 Arciere',  'value': 'archer',  'rect': None},
			{'label': '🔮 Mago',     'value': 'mage',    'rect': None},
		]
		self.start_button_rect = None

	def draw_button(self, text, cx, cy, selected=False):
		color_bg     = '#c8a96e' if selected else '#3a3a3a'
		color_border = '#f0d080' if selected else '#888888'
		color_text   = '#1a1a1a' if selected else TEXT_COLOR

		surf = self.font_option.render(text, True, color_text)
		w, h = surf.get_width() + 48, surf.get_height() + 20
		rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

		pygame.draw.rect(self.screen, color_bg,     rect, border_radius=10)
		pygame.draw.rect(self.screen, color_border, rect, 2, border_radius=10)
		self.screen.blit(surf, surf.get_rect(center=rect.center))
		return rect

	def _draw_role_stats(self, role, cx, cy):
		"""Mostra HP, ATK e velocità del ruolo sotto i pulsanti."""
		data = ROLE_DATA.get(role, {})
		if not data:
			return

		sw = self.screen.get_width()

		# Descrizione
		desc = self.font_desc.render(data['description'], True, '#aaaaaa')
		self.screen.blit(desc, desc.get_rect(centerx=sw // 2, y=cy))

		# Statistiche
		stats_text = (f"HP: {data['health']}   "
		              f"ATK: {data['attack_power']}   "
		              f"VEL: {data['speed']}   "
		              f"Arma: {data['weapon']}")
		stats = self.font_desc.render(stats_text, True, '#c8a96e')
		self.screen.blit(stats, stats.get_rect(centerx=sw // 2, y=cy + 30))

	def draw(self):
		sw = self.screen.get_width()
		sh = self.screen.get_height()
		self.screen.fill('#1a1a2e')

		title = self.font_title.render('The Legend of Zedda', True, '#f0d080')
		self.screen.blit(title, title.get_rect(centerx=sw // 2, y=40))

		sub = self.font_small.render('Scegli il tuo personaggio', True, '#aaaaaa')
		self.screen.blit(sub, sub.get_rect(centerx=sw // 2, y=120))

		# ── Genere ──────────────────────────────────────────────────
		label_g = self.font_small.render('— GENERE —', True, '#c8a96e')
		self.screen.blit(label_g, label_g.get_rect(centerx=sw // 2, y=190))

		gx_positions = [sw // 2 - 160, sw // 2 + 160]
		for btn, cx in zip(self.gender_buttons, gx_positions):
			btn['rect'] = self.draw_button(
				btn['label'], cx, 260,
				selected=(self.selected_gender == btn['value'])
			)

		# ── Ruolo ────────────────────────────────────────────────────
		label_r = self.font_small.render('— RUOLO —', True, '#c8a96e')
		self.screen.blit(label_r, label_r.get_rect(centerx=sw // 2, y=330))

		rx_positions = [sw // 2 - 280, sw // 2, sw // 2 + 280]
		for btn, cx in zip(self.role_buttons, rx_positions):
			btn['rect'] = self.draw_button(
				btn['label'], cx, 410,
				selected=(self.selected_role == btn['value'])
			)

		# ── Descrizione ruolo selezionato ────────────────────────────
		if self.selected_role:
			self._draw_role_stats(self.selected_role, sw // 2, 460)

		# ── Pulsante start ───────────────────────────────────────────
		start_y = 560
		if self.selected_gender and self.selected_role:
			self.start_button_rect = self.draw_button('▶  INIZIA', sw // 2, start_y, selected=True)
		else:
			hint = self.font_small.render('Seleziona genere e ruolo per iniziare', True, '#666666')
			self.screen.blit(hint, hint.get_rect(centerx=sw // 2, y=start_y - 14))

	def handle_click(self, pos):
		for btn in self.gender_buttons:
			if btn['rect'] and btn['rect'].collidepoint(pos):
				self.selected_gender = btn['value']

		for btn in self.role_buttons:
			if btn['rect'] and btn['rect'].collidepoint(pos):
				self.selected_role = btn['value']

		if (self.start_button_rect and
				self.start_button_rect.collidepoint(pos) and
				self.selected_gender and self.selected_role):
			return True
		return False

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					if self.handle_click(event.pos):
						return self.selected_gender, self.selected_role

			self.draw()
			pygame.display.update()