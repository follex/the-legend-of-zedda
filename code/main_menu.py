# code/main_menu.py
import pygame
import os
import sys
from settings import *


class MainMenu:
	"""
	Menu principale stile RPG anni 90.
	Voci: Nuova Partita / Continua (solo se esiste save) / Esci
	Navigazione con frecce su/giù e INVIO, oppure click del mouse.
	"""

	def __init__(self, screen, has_save=False):
		self.screen   = screen
		self.has_save = has_save

		# Voci del menu
		self.items = ['Nuova Partita']
		if has_save:
			self.items.append('Continua')
		self.items.append('Esci')

		self.selected = 0   # indice voce selezionata

		# Font
		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		try:
			self.font_title  = pygame.font.Font(font_path, 48)
			self.font_sub    = pygame.font.Font(font_path, 13)
			self.font_item   = pygame.font.Font(font_path, 22)
			self.font_small  = pygame.font.Font(font_path, 11)
		except Exception:
			self.font_title  = pygame.font.SysFont('Georgia', 48, bold=True)
			self.font_sub    = pygame.font.SysFont('Georgia', 13)
			self.font_item   = pygame.font.SysFont('Georgia', 22)
			self.font_small  = pygame.font.SysFont('Georgia', 11)

		# Animazione cursore lampeggiante
		self._blink      = True
		self._blink_t    = 0
		self._blink_ms   = 500

		# Cache dei rettangoli per il click
		self._item_rects = []

	def _draw_background(self):
		sw, sh = self.screen.get_size()
		self.screen.fill((8, 12, 20))

		# Griglia di punti decorativa stile anni 90
		dot_color = (20, 30, 45)
		for x in range(0, sw, 32):
			for y in range(0, sh, 32):
				pygame.draw.circle(self.screen, dot_color, (x, y), 1)

		# Bordo dorato
		pygame.draw.rect(self.screen, (100, 80, 30),
		                 (16, 16, sw - 32, sh - 32), 2, border_radius=4)
		pygame.draw.rect(self.screen, (60, 45, 15),
		                 (20, 20, sw - 40, sh - 40), 1, border_radius=4)

	def _draw_title(self):
		sw, sh = self.screen.get_size()

		# Titolo principale
		title = self.font_title.render('THE LEGEND OF', True, (200, 170, 60))
		self.screen.blit(title, title.get_rect(centerx=sw // 2, y=sh // 5))

		title2 = self.font_title.render('ZEDDA', True, (240, 210, 80))
		self.screen.blit(title2, title2.get_rect(centerx=sw // 2, y=sh // 5 + 58))

		# Sottotitolo
		sub = self.font_sub.render(
			f'Un\'avventura nel villaggio di {STARTING_VILLAGE}', True, (120, 100, 50))
		self.screen.blit(sub, sub.get_rect(centerx=sw // 2, y=sh // 5 + 116))

		# Linea separatrice
		pygame.draw.line(self.screen, (80, 60, 20),
		                 (sw // 2 - 160, sh // 5 + 138),
		                 (sw // 2 + 160, sh // 5 + 138), 1)

	def _draw_menu_items(self):
		sw, sh = self.screen.get_size()
		self._item_rects = []

		start_y = int(sh * 0.52)
		spacing = 52

		for i, item in enumerate(self.items):
			is_sel = (i == self.selected)
			y      = start_y + i * spacing

			# Sfondo voce selezionata
			if is_sel:
				bg_w = 280
				bg   = pygame.Surface((bg_w, 40), pygame.SRCALPHA)
				bg.fill((60, 45, 10, 180))
				pygame.draw.rect(bg, (140, 110, 30), (0, 0, bg_w, 40), 1, border_radius=4)
				self.screen.blit(bg, (sw // 2 - bg_w // 2, y - 8))

			# Testo voce
			color = (240, 210, 80) if is_sel else (160, 140, 80)
			surf  = self.font_item.render(item, True, color)
			rect  = surf.get_rect(centerx=sw // 2, centery=y + 12)
			self.screen.blit(surf, rect)
			self._item_rects.append(rect)

			# Cursore ► lampeggiante a sinistra
			if is_sel and self._blink:
				cur = self.font_item.render('>', True, (240, 180, 40))
				self.screen.blit(cur, (rect.left - 26, rect.top))

		# Hint tasti in basso
		hint = self.font_small.render(
			'FRECCE: naviga    INVIO: conferma    F5: salva durante il gioco',
			True, (60, 50, 25))
		self.screen.blit(hint, hint.get_rect(centerx=sw // 2, y=sh - 40))

	def draw(self):
		self._draw_background()
		self._draw_title()
		self._draw_menu_items()

	def update(self, dt):
		self._blink_t += dt
		if self._blink_t >= self._blink_ms:
			self._blink   = not self._blink
			self._blink_t = 0

	def handle_event(self, event):
		"""
		Gestisce input. Ritorna:
		  'new_game'  — Nuova Partita
		  'continue'  — Continua
		  'quit'      — Esci
		  None        — nessuna selezione
		"""
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				self.selected = (self.selected - 1) % len(self.items)
			elif event.key == pygame.K_DOWN:
				self.selected = (self.selected + 1) % len(self.items)
			elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
				return self._confirm()

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			for i, rect in enumerate(self._item_rects):
				# Allarga l'area cliccabile
				click_rect = rect.inflate(60, 20)
				if click_rect.collidepoint(event.pos):
					self.selected = i
					return self._confirm()

		if event.type == pygame.MOUSEMOTION:
			for i, rect in enumerate(self._item_rects):
				if rect.inflate(60, 20).collidepoint(event.pos):
					self.selected = i

		return None

	def _confirm(self):
		label = self.items[self.selected]
		if label == 'Nuova Partita':
			return 'new_game'
		elif label == 'Continua':
			return 'continue'
		elif label == 'Esci':
			pygame.quit()
			sys.exit()
		return None

	def run(self):
		"""Loop del menu. Ritorna 'new_game' o 'continue'."""
		clock = pygame.time.Clock()
		while True:
			dt = clock.tick(FPS)
			self.update(dt)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.VIDEORESIZE:
					pass  # la finestra è già resizable
				result = self.handle_event(event)
				if result:
					return result

			self.draw()
			pygame.display.update()