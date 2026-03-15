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
		self.font_medium = pygame.font.Font(font_path, 24)
		self.font_small  = pygame.font.Font(font_path, 16)

		self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
		self.overlay.fill((0, 0, 0, 180))

		self.blink_timer    = 0
		self.blink_visible  = True
		self.blink_interval = 600
		self._sound_played  = False   # suono game over una volta sola

	def run(self):
		"""Mostra la schermata Game Over e aspetta input.
		   Restituisce 'restart' o 'quit'."""
		clock = pygame.time.Clock()

		while True:
			dt = clock.tick(60)

			# Suono game over — una volta sola all'apertura
			if not self._sound_played:
				try:
					import sound_manager
					sound_manager.play('game_over', volume=1.0)
				except Exception:
					pass
				self._sound_played = True

			self.blink_timer += dt
			if self.blink_timer >= self.blink_interval:
				self.blink_timer   = 0
				self.blink_visible = not self.blink_visible

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_r:
						return 'restart'
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()

			self.screen.blit(self.overlay, (0, 0))

			title_surf = self.font_title.render('GAME OVER', True, '#c0392b')
			title_rect = title_surf.get_rect(center=(self.width // 2, self.height // 2 - 80))
			self.screen.blit(title_surf, title_rect)

			sub_surf = self.font_medium.render('Sei caduto in battaglia...', True, '#aaaaaa')
			sub_rect = sub_surf.get_rect(center=(self.width // 2, self.height // 2))
			self.screen.blit(sub_surf, sub_rect)

			if self.blink_visible:
				blink_surf = self.font_small.render('Premi R per riprovare  |  ESC per uscire', True, '#f0d080')
				blink_rect = blink_surf.get_rect(center=(self.width // 2, self.height // 2 + 80))
				self.screen.blit(blink_surf, blink_rect)

			pygame.display.update()