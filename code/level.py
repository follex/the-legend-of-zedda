# code/level.py
import pygame
from pytmx.util_pygame import load_pygame
import os

class Level:
    def __init__(self, map_file, screen):
        self.screen        = screen
        self.display_surf  = screen
        self.half_w        = screen.get_width()  // 2
        self.half_h        = screen.get_height() // 2

        # Carica la mappa TMX
        base     = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(base, '..', map_file)
        self.tmx_data = load_pygame(map_path)

        # Gruppi di sprite
        self.visible_sprites  = YSortCameraGroup(screen)
        self.obstacle_sprites = pygame.sprite.Group()

        self._load_map()

    def _load_map(self):
        """Carica tutti i layer della mappa TMX."""

        # Layer del terreno (Floor)
        for layer in self.tmx_data.visible_layers:
            from pytmx import TiledTileLayer
            if not isinstance(layer, TiledTileLayer):
                continue

            for x, y, surf in layer.tiles():
                pos  = (x * self.tmx_data.tilewidth,
                        y * self.tmx_data.tileheight)

                if layer.name == 'FloorLayer':
                    Tile(pos, surf, [self.visible_sprites])

                elif layer.name == 'BlockLayer':
                    Tile(pos, surf, [self.visible_sprites, self.obstacle_sprites])

    def run(self):
        """Aggiorna e disegna tutto."""
        self.visible_sprites.custom_draw()


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect  = self.image.get_rect(topleft=pos)
        # Hitbox leggermente ridotta rispetto al tile
        self.hitbox = self.rect.inflate(0, -10)


class YSortCameraGroup(pygame.sprite.Group):
    """
    Gruppo di sprite con camera che segue il player
    e ordinamento verticale (gli sprite più in basso
    vengono disegnati sopra quelli più in alto).
    """
    def __init__(self, screen):
        super().__init__()
        self.display_surf = screen
        self.half_w = screen.get_width()  // 2
        self.half_h = screen.get_height() // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player=None):
        # Calcola l'offset della camera centrata sul player
        if player:
            self.offset.x = player.rect.centerx - self.half_w
            self.offset.y = player.rect.centery  - self.half_h
        else:
            self.offset = pygame.math.Vector2(0, 0)

        # Disegna gli sprite ordinati per asse Y (chi è più in basso, sopra)
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surf.blit(sprite.image, offset_pos)