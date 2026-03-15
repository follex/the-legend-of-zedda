# code/pause_menu.py
import pygame
import os
import sys


class PauseMenu:
	"""
	Menu di pausa — appare sopra il gioco premendo ESC.
	Voci: Riprendi / Salva partita / Carica ultimo salvataggio /
	      Ricomincia da capo / Menu principale / Esci
	"""

	def __init__(self, screen, has_save=False):
		self.screen   = screen
		self.has_save = has_save
		self.selected = 0

		self.items = [
			('Riprendi',                  'resume'),
			('Salva partita  (F5)',        'save'),
		]
		if has_save:
			self.items.append(('Carica ultimo salvataggio', 'load'))
		self.items += [
			('Ricomincia da capo',         'restart'),
			('Menu principale',            'menu'),
			('Esci dal gioco',             'quit'),
		]

		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		try:
			self.font_title = pygame.font.Font(font_path, 20)
			self.font_item  = pygame.font.Font(font_path, 16)
			self.font_small = pygame.font.Font(font_path, 10)
		except Exception:
			self.font_title = pygame.font.SysFont('Arial', 20, bold=True)
			self.font_item  = pygame.font.SysFont('Arial', 16)
			self.font_small = pygame.font.SysFont('Arial', 10)

		self._item_rects = []
		self._blink      = True
		self._blink_t    = 0

	def draw(self):
		sw, sh = self.screen.get_size()

		# Overlay scuro
		overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 170))
		self.screen.blit(overlay, (0, 0))

		# Pannello centrale
		panel_w = 380
		panel_h = 60 + len(self.items) * 50 + 30
		panel_x = (sw - panel_w) // 2
		panel_y = (sh - panel_h) // 2

		panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel.fill((12, 16, 28, 240))
		pygame.draw.rect(panel, (100, 80, 30),
		                 (0, 0, panel_w, panel_h), 2, border_radius=8)
		pygame.draw.rect(panel, (60, 45, 15),
		                 (4, 4, panel_w-8, panel_h-8), 1, border_radius=6)
		self.screen.blit(panel, (panel_x, panel_y))

		# Titolo
		title = self.font_title.render('- PAUSA -', True, (240, 210, 80))
		self.screen.blit(title, title.get_rect(
			centerx=sw // 2, y=panel_y + 16))

		pygame.draw.line(self.screen, (80, 60, 20),
		                 (panel_x + 20, panel_y + 48),
		                 (panel_x + panel_w - 20, panel_y + 48))

		# Voci menu
		self._item_rects = []
		for i, (label, _) in enumerate(self.items):
			is_sel = (i == self.selected)
			y = panel_y + 58 + i * 50

			# Sfondo voce selezionata
			if is_sel:
				bg = pygame.Surface((panel_w - 20, 38), pygame.SRCALPHA)
				bg.fill((60, 45, 10, 180))
				pygame.draw.rect(bg, (140, 110, 30),
				                 (0, 0, panel_w-20, 38), 1, border_radius=4)
				self.screen.blit(bg, (panel_x + 10, y - 4))

			# Colore speciale per voci pericolose
			if label.startswith('Ricomincia') or label.startswith('Esci'):
				color = (200, 80, 80) if is_sel else (140, 60, 60)
			elif label.startswith('Menu'):
				color = (180, 140, 60) if is_sel else (120, 100, 50)
			else:
				color = (240, 210, 80) if is_sel else (160, 140, 80)

			surf = self.font_item.render(label, True, color)
			rect = surf.get_rect(centerx=sw // 2, centery=y + 15)
			self.screen.blit(surf, rect)
			self._item_rects.append(rect)

			# Cursore lampeggiante
			if is_sel and self._blink:
				cur = self.font_item.render('>', True, (240, 180, 40))
				self.screen.blit(cur, (rect.left - 22, rect.top))

		# Hint in basso
		hint = self.font_small.render(
			'FRECCE: naviga    INVIO: conferma    ESC: riprendi',
			True, (60, 50, 25))
		self.screen.blit(hint, hint.get_rect(
			centerx=sw // 2, y=panel_y + panel_h - 20))

	def update(self, dt):
		self._blink_t += dt
		if self._blink_t >= 500:
			self._blink   = not self._blink
			self._blink_t = 0

	def handle_event(self, event):
		"""
		Ritorna:
		  None       — nessuna azione
		  'resume'   — riprendi il gioco
		  'save'     — salva
		  'load'     — carica
		  'restart'  — ricomincia da capo
		  'menu'     — menu principale
		  'quit'     — esci
		"""
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				return 'resume'
			if event.key == pygame.K_UP:
				self.selected = (self.selected - 1) % len(self.items)
			if event.key == pygame.K_DOWN:
				self.selected = (self.selected + 1) % len(self.items)
			if event.key in (pygame.K_RETURN, pygame.K_SPACE):
				return self.items[self.selected][1]

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			for i, rect in enumerate(self._item_rects):
				if rect.inflate(40, 16).collidepoint(event.pos):
					if self.selected == i:
						return self.items[i][1]
					self.selected = i

		if event.type == pygame.MOUSEMOTION:
			for i, rect in enumerate(self._item_rects):
				if rect.inflate(40, 16).collidepoint(event.pos):
					self.selected = i

		return None