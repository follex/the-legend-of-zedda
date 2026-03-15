# code/level.py
import pygame
import os
from pytmx.util_pygame import load_pygame
from enemy import Enemy
from item_drop import ItemDrop
from inventory_ui import InventoryUI
from dialogue_ui import DialogueUI
from npc import NPC
from quest import build_main_quest
import save_manager
from world_map import WorldMapScreen
from zones import get_all_zones


class Level:
	def __init__(self, map_file, screen, player_name='', gender='male', role='warrior', save_data=None):
		self.screen      = screen
		self.half_w      = screen.get_width()  // 2
		self.half_h      = screen.get_height() // 2
		self.player_name = player_name
		self.role        = role
		self.map_file    = map_file
		self.travel_to   = None   # impostato quando il player vuole viaggiare
		self.gender      = gender
		self.save_data   = save_data

		base     = os.path.dirname(os.path.abspath(__file__))
		map_path = os.path.join(base, '..', map_file)
		self.tmx_data = load_pygame(map_path)

		self.visible_sprites  = YSortCameraGroup(screen)
		self.obstacle_sprites = pygame.sprite.Group()
		self.attack_sprites   = pygame.sprite.Group()
		self.enemy_sprites    = pygame.sprite.Group()
		self.item_sprites     = pygame.sprite.Group()
		self.npc_sprites      = pygame.sprite.Group()

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
			player_name=self.player_name,
			role=self.role
		)
		self.player.attack_group = [self.visible_sprites, self.attack_sprites]
		self.player.gender       = self.gender

		# ── Nemici fissi (raccoon, spirit, bamboo, squid) ─────────────
		self._spawn_base_enemies()

		# ── Nemici dai plugin (Registry) ──────────────────────────────
		self._spawn_plugin_enemies()

		self.hud = HUD(self.screen, self.player)

		# ── Inventario UI ─────────────────────────────────────────────
		self.inventory_ui = InventoryUI(self.screen, self.player)

		# ── Dialogo ───────────────────────────────────────────────────
		self.dialogue_ui = DialogueUI(self.screen)

		# ── Quest principale ──────────────────────────────────────────
		from settings import PRINCESS_NAME, CASTLE_NAME, PLAYER_SURNAME
		self.main_quest = build_main_quest(
			player_name=self.player_name,
			princess_name=PRINCESS_NAME,
			castle_name=CASTLE_NAME,
		)

		# ── Applica save se disponibile ──────────────────────────────
		if self.save_data:
			save_manager.apply_to_player(self.save_data, self.player)
			save_manager.apply_inventory(self.save_data, self.player)

		# ── NPC — Vecchio Saggio ──────────────────────────────────────
		self._spawn_npcs()

		# ── Applica stato quest dal save ─────────────────────────────
		if self.save_data:
			save_manager.apply_quest(self.save_data, self.main_quest)
			save_manager.apply_map(self.save_data, self)

		# ── Collega quest all'HUD ────────────────────────────────────
		self.hud.set_quest(self.main_quest)

		# ── Musica di sottofondo ─────────────────────────────────────
		# Il nome della musica corrisponde al nome del file mappa senza estensione
		try:
			import sound_manager
			map_name = os.path.splitext(os.path.basename(self.map_file))[0]
			sound_manager.play_music(map_name)
		except Exception as e:
			print(f'[MUSIC] {e}')

		# ── Listener drop oggetti dai nemici ─────────────────────────
		self._register_drop_listener()

		# ── Oggetti spawn — saltato se c'è un save (apply_map li ripristina) ─
		if not self.save_data:
			self._spawn_items()

	def _spawn_base_enemies(self):
		"""Spawna i nemici hardcoded già presenti nel gioco."""
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

	def _spawn_plugin_enemies(self):
		"""
		Legge tutti i nemici registrati dai plugin nel Registry
		e li spawna nella mappa in posizioni distribuite.
		Non spawna tipi già presenti in ENEMY_DATA (già gestiti da _spawn_base_enemies).
		"""
		try:
			from core.registry import registry
			from enemy import ENEMY_DATA
		except Exception as e:
			print(f'[LEVEL] Registry non disponibile: {e}')
			return

		all_enemies = registry.get_all('enemies')
		if not all_enemies:
			return

		map_w = self.tmx_data.width  * self.tmx_data.tilewidth
		map_h = self.tmx_data.height * self.tmx_data.tileheight

		# Posizioni di spawn disponibili per i plugin enemy
		# (evitano centro mappa dove spawna il player)
		import random
		spawn_positions = [
			(map_w * 0.25, map_h * 0.25),
			(map_w * 0.75, map_h * 0.25),
			(map_w * 0.25, map_h * 0.75),
			(map_w * 0.75, map_h * 0.75),
			(map_w * 0.50, map_h * 0.20),
			(map_w * 0.50, map_h * 0.80),
			(map_w * 0.15, map_h * 0.50),
			(map_w * 0.85, map_h * 0.50),
		]
		random.shuffle(spawn_positions)

		spawned = 0
		for enemy_name, enemy_cls in all_enemies.items():
			# Salta i nemici che sono già gestiti dal dizionario hardcoded
			if enemy_name.lower() in ENEMY_DATA:
				continue

			# Usa al massimo len(spawn_positions) nemici plugin
			if spawned >= len(spawn_positions):
				print(f'[LEVEL] Posizioni spawn esaurite, {enemy_name} non spawnato')
				break

			pos = spawn_positions[spawned]
			Enemy(
				name=enemy_name,
				pos=pos,
				groups=[self.visible_sprites, self.enemy_sprites],
				obstacle_sprites=self.obstacle_sprites,
				player=self.player
			)
			print(f'[LEVEL] Spawnato nemico plugin: {enemy_name} @ {pos}')
			spawned += 1

	def _player_attack_logic(self):
		if self.player.attacking and self.player.weapon_sprite:
			for enemy in list(self.enemy_sprites):
				if enemy not in self.player.hit_this_attack:
					if self.player.weapon_sprite.rect.colliderect(enemy.hitbox):
						enemy.take_damage(self.player.attack_power)
						self.player.hit_this_attack.add(enemy)
						if not enemy.alive():
							self.player.gain_exp(enemy.exp_reward)

	def _spawn_npcs(self):
		"""Spawna gli NPC nella mappa con i loro dialoghi."""
		from settings import PRINCESS_NAME, CASTLE_NAME, PLAYER_SURNAME

		def on_vecchio_saggio_talk():
			"""Chiamata quando il player parla per la prima volta con il saggio."""
			self.main_quest.start()
			self.main_quest.advance()  # avanza oltre lo step 'parla con il saggio'

		# Dialogo del Vecchio Saggio — si trova vicino al centro mappa
		map_w = self.tmx_data.width  * self.tmx_data.tilewidth
		map_h = self.tmx_data.height * self.tmx_data.tileheight
		saggio_pos = (map_w // 2 + 150, map_h // 2 - 100)

		# Forme maschili/femminili
		if self.gender == 'female':
			arriv   = 'arrivata'
			coraggi = 'coraggiosa'
			ventur  = 'avventuriera'
			solo    = 'sola'
			il_la   = 'la'
		else:
			arriv   = 'arrivato'
			coraggi = 'coraggioso'
			ventur  = 'avventuriero'
			solo    = 'solo'
			il_la   = 'il'

		# Percorso sprite Vecchio Saggio (opzionale — usa placeholder se non esiste)
		saggio_sprite = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'graphics', 'npc', 'vecchio_saggio.png'
		)

		NPC(
			name='Vecchio Saggio',
			pos=saggio_pos,
			groups=[self.visible_sprites, self.npc_sprites],
			sprite_path=saggio_sprite,
			dialogue_lines=[
				f'Finalmente sei {arriv}, {self.player_name} {PLAYER_SURNAME}!',
				f'La Principessa {PRINCESS_NAME} è stata rapita e rinchiusa '
				f'nel {CASTLE_NAME}, a nord di questa foresta.',
				f'Sei {il_la} {solo} abbastanza {coraggi} da affrontare i mostri '
				f'che presidiano il castello.',
				f'Raccogli oggetti lungo il cammino e potenzia le tue armi. '
				f'Buona fortuna, {ventur}!',
			],
			on_talk=on_vecchio_saggio_talk,
		)

	def _register_drop_listener(self):
		"""
		Ascolta l'evento 'enemy_drop_item' emesso da BaseEnemy.drop_item()
		e crea un ItemDrop nel punto in cui si trova il nemico.
		"""
		try:
			from core.event_bus import event_bus
			from core.registry import registry
		except Exception:
			return

		def on_enemy_drop(data):
			item_name = data.get('item', '')
			enemy_pos = data.get('pos', None)

			# Cerca la classe item nel registry (nome case-insensitive)
			all_items = registry.get_all('items')
			item_cls  = None
			for name, cls in all_items.items():
				if name.lower() == item_name.lower() or getattr(cls, 'name', '').lower() == item_name.lower():
					item_cls = cls
					break

			if item_cls is None:
				print(f'[DROP] Item non trovato nel registry: {item_name}')
				return

			# Posizione: usa quella passata nell'evento, altrimenti centro mappa
			pos = enemy_pos if enemy_pos else (640, 480)
			ItemDrop(item_cls, pos, [self.visible_sprites, self.item_sprites])
			print(f'[DROP] {item_name} droppato @ {pos}')

		event_bus.on('enemy_drop_item', on_enemy_drop)

	def _open_world_map(self):
		"""Apre la schermata mappa mondo. Ritorna map_file scelto o None."""
		zones = get_all_zones(quest=self.main_quest)
		wm    = WorldMapScreen(self.screen, zones, current_map=self.map_file)
		return wm.run()

	def save(self):
		"""Salva lo stato corrente del gioco."""
		return save_manager.save(self.player, self.main_quest, level=self)

	def _spawn_items(self):
		"""Spawna oggetti dai plugin nella mappa."""
		try:
			from core.registry import registry
			all_items = registry.get_all('items')
		except Exception:
			return

		if not all_items:
			return

		import random
		map_w = self.tmx_data.width  * self.tmx_data.tilewidth
		map_h = self.tmx_data.height * self.tmx_data.tileheight

		# Spawn ogni item registrato in 2-3 posizioni casuali
		for item_name, item_cls in all_items.items():
			count = getattr(item_cls, 'spawn_count', 2)
			for _ in range(count):
				pos = (
					random.randint(200, map_w - 200),
					random.randint(200, map_h - 200),
				)
				ItemDrop(item_cls, pos, [self.visible_sprites, self.item_sprites])
				print(f'[LEVEL] Spawnato item: {item_name} @ {pos}')

	def _check_item_pickup(self):
		"""Controlla se il player è abbastanza vicino a un item per raccoglierlo."""
		for drop in list(self.item_sprites):
			dist = pygame.math.Vector2(self.player.rect.center).distance_to(
				   pygame.math.Vector2(drop.rect.center))
			if dist <= ItemDrop.PICK_UP_RADIUS:
				picked = self.player.pick_up_item(drop.item_cls)
				if picked:
					drop.kill()
					try:
						import sound_manager
						sound_manager.play('pickup', volume=0.8)
					except Exception:
						pass

	def run(self, events=[]):
		dt = 16   # ~60 FPS, il clock reale è gestito da main.py

		# Controlla prossimità NPC
		for npc in self.npc_sprites:
			npc.check_player_proximity(self.player)

		# Gestione eventi
		for event in events:
			# Dialogo aperto — assorbe tutti gli input
			if self.dialogue_ui.visible:
				self.dialogue_ui.handle_event(event)
				continue

			# M — mappa mondo
			if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
				dest = self._open_world_map()
				if dest:
					self.travel_to = dest
				continue

			# I — inventario
			if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
				self.inventory_ui.toggle()
				continue
			if self.inventory_ui.visible:
				self.inventory_ui.handle_event(event)
				continue

			# SPACE vicino a un NPC — apre dialogo
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				for npc in self.npc_sprites:
					if npc.try_talk(self.dialogue_ui):
						break

		# Aggiorna typewriter dialogo
		self.dialogue_ui.update(dt)

		# Gioco in pausa se dialogo o inventario aperti
		paused = self.dialogue_ui.visible or self.inventory_ui.visible
		if not paused:
			self.visible_sprites.update(events=events)
			self.attack_sprites.update()
			self._player_attack_logic()
			self._check_item_pickup()

		self.visible_sprites.custom_draw(self.player)

		# Disegna indicatori NPC (sopra gli sprite, sotto HUD)
		for npc in self.npc_sprites:
			npc.draw_indicator(self.screen, self.visible_sprites.offset)

		self.hud.draw()
		self.inventory_ui.draw()
		self.dialogue_ui.draw()


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