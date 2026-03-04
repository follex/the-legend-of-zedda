# main.py
import sys
import os

# Aggiunge sia la cartella 'code/' che la root del progetto al path
sys.path.insert(0, os.path.dirname(__file__))                        # → code/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))   # → root/

import pygame
from settings import *
from splash_screen import SplashScreen
from character_select import CharacterSelect
from name_input import NameInput
from core import load_all_plugins

class Game:
    def __init__(self, name, gender, role):
        self.player_name = name
        self.gender      = gender
        self.role        = role
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()
        print(f"Gioco avviato: {name} {PLAYER_SURNAME} | {gender} | {role}")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(WATER_COLOR)
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    pygame.init()
    load_all_plugins()                     # ← aggiungi questa riga

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()
    pygame.display.set_caption(TITLE)

    # 1. Splash screen
    splash = SplashScreen(screen, clock, logo_path='../graphics/logo.jpg')
    splash.run()

    # 2. Selezione personaggio
    while True:
        char_select = CharacterSelect(screen)
        gender, role = char_select.run()

        name_input = NameInput(screen, gender, role)
        name = name_input.run()

        if name:
            break

    # 3. Avvia il gioco
    game = Game(name, gender, role)
    game.run()