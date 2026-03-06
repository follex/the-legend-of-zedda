# code/level.py
import pygame
import os
from pytmx.util_pygame import load_pygame
from enemy import Enemy

class Level:
	def __init__(self, map_file, screen, player_name='', gender='male', role='warrior'):
		self.screen      = screen
		self.half_w      = screen.get_width()  // 2
		self.half_h      = screen.get_height() // 2
		self.player_name = player_name

		base     = os.path.dirname(os.path.abspath(__file__))
		map_path = os.path.join(base, '..', map_file)
		self.tmx_data = load_pygame(map_path)

		self.visible_sprites  = YSortCameraGroup(screen)
		self.obstacle_sprites = pygame.sprite.Group()
		self.attack_sprites   = pygame.sprite.Group()
		self.enemy_sprites    = pygame.sprite.Group()

		self._load_map()

	def _load_map(self):
		from pytmx import TiledTileLayer, TiledObjectGroup
		from player import Player
		from hud import HUD

		for layer in self.tmx_data.visible_layers:
			if not isinstance(layer, TiledTileLayer):
				continue
			for x, y, surf in layer.tiles():
				pos = (x * self.tmx_data.tilewidth,
				       y * self.tmx_data.tileheight)
				if layer.name == 'FloorLayer':
					Tile(pos, surf, [self.visible_sprites], is_floor=True)
				elif layer.name == 'BlockLayer':
					Tile(pos, surf, [self.visible_sprites, self.obstacle_sprites])

		# ── Oggetti scenici da ObjectsLayer ───────────────────────────
		for layer in self.tmx_data.visible_layers:
			if isinstance(layer, TiledObjectGroup) and layer.name == 'ObjectsLayer':
				for obj in layer:
					if obj.image:
						SceneryObject(
							pos=(obj.x, obj.y),
							surf=obj.image,
							groups=[self.visible_sprites],
							obstacle_sprites=self.obstacle_sprites
						)

		# ── Player ────────────────────────────────────────────────────
		map_w = self.tmx_data.width  * self.tmx_data.tilewidth
		map_h = self.tmx_data.height * self.tmx_data.tileheight
		self.player = Player(
			pos=(map_w // 2, map_h // 2),
			groups=[self.visible_sprites],
			obstacle_sprites=self.obstacle_sprites,
			player_name=self.player_name
		)
		self.player.attack_group = [self.visible_sprites, self.attack_sprites]

		# ── Nemici ────────────────────────────────────────────────────
		enemy_spawns = [
			# Raccoon — angoli
			('raccoon', (150,  150)),
			('raccoon', (2400, 150)),
			('raccoon', (150,  1750)),
			('raccoon', (2400, 1750)),

			# Spirit — zone intermedie
			('spirit',  (640,  480)),
			('spirit',  (1920, 480)),
			('spirit',  (640,  1440)),
			('spirit',  (1920, 1440)),

			# Bamboo — fasce laterali
			('bamboo',  (300,  900)),
			('bamboo',  (2200, 600)),
			('bamboo',  (1280, 300)),
			('bamboo',  (1280, 1600)),

			# Squid — zone centrali
			('squid',   (800,  700)),
			('squid',   (1700, 1200)),
			('squid',   (960,  1400)),
		]
		for name, pos in enemy_spawns:
			Enemy(
				name=name,
				pos=pos,
				groups=[self.visible_sprites, self.enemy_sprites],
				obstacle_sprites=self.obstacle_sprites,
				player=self.player
			)

		self.hud = HUD(self.screen, self.player)

	def _player_attack_logic(self):
		if self.player.attacking and self.player.weapon_sprite:
			for enemy in list(self.enemy_sprites):
				if enemy not in self.player.hit_this_attack:
					if self.player.weapon_sprite.rect.colliderect(enemy.hitbox):
						enemy.take_damage(self.player.attack_power)
						self.player.hit_this_attack.add(enemy)
						if not enemy.alive():
							self.player.gain_exp(enemy.exp_reward)

	def run(self, events=[]):
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update(events=events)
		self.attack_sprites.update()
		self._player_attack_logic()
		self.hud.draw()


class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups, is_floor=False):
		super().__init__(groups)
		self.image    = surf
		self.rect     = self.image.get_rect(topleft=pos)
		self.hitbox   = self.rect.inflate(0, -10)
		self.is_floor = is_floor


class SceneryObject(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups, obstacle_sprites):
		super().__init__(groups)
		self.image  = surf
		self.rect   = self.image.get_rect(topleft=pos)
		self.hitbox = pygame.Rect(
			self.rect.x + 20,
			self.rect.y + self.rect.height // 2.25,
			self.rect.width - 40,
			32
		)
		obstacle_sprites.add(self)


class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self, screen):
		super().__init__()
		self.display_surf = screen
		self.half_w = screen.get_width()  // 2
		self.half_h = screen.get_height() // 2
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player=None):
		if player:
			map_w = 40 * 64
			map_h = 30 * 64

			cam_x = player.rect.centerx - self.half_w
			cam_y = player.rect.centery  - self.half_h

			cam_x = max(0, min(cam_x, map_w - self.half_w * 2))
			cam_y = max(0, min(cam_y, map_h - self.half_h * 2))

			self.offset.x = cam_x
			self.offset.y = cam_y
		else:
			self.offset = pygame.math.Vector2(0, 0)

		for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
			if hasattr(sprite, 'is_floor') and sprite.is_floor:
				offset_pos = sprite.rect.topleft - self.offset
				self.display_surf.blit(sprite.image, offset_pos)

		for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
			if not hasattr(sprite, 'is_floor') or not sprite.is_floor:
				offset_pos = sprite.rect.topleft - self.offset
				self.display_surf.blit(sprite.image, offset_pos)