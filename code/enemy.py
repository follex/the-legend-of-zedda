# code/enemy.py
import pygame
import os

class Enemy(pygame.sprite.Sprite):
	def __init__(self, name, pos, groups, obstacle_sprites, player):
		super().__init__(groups)

		# ── Tipo nemico ───────────────────────────────────────────────
		self.name = name

		# ── Animazioni ────────────────────────────────────────────────
		self.animations      = self._load_animations(name)
		self.status          = 'idle'
		self.frame_index     = 0
		self.animation_speed = 0.12

		# ── Immagine e posizione ───────────────────────────────────────
		self.image  = self.animations[self.status][0]
		self.rect   = self.image.get_rect(center=pos)
		self.hitbox = self.rect.inflate(-16, -16)

		# ── Statistiche (valori di default, override per tipo) ─────────
		self.stats = ENEMY_DATA.get(name, ENEMY_DATA['raccoon'])
		self.health      = self.stats['health']
		self.damage      = self.stats['damage']
		self.speed       = self.stats['speed']
		self.aggro_radius= self.stats['aggro_radius']
		self.attack_radius= self.stats['attack_radius']
		self.exp_reward  = self.stats['exp_reward']

		# ── AI ────────────────────────────────────────────────────────
		self.player          = player
		self.obstacle_sprites= obstacle_sprites
		self.can_attack      = True
		self.attack_cooldown = 800
		self.attack_time     = 0
		self.hit_cooldown    = 400
		self.hit_time        = 0
		self.is_hit          = False

	def _load_animations(self, name):
		base = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'graphics', 'monsters', name
		)
		animations = { 'idle': [], 'move': [], 'attack': [] }
		for anim in animations:
			folder = os.path.join(base, anim)
			if not os.path.exists(folder):
				continue
			files = sorted(
				[f for f in os.listdir(folder) if f.endswith('.png')],
				key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
			)
			for f in files:
				surf = pygame.image.load(os.path.join(folder, f)).convert_alpha()
				animations[anim].append(surf)
		# fallback
		for key in animations:
			if not animations[key]:
				animations[key] = animations.get('idle') or [pygame.Surface((64,64))]
		return animations

	def _get_player_distance(self):
		"""Restituisce vettore direzione e distanza dal player."""
		enemy_vec  = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(self.player.rect.center)
		distance   = enemy_vec.distance_to(player_vec)
		if distance > 0:
			direction = (player_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2()
		return direction, distance

	def _get_status(self, distance):
		if distance <= self.attack_radius:
			self.status = 'attack'
		elif distance <= self.aggro_radius:
			self.status = 'move'
		else:
			self.status = 'idle'

	def _animate(self):
		frames = self.animations[self.status]
		self.frame_index += self.animation_speed
		if self.frame_index >= len(frames):
			self.frame_index = 0
			# Fine animazione attacco — reset
			if self.status == 'attack':
				self.can_attack = True
		self.image = frames[int(self.frame_index)]
		self.rect  = self.image.get_rect(center=self.hitbox.center)

		# Lampeggia quando viene colpito
		if self.is_hit:
			if pygame.time.get_ticks() - self.hit_time >= self.hit_cooldown:
				self.is_hit = False
			else:
				alpha = 100 if (pygame.time.get_ticks() // 80) % 2 == 0 else 255
				self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def _move(self, direction):
		self.hitbox.x += direction.x * self.speed
		self._collision('horizontal')
		self.hitbox.y += direction.y * self.speed
		self._collision('vertical')
		self.rect.center = self.hitbox.center

	def _collision(self, direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.hitbox.x > sprite.hitbox.x:
						self.hitbox.left = sprite.hitbox.right
					else:
						self.hitbox.right = sprite.hitbox.left
		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.hitbox.y > sprite.hitbox.y:
						self.hitbox.top = sprite.hitbox.bottom
					else:
						self.hitbox.bottom = sprite.hitbox.top

	def _attack(self):
		if self.can_attack:
			self.player.take_damage(self.damage)
			self.can_attack  = False
			self.attack_time = pygame.time.get_ticks()
			self.frame_index = 0

	def _cooldowns(self):
		now = pygame.time.get_ticks()
		if not self.can_attack:
			if now - self.attack_time >= self.attack_cooldown:
				self.can_attack = True

	def take_damage(self, amount):
		"""Chiamato quando il player colpisce il nemico."""
		self.health  -= amount
		self.is_hit   = True
		self.hit_time = pygame.time.get_ticks()
		if self.health <= 0:
			self.kill()

	def update(self, events=[]):
			direction, distance = self._get_player_distance()
			self._get_status(distance)
			self._cooldowns()
			if self.status == 'attack':
				self._attack()
			elif self.status == 'move':
				self._move(direction)
			self._animate()


# ── Dati statistiche per tipo di nemico ──────────────────────────────────
ENEMY_DATA = {
	'raccoon': {
		'health':        100,
		'damage':        20,
		'speed':         2,
		'aggro_radius':  300,
		'attack_radius': 60,
		'exp_reward':    150,   # 100 * 1.5
	},
	'spirit': {
		'health':        50,
		'damage':        8,
		'speed':         4,
		'aggro_radius':  350,
		'attack_radius': 50,
		'exp_reward':    75,    # 50 * 1.5
	},
	'bamboo': {
		'health':        70,
		'damage':        12,
		'speed':         3,
		'aggro_radius':  250,
		'attack_radius': 55,
		'exp_reward':    105,   # 70 * 1.5
	},
	'squid': {
		'health':        80,
		'damage':        15,
		'speed':         2,
		'aggro_radius':  280,
		'attack_radius': 55,
		'exp_reward':    120,   # 80 * 1.5
	},
}