# code/enemy.py
import pygame
import os
import inspect


def get_enemy_stats(name):
	"""
	Cerca le statistiche del nemico nel Registry (plugin),
	poi cade sul dizionario ENEMY_DATA come fallback.
	"""
	try:
		from core.registry import registry
		cls = registry.get('enemies', name)
		if cls is not None:
			return {
				'health':        cls.health,
				'damage':        cls.damage,
				'speed':         cls.speed,
				'aggro_radius':  cls.aggro_radius,
				'attack_radius': cls.attack_radius,
				'exp_reward':    cls.exp_reward,
				'plugin_class':  cls,   # teniamo la classe per on_death()
			}
	except Exception:
		pass

	# Fallback ai dati hardcoded
	stats = ENEMY_DATA.get(name, ENEMY_DATA['raccoon']).copy()
	stats['plugin_class'] = None
	return stats


class Enemy(pygame.sprite.Sprite):
	def __init__(self, name, pos, groups, obstacle_sprites, player):
		super().__init__(groups)

		# ── Tipo nemico ───────────────────────────────────────────────
		self.name = name

		# ── Statistiche — prima dal Registry, poi da ENEMY_DATA ────────
		stats = get_enemy_stats(name)
		self.health        = stats['health']
		self.damage        = stats['damage']
		self.speed         = stats['speed']
		self.aggro_radius  = stats['aggro_radius']
		self.attack_radius = stats['attack_radius']
		self.exp_reward    = stats['exp_reward']
		self._plugin_class = stats['plugin_class']  # None se non è un plugin

		# ── Animazioni — usa percorso plugin se disponibile ───────────
		self.animations      = self._load_animations(name, plugin_class=self._plugin_class)
		self.status          = 'idle'
		self.frame_index     = 0
		self.animation_speed = 0.12

		# ── Immagine e posizione ───────────────────────────────────────
		self.image  = self.animations[self.status][0]
		self.rect   = self.image.get_rect(center=pos)
		self.hitbox = self.rect.inflate(-16, -16)

		# ── AI ────────────────────────────────────────────────────────
		self.player           = player
		self.obstacle_sprites = obstacle_sprites
		self.can_attack       = True
		self.attack_cooldown  = 800
		self.attack_time      = 0
		self.hit_cooldown     = 400
		self.hit_time         = 0
		self.is_hit           = False

	def _load_animations(self, name, plugin_class=None):
		# Se è un nemico plugin, cerca le sprite nella cartella del contributor
		# es: plugins/example_contributor/graphics/monsters/goblin/
		if plugin_class is not None:
			# Il loader salva il percorso del contributor su ogni classe: cls._plugin_dir
			# es. .../plugins/example_contributor/
			plugin_dir = getattr(plugin_class, '_plugin_dir', None)
			if plugin_dir:
				base = os.path.join(plugin_dir, 'graphics', 'monsters', name.lower())
			else:
				# fallback al percorso globale se _plugin_dir non è impostato
				base = os.path.join(
					os.path.dirname(os.path.abspath(__file__)),
					'..', 'graphics', 'monsters', name.lower()
				)
		else:
			base = os.path.join(
				os.path.dirname(os.path.abspath(__file__)),
				'..', 'graphics', 'monsters', name.lower()
			)
		animations = {'idle': [], 'move': [], 'attack': []}
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
				animations[key] = animations.get('idle') or [pygame.Surface((64, 64))]
		return animations

	def _get_player_distance(self):
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
			if self.status == 'attack':
				self.can_attack = True
		self.image = frames[int(self.frame_index)]
		self.rect  = self.image.get_rect(center=self.hitbox.center)

		# Lampeggia quando colpito
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
		self.health -= amount
		self.is_hit   = True
		self.hit_time = pygame.time.get_ticks()
		if self.health <= 0:
			self._on_death()
			self.kill()

	def _on_death(self):
		"""
		Chiama on_death() della classe plugin se esiste,
		altrimenti emette l'evento sull'EventBus.
		In entrambi i casi emette 'enemy_killed' con la posizione.
		"""
		# Suono morte nemico
		try:
			import sound_manager
			sound_manager.play('enemy_death', volume=0.7)
		except Exception:
			pass

		# Emette sempre enemy_killed con posizione
		try:
			from core.event_bus import event_bus
			event_bus.emit('enemy_killed', {
				'name':       self.name,
				'exp_reward': self.exp_reward,
				'pos':        self.rect.center,
			})
		except Exception:
			pass

		# Se è un nemico plugin, chiama on_death() della sua classe
		if self._plugin_class is not None:
			try:
				# Crea un'istanza temporanea e inietta la posizione
				# così drop_item() può passarla nell'evento
				instance = self._plugin_class()
				instance._drop_pos = self.rect.center
				instance.on_death()
			except Exception as e:
				print(f'[ENEMY] on_death() error per {self.name}: {e}')

	def update(self, events=[]):
		direction, distance = self._get_player_distance()
		self._get_status(distance)
		self._cooldowns()
		if self.status == 'attack':
			self._attack()
		elif self.status == 'move':
			self._move(direction)
		self._animate()


# ── Statistiche hardcoded — usate come FALLBACK se il nemico
#    non è registrato in nessun plugin ────────────────────────────────────
ENEMY_DATA = {
	'raccoon': {
		'health':        100,
		'damage':        20,
		'speed':         2,
		'aggro_radius':  300,
		'attack_radius': 60,
		'exp_reward':    150,
	},
	'spirit': {
		'health':        50,
		'damage':        8,
		'speed':         4,
		'aggro_radius':  350,
		'attack_radius': 50,
		'exp_reward':    75,
	},
	'bamboo': {
		'health':        70,
		'damage':        12,
		'speed':         3,
		'aggro_radius':  250,
		'attack_radius': 55,
		'exp_reward':    105,
	},
	'squid': {
		'health':        80,
		'damage':        15,
		'speed':         2,
		'aggro_radius':  280,
		'attack_radius': 55,
		'exp_reward':    120,
	},
}