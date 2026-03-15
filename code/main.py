# code/main.py
import sys
import os

# Percorsi assoluti — funzionano indipendentemente da dove si lancia lo script
_code_dir    = os.path.dirname(os.path.abspath(__file__))
_project_dir = os.path.dirname(_code_dir)

if _code_dir    not in sys.path: sys.path.insert(0, _code_dir)
if _project_dir not in sys.path: sys.path.insert(0, _project_dir)

import pygame
from settings import *
import save_manager
from splash_screen import SplashScreen
from character_select import CharacterSelect
from name_input import NameInput
from core.loader import load_all_plugins


class Game:
	def __init__(self, name, gender, role, screen, save_data=None):
		self.player_name = name
		self.gender      = gender
		self.role        = role
		self.screen      = screen
		pygame.display.set_caption(TITLE)
		self.clock       = pygame.time.Clock()
		self._save_data  = save_data   # usato solo al primo _new_level
		self._save_msg   = 0           # timer messaggio "Salvato!"
		self._new_level()

	def _new_level(self):
		from level import Level
		self.level = Level(
			'data/maps/gonnostramatza.tmx',
			self.screen,
			player_name=self.player_name,
			gender=self.gender,
			role=self.role,
			save_data=self._save_data,
		)
		self._save_data = None   # usato solo alla prima creazione

	def _on_resize(self, new_w, new_h):
		"""Aggiorna tutti i componenti che dipendono dalla dimensione della finestra."""
		self.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
		self._save_data = None
		self._new_level()

	def _draw_save_message(self):
		"""Mostra un messaggio 'Partita salvata!' in sovrimpressione."""
		font = pygame.font.SysFont('Arial', 20, bold=True)
		surf = font.render('Partita salvata!  (F5)', True, (240, 210, 80))
		bg   = pygame.Surface((surf.get_width() + 20, surf.get_height() + 12), pygame.SRCALPHA)
		bg.fill((0, 0, 0, 160))
		sw   = self.screen.get_width()
		self.screen.blit(bg,   (sw - bg.get_width() - 20, 20))
		self.screen.blit(surf, (sw - surf.get_width() - 30, 26))

	def run(self):
		from game_over import GameOver
		game_over_screen = GameOver(self.screen)

		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				# Finestra ridimensionata dall'utente
				if event.type == pygame.VIDEORESIZE:
					self._on_resize(event.w, event.h)
					game_over_screen = GameOver(self.screen)

				# F5 — salva la partita
				if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
					if self.level.save():
						self._save_msg = 2000   # mostra messaggio per 2 secondi

			self.screen.fill(WATER_COLOR)
			self.level.run(events=events)

			# Messaggio "Salvato!" temporaneo
			if self._save_msg > 0:
				self._save_msg -= self.clock.get_time()
				self._draw_save_message()

			pygame.display.update()
			self.clock.tick(FPS)

			if self.level.player.health <= 0:
				result = game_over_screen.run()
				if result == 'restart':
					self._new_level()


if __name__ == '__main__':
	pygame.init()

	# Inizializza il sistema audio
	import sound_manager
	sound_manager.init()

	# RESIZABLE permette di trascinare il bordo della finestra
	screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
	pygame.display.set_caption(TITLE)
	clock = pygame.time.Clock()

	load_all_plugins()

	logo_path = os.path.join(_project_dir, 'graphics', 'logo.jpg')
	splash = SplashScreen(screen, clock, logo_path=logo_path)
	splash.run()

	# ── Controlla se esiste un salvataggio ───────────────────────────
	if save_manager.exists():
		save_data = save_manager.load()
		if save_data:
			p = save_data['player']
			game = Game(
				name=p['name'],
				gender=p['gender'],
				role=p['role'],
				screen=screen,
				save_data=save_data,
			)
			game.run()

	# ── Nessun save — nuova partita ──────────────────────────────────
	while True:
		char_select = CharacterSelect(screen)
		gender, role = char_select.run()

		name_input = NameInput(screen, gender, role)
		name = name_input.run()

		if name:
			break

	game = Game(name, gender, role, screen)
	game.run()