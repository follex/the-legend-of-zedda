# code/main.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from settings import *
from splash_screen import SplashScreen
from character_select import CharacterSelect
from name_input import NameInput
from core.loader import load_all_plugins


class Game:
	def __init__(self, name, gender, role):
		self.player_name = name
		self.gender      = gender
		self.role        = role
		self.screen      = pygame.display.set_mode((WIDTH, HEIGHT))
		pygame.display.set_caption(TITLE)
		self.clock       = pygame.time.Clock()
		self._new_level()

	def _new_level(self):
		from level import Level
		self.level = Level(
			'data/maps/gonnostramatza.tmx',
			self.screen,
			player_name=self.player_name
		)

	def run(self):
		from game_over import GameOver
		game_over_screen = GameOver(self.screen)

		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			self.screen.fill(WATER_COLOR)
			self.level.run(events=events)
			pygame.display.update()
			self.clock.tick(FPS)

			if self.level.player.health <= 0:
				result = game_over_screen.run()
				if result == 'restart':
					self._new_level()


if __name__ == '__main__':
	pygame.init()

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption(TITLE)
	clock = pygame.time.Clock()

	load_all_plugins()

	logo_path = os.path.join(os.path.dirname(__file__), '..', 'graphics', 'logo.jpg')
	splash = SplashScreen(screen, clock, logo_path=logo_path)
	splash.run()

	while True:
		char_select = CharacterSelect(screen)
		gender, role = char_select.run()

		name_input = NameInput(screen, gender, role)
		name = name_input.run()

		if name:
			break

	game = Game(name, gender, role)
	game.run()