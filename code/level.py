# code/level.py
import pygame
import os
from pytmx.util_pygame import load_pygame

class Level:
    def __init__(self, map_file, screen, player_name='', gender='male', role='warrior'):
        self.screen = screen
        self.half_w = screen.get_width()  // 2
        self.half_h = screen.get_height() // 2

        base     = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(base, '..', map_file)
        self.tmx_data = load_pygame(map_path)

        self.visible_sprites  = YSortCameraGroup(screen)
        self.obstacle_sprites = pygame.sprite.Group()

        self._load_map()

    def _load_map(self):
        from pytmx import TiledTileLayer
        from player import Player

        for layer in self.tmx_data.visible_layers:
            if not isinstance(layer, TiledTileLayer):
                continue
            for x, y, surf in layer.tiles():
                pos = (x * self.tmx_data.tilewidth,
                       y * self.tmx_data.tileheight)
                if layer.name == 'FloorLayer':
                    Tile(pos, surf, [self.visible_sprites], is_floor=True)
                elif layer.name == 'BlockLayer':
                    Tile(pos, surf, [self.visible_sprites, self.obstacle_sprites], is_floor=False)

        # Spawna il player al centro della mappa
        map_w = self.tmx_data.width  * self.tmx_data.tilewidth
        map_h = self.tmx_data.height * self.tmx_data.tileheight
        self.player = Player(
            pos=(map_w // 2, map_h // 2),
            groups=[self.visible_sprites],
            obstacle_sprites=self.obstacle_sprites
        )

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, is_floor=False):
        super().__init__(groups)
        self.image    = surf
        self.rect     = self.image.get_rect(topleft=pos)
        self.hitbox   = self.rect.inflate(0, -10)
        self.is_floor = is_floor


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, screen):
        super().__init__()
        self.display_surf = screen
        self.half_w = screen.get_width()  // 2
        self.half_h = screen.get_height() // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player=None):
        if player:
            self.offset.x = player.rect.centerx - self.half_w
            self.offset.y = player.rect.centery  - self.half_h
        else:
            self.offset = pygame.math.Vector2(0, 0)

        # Prima disegna i tile del pavimento (FloorLayer)
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            if hasattr(sprite, 'is_floor') and sprite.is_floor:
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surf.blit(sprite.image, offset_pos)

        # Poi disegna tutto il resto (player, blocchi, nemici)
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            if not hasattr(sprite, 'is_floor') or not sprite.is_floor:
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surf.blit(sprite.image, offset_pos)