# code/dialogue_ui.py
import pygame
import os


class DialogueUI:
	"""
	Finestra dialogo stile RPG anni 90.
	- Testo che appare lettera per lettera (effetto macchina da scrivere)
	- SPACE o clic per avanzare al prossimo messaggio
	- ESC o SPACE sull'ultimo messaggio per chiudere
	"""

	TYPEWRITER_SPEED = 40   # caratteri al secondo

	def __init__(self, screen):
		self.screen  = screen
		self.visible = False
		self.lines   = []        # lista di stringhe (pagine del dialogo)
		self._page   = 0         # pagina corrente
		self._chars  = 0.0       # caratteri mostrati finora (float per velocità)
		self._done   = False     # testo corrente completamente mostrato?
		self._on_close = None    # callback chiamata alla chiusura

		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		try:
			self.font_text = pygame.font.Font(font_path, 14)
			self.font_name = pygame.font.Font(font_path, 13)
		except Exception:
			self.font_text = pygame.font.SysFont('Arial', 14)
			self.font_name = pygame.font.SysFont('Arial', 13, bold=True)

	def open(self, lines, on_close=None):
		"""
		Apre il dialogo con una lista di messaggi.
		lines    : lista di stringhe, una per pagina
		          es. ["Ciao avventuriero!", "La principessa è in pericolo..."]
		on_close : funzione chiamata quando il dialogo si chiude
		"""
		self.lines     = lines
		self._page     = 0
		self._chars    = 0.0
		self._done     = False
		self.visible   = True
		self._on_close = on_close

	def close(self):
		self.visible = False
		self.lines   = []
		if self._on_close:
			self._on_close()
			self._on_close = None

	def handle_event(self, event):
		"""
		Gestisce input. Ritorna True se l'evento è stato consumato.
		"""
		if not self.visible:
			return False

		if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
			self._advance()
			return True

		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			self.close()
			return True

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			self._advance()
			return True

		return False

	def _advance(self):
		"""SPACE/clic: completa il testo corrente o avanza alla pagina successiva."""
		if not self._done:
			# Mostra subito tutto il testo corrente
			self._chars = float(len(self.lines[self._page]))
			self._done  = True
		else:
			# Vai alla pagina successiva
			self._page += 1
			if self._page >= len(self.lines):
				self.close()
			else:
				self._chars = 0.0
				self._done  = False

	def update(self, dt):
		"""Aggiorna l'animazione typewriter. dt in millisecondi."""
		if not self.visible or self._done:
			return
		self._chars += self.TYPEWRITER_SPEED * dt / 1000.0
		current_text = self.lines[self._page]
		if self._chars >= len(current_text):
			self._chars = float(len(current_text))
			self._done  = True

	def draw(self):
		if not self.visible or not self.lines:
			return

		sw, sh = self.screen.get_size()

		# Dimensioni e posizione finestra
		box_w = sw - 80
		box_h = 160
		box_x = 40
		box_y = sh - box_h - 30

		# Sfondo finestra
		box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
		box_surf.fill((10, 10, 25, 220))
		pygame.draw.rect(box_surf, (200, 180, 80),
		                 (0, 0, box_w, box_h), 3, border_radius=8)
		self.screen.blit(box_surf, (box_x, box_y))

		# Testo con wrap automatico
		current_text = self.lines[self._page]
		visible_text = current_text[:int(self._chars)]
		self._draw_wrapped(visible_text, box_x + 20, box_y + 20, box_w - 40)

		# Indicatore avanzamento (lampeggia quando il testo è completo)
		if self._done:
			ticks = pygame.time.get_ticks()
			if (ticks // 400) % 2 == 0:
				is_last = (self._page >= len(self.lines) - 1)
				hint = '[ ESC chiudi ]' if is_last else '[ SPACE continua ]'
				hint_surf = self.font_name.render(hint, True, (180, 160, 60))
				self.screen.blit(hint_surf, (box_x + box_w - hint_surf.get_width() - 16,
				                             box_y + box_h - hint_surf.get_height() - 10))

		# Numero pagina
		if len(self.lines) > 1:
			page_surf = self.font_name.render(
				f'{self._page + 1}/{len(self.lines)}', True, (120, 120, 120))
			self.screen.blit(page_surf, (box_x + 16, box_y + box_h - page_surf.get_height() - 10))

	def _draw_wrapped(self, text, x, y, max_width):
		"""Disegna il testo andando a capo automaticamente."""
		words   = text.split(' ')
		line    = ''
		line_y  = y
		line_h  = self.font_text.get_linesize()

		for word in words:
			test = f'{line} {word}'.strip()
			if self.font_text.size(test)[0] <= max_width:
				line = test
			else:
				if line:
					surf = self.font_text.render(line, True, (230, 230, 230))
					self.screen.blit(surf, (x, line_y))
					line_y += line_h
				line = word

		if line:
			surf = self.font_text.render(line, True, (230, 230, 230))
			self.screen.blit(surf, (x, line_y))