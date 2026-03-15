# code/game_over.py
import pygame
import os
import sys

class GameOver:
	def __init__(self, screen):
		self.screen = screen
		self.width  = screen.get_width()
		self.height = screen.get_height()

		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		self.font_title  = pygame.font.Font(font_path, 64)
		self.font_medium = pygame.font.Font(font_path, 22)
		self.font_small  = pygame.font.Font(font_path, 14)

		self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
		self.overlay.fill((0, 0, 0, 210))

		self.blink_timer    = 0
		self.blink_visible  = True
		self.blink_on_ms    = 1800   # ms visibile
		self.blink_off_ms   = 400    # ms nascosta
		self._sound_played  = False

		# Controlla se esiste un salvataggio
		try:
			import save_manager
			self._has_save = save_manager.exists()
		except Exception:
			self._has_save = False

	def run(self):
		"""
		Mostra la schermata Game Over.
		Ritorna: 'restart' | 'menu' | 'quit'
		"""
		clock = pygame.time.Clock()

		while True:
			dt = clock.tick(60)

			if not self._sound_played:
				try:
					import sound_manager
					sound_manager.play('game_over', volume=1.0)
				except Exception:
					pass
				self._sound_played = True

			self.blink_timer += dt
			threshold = self.blink_on_ms if self.blink_visible else self.blink_off_ms
			if self.blink_timer >= threshold:
				self.blink_timer   = 0
				self.blink_visible = not self.blink_visible

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_r:
						return 'restart'
					if event.key == pygame.K_l and self._has_save:
						return 'load'
					if event.key == pygame.K_m:
						return 'menu'
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()

			self.screen.blit(self.overlay, (0, 0))

			# GAME OVER
			title = self.font_title.render('GAME OVER', True, '#c0392b')
			self.screen.blit(title, title.get_rect(
				center=(self.width // 2, self.height // 2 - 90)))

			# Sottotitolo
			sub = self.font_medium.render('Sei caduto in battaglia...', True, '#aaaaaa')
			self.screen.blit(sub, sub.get_rect(
				center=(self.width // 2, self.height // 2 - 10)))

			# Tasti lampeggianti
			if self.blink_visible:
				hints = [
					('R - Riprova dall\'inizio', '#f0d080'),
				]
				if self._has_save:
					hints.append(('L - Carica ultimo salvataggio', '#a0d080'))
				hints.append(('M - Menu principale', '#aaaaaa'))
				hints.append(('ESC - Esci dal gioco',  '#666666'))

				base_y = self.height // 2 + 55
				for i, (testo, colore) in enumerate(hints):
					surf = self.font_small.render(testo, True, colore)
					self.screen.blit(surf, surf.get_rect(
						center=(self.width // 2, base_y + i * 24)))

			pygame.display.update()