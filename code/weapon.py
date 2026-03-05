# code/weapon.py
import pygame
import os

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'

        # Direzione del player
        direction = player.status.split('_')[0]

        # Carica l'immagine dell'arma nella direzione giusta
        base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'graphics', 'weapons',
            player.weapon
        )
        self.image = pygame.image.load(
            os.path.join(base, f'{direction}.png')
        ).convert_alpha()

        # Posiziona l'arma vicino al player in base alla direzione
        if direction == 'right':
            self.rect = self.image.get_rect(
                midleft=player.rect.midright + pygame.math.Vector2(0, 16))
        elif direction == 'left':
            self.rect = self.image.get_rect(
                midright=player.rect.midleft + pygame.math.Vector2(0, 16))
        elif direction == 'down':
            self.rect = self.image.get_rect(
                midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
        elif direction == 'up':
            self.rect = self.image.get_rect(
                midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))
        else:
            self.rect = self.image.get_rect(center=player.rect.center)