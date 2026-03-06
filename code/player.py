# code/player.py
import pygame
import os

# Dati delle armi — danno e cooldown per tipo
WEAPON_DATA = {
	'sword':  { 'damage': 25,  'cooldown': 400 },
	'axe':    { 'damage': 40,  'cooldown': 700 },
	'lance':  { 'damage': 30,  'cooldown': 500 },
	'rapier': { 'damage': 20,  'cooldown': 250 },
	'sai':    { 'damage': 15,  'cooldown': 200 },
}

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, obstacle_sprites, player_name=''):
		super().__init__(groups)

		# ── Animazioni ────────────────────────────────────────────────
		self.animations      = self._load_animations()
		self.status          = 'down_idle'
		self.frame_index     = 0
		self.animation_speed = 0.15

		# ── Immagine e posizione ───────────────────────────────────────
		self.image  = self.animations[self.status][0]
		self.rect   = self.image.get_rect(center=pos)
		self.hitbox = self.rect.inflate(-6, -26)

		# ── Movimento ─────────────────────────────────────────────────
		self.direction = pygame.math.Vector2()
		self.speed     = 5

		# ── Salute ────────────────────────────────────────────────────
		self.health     = 100
		self.max_health = 100

		# ── Esperienza e livello ──────────────────────────────────────
		self.level        = 1
		self.exp          = 0
		self.exp_to_next  = 100
		self.attack_power = 25

		# ── Identità ──────────────────────────────────────────────────
		self.player_name = player_name

		# ── Mappa ─────────────────────────────────────────────────────
		self.map_w = 40 * 64
		self.map_h = 30 * 64

		# ── Attacco ───────────────────────────────────────────────────
		self.attacking       = False
		self.attack_cooldown = 400
		self.attack_time     = 0
		self.weapon          = 'sword'
		self.weapon_sprite   = None
		self.attack_group    = None
		self.hit_this_attack = set()

		# ── Collisioni ────────────────────────────────────────────────
		self.obstacle_sprites = obstacle_sprites

	def _load_animations(self):
		base = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'graphics', 'player'
		)

		animations = {
			'up':           [], 'down':           [],
			'left':         [], 'right':          [],
			'up_idle':      [], 'down_idle':       [],
			'left_idle':    [], 'right_idle':      [],
			'up_attack':    [], 'down_attack':     [],
			'left_attack':  [], 'right_attack':    [],
		}

		for anim_name in animations:
			folder = os.path.join(base, anim_name)
			if not os.path.exists(folder):
				continue
			files = sorted(
				[f for f in os.listdir(folder) if f.endswith('.png')],
				key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
			)
			for f in files:
				path = os.path.join(folder, f)
				surf = pygame.image.load(path).convert_alpha()
				animations[anim_name].append(surf)

		for key in animations:
			if not animations[key]:
				fallback = os.path.join(base, 'down_idle', 'idle_down.png')
				if os.path.exists(fallback):
					animations[key] = [pygame.image.load(fallback).convert_alpha()]

		return animations

	def _get_status(self):
		if self.attacking:
			direction = self.status.split('_')[0]
			self.status = direction + '_attack'
			return
		base_status = self.status.replace('_idle', '').replace('_attack', '')
		if self.direction.magnitude() == 0:
			self.status = base_status + '_idle'
		else:
			self.status = base_status

	def _animate(self):
		frames = self.animations[self.status]
		self.frame_index += self.animation_speed
		if self.frame_index >= len(frames):
			self.frame_index = 0
		self.image = frames[int(self.frame_index)]
		self.rect  = self.image.get_rect(center=self.hitbox.center)

	def _input(self, events=[]):
		keys = pygame.key.get_pressed()

		if not self.attacking:
			if keys[pygame.K_UP] or keys[pygame.K_w]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_LEFT] or keys[pygame.K_a]:
				self.direction.x = -1
				self.status = 'left'
			elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				self.direction.x = 1
				self.status = 'right'
			else:
				self.direction.x = 0

		if keys[pygame.K_SPACE] and not self.attacking:
			self.attacking       = True
			self.attack_time     = pygame.time.get_ticks()
			self.direction       = pygame.math.Vector2()
			self.hit_this_attack = set()
			self._create_weapon()

		# Cambia arma con Q
		for event in events:
			if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
				self._cycle_weapon_type()

	def _cycle_weapon_type(self):
		"""Cicla tra le armi disponibili."""
		weapons = ['sword', 'axe', 'lance', 'rapier', 'sai']
		idx = weapons.index(self.weapon) if self.weapon in weapons else 0
		self.weapon = weapons[(idx + 1) % len(weapons)]

		# Aggiorna danno e cooldown in base all'arma
		data = WEAPON_DATA.get(self.weapon, WEAPON_DATA['sword'])
		self.attack_power    = data['damage']
		self.attack_cooldown = data['cooldown']

	def _create_weapon(self):
		from weapon import Weapon
		if self.attack_group is not None:
			self.weapon_sprite = Weapon(self, self.attack_group)

	def _destroy_weapon(self):
		if self.weapon_sprite:
			self.weapon_sprite.kill()
			self.weapon_sprite = None

	def _cooldown(self):
		if self.attacking:
			if pygame.time.get_ticks() - self.attack_time >= self.attack_cooldown:
				self.attacking = False
				self._destroy_weapon()

	def _move(self):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.hitbox.x += self.direction.x * self.speed
		self._collision('horizontal')
		self._check_map_bounds()

		self.hitbox.y += self.direction.y * self.speed
		self._collision('vertical')
		self._check_map_bounds()

		self.rect.center = self.hitbox.center

	def _collision(self, direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0:
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0:
						self.hitbox.left = sprite.hitbox.right

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0:
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0:
						self.hitbox.top = sprite.hitbox.bottom

	def _check_map_bounds(self):
		if self.hitbox.left   < 0:          self.hitbox.left   = 0
		if self.hitbox.right  > self.map_w: self.hitbox.right  = self.map_w
		if self.hitbox.top    < 0:          self.hitbox.top    = 0
		if self.hitbox.bottom > self.map_h: self.hitbox.bottom = self.map_h

	def take_damage(self, amount):
		self.health -= amount
		if self.health <= 0:
			self.health = 0

	def gain_exp(self, amount):
		self.exp += amount
		if self.exp >= self.exp_to_next:
			self.exp         -= self.exp_to_next
			self.level       += 1
			self.exp_to_next  = int(self.exp_to_next * 1.5)
			self.max_health  += 20
			self.health       = self.max_health
			self.attack_power += 5

	def update(self, events=[]):
		self._input(events)
		self._get_status()
		self._move()
		self._animate()
		self._cooldown()