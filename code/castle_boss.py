# code/castle_boss.py
"""
Boss finale — Il Guardiano di Casteddu.
Stat altissime, aggro_radius grande, sprite animati da Golden Axe.

Struttura cartelle richiesta (relativa alla root del progetto):
  graphics/boss/
    left/          right/          up/          down/
    left_idle/     right_idle/     up_idle/     down_idle/
    left_attack/   right_attack/   up_attack/   down_attack/
    death/

Ogni cartella contiene PNG numerati: 0000.png, 0001.png, ...
"""
import pygame
import os
import math


BOSS_HEALTH        = 800
BOSS_DAMAGE        = 35
BOSS_SPEED         = 2.5
BOSS_AGGRO_RADIUS  = 400
BOSS_ATTACK_RADIUS = 65
BOSS_EXP           = 500

# Velocità animazione (frame per tick di update)
ANIM_SPEED_WALK   = 0.12
ANIM_SPEED_ATTACK = 0.18
ANIM_SPEED_DEATH  = 0.08


class CastleBoss(pygame.sprite.Sprite):
	"""Boss finale del gioco con sprite animati."""

	def __init__(self, pos, groups, obstacle_sprites, player):
		super().__init__(groups)

		self.player           = player
		self.obstacle_sprites = obstacle_sprites

		# ── Statistiche ───────────────────────────────────────────────
		self.name          = 'Guardiano di Casteddu'
		self.health        = BOSS_HEALTH
		self.max_health    = BOSS_HEALTH
		self.damage        = BOSS_DAMAGE
		self.speed         = BOSS_SPEED
		self.aggro_radius  = BOSS_AGGRO_RADIUS
		self.attack_radius = BOSS_ATTACK_RADIUS
		self.exp_reward    = BOSS_EXP

		# ── Animazioni ────────────────────────────────────────────────
		self.animations    = self._load_animations()
		self.status        = 'down_idle'
		self.facing        = 'down'       # ultima direzione affrontata
		self.frame_index   = 0.0
		self.is_dead       = False        # True: sta riproducendo animazione morte
		self._death_done   = False        # True: animazione morte completata

		# Prima immagine
		self.image  = self._current_frames()[0]
		self.rect   = self.image.get_rect(center=pos)
		self.hitbox = self.rect.inflate(-30, -20)

		# ── AI ────────────────────────────────────────────────────────
		self.can_attack      = True
		self.attack_cooldown = 1200
		self.attack_time     = 0
		self.hit_cooldown    = 500
		self.hit_time        = 0
		self.is_hit          = False

		# Posizione base per idle bob
		self._base_y = float(pos[1])
		self._anim_t = 0.0

		# ── Font barra HP ─────────────────────────────────────────────
		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		try:
			self._font_name = pygame.font.Font(font_path, 12)
			self._font_hp   = pygame.font.Font(font_path, 10)
		except Exception:
			self._font_name = pygame.font.SysFont('Arial', 12, bold=True)
			self._font_hp   = pygame.font.SysFont('Arial', 10)

	# ── Caricamento animazioni ─────────────────────────────────────────────

	def _load_animations(self):
		base = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'graphics', 'boss'
		)

		keys = [
			'up', 'down', 'left', 'right',
			'up_idle', 'down_idle', 'left_idle', 'right_idle',
			'up_attack', 'down_attack', 'left_attack', 'right_attack',
			'death',
		]
		animations = {k: [] for k in keys}

		for anim_name in animations:
			folder = os.path.join(base, anim_name)
			if not os.path.exists(folder):
				continue
			files = sorted(
				[f for f in os.listdir(folder) if f.endswith('.png')],
				key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
			)
			for f in files:
				surf = pygame.image.load(os.path.join(folder, f)).convert_alpha()
				animations[anim_name].append(surf)

		# Fallback: se una direzione manca, usa quella disponibile
		self._apply_fallbacks(animations)
		return animations

	def _apply_fallbacks(self, anims):
		"""Riempie animazioni mancanti con fallback ragionevoli."""
		# Idle = primo frame del walk corrispondente
		for d in ('up', 'down', 'left', 'right'):
			if not anims[f'{d}_idle'] and anims[d]:
				anims[f'{d}_idle'] = [anims[d][0]]

		# Direzioni mancanti: usa left specchiato per right e viceversa
		pairs = [('left', 'right'), ('up', 'down')]
		for a, b in pairs:
			for suffix in ('', '_idle', '_attack'):
				ka, kb = f'{a}{suffix}', f'{b}{suffix}'
				if anims[ka] and not anims[kb]:
					anims[kb] = [f.copy() for f in anims[ka]]
					# specchio orizzontale
					anims[kb] = [pygame.transform.flip(f, True, False) for f in anims[kb]]
				elif anims[kb] and not anims[ka]:
					anims[ka] = [pygame.transform.flip(f, True, False) for f in anims[kb]]

		# Se death è vuota, usa down come ultimo frame
		if not anims['death'] and anims['down']:
			anims['death'] = [anims['down'][-1]]

		# Ultimo fallback assoluto: superficie magenta 128x160
		fallback = pygame.Surface((128, 160), pygame.SRCALPHA)
		fallback.fill((180, 0, 180, 200))
		for k in anims:
			if not anims[k]:
				anims[k] = [fallback]

	# ── Logica animazione ──────────────────────────────────────────────────

	def _current_frames(self):
		return self.animations.get(self.status, self.animations['down_idle'])

	def _get_status(self, direction_vec, distance):
		"""Determina lo status corrente in base allo stato AI."""
		if self.is_dead:
			self.status = 'death'
			return

		# Determina facing dalla direzione di movimento
		if distance > self.attack_radius and direction_vec.length() > 0:
			if abs(direction_vec.x) >= abs(direction_vec.y):
				self.facing = 'right' if direction_vec.x > 0 else 'left'
			else:
				self.facing = 'down' if direction_vec.y > 0 else 'up'

		if distance <= self.attack_radius:
			self.status = f'{self.facing}_attack'
		elif distance <= self.aggro_radius:
			self.status = self.facing           # walk
		else:
			self.status = f'{self.facing}_idle'

	def _animate(self):
		frames = self._current_frames()
		if not frames:
			return

		if self.is_dead:
			# Animazione morte: va avanti e si ferma sull'ultimo frame
			if not self._death_done:
				self.frame_index += ANIM_SPEED_DEATH
				if self.frame_index >= len(frames):
					self.frame_index = len(frames) - 1
					self._death_done = True
		elif '_attack' in self.status:
			self.frame_index += ANIM_SPEED_ATTACK
			if self.frame_index >= len(frames):
				self.frame_index = 0.0
		else:
			self.frame_index += ANIM_SPEED_WALK
			if self.frame_index >= len(frames):
				self.frame_index = 0.0

		self.image = frames[int(self.frame_index)]
		# Mantieni il centro del rect rispetto all'hitbox
		self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)

	# ── Movimento e collisioni ────────────────────────────────────────────

	def _get_player_distance(self):
		ev   = pygame.math.Vector2(self.rect.center)
		pv   = pygame.math.Vector2(self.player.rect.center)
		dist = ev.distance_to(pv)
		direction = (pv - ev).normalize() if dist > 0 else pygame.math.Vector2()
		return direction, dist

	def _move(self, direction):
		self.hitbox.x += direction.x * self.speed
		self._collision('horizontal')
		self.hitbox.y += direction.y * self.speed
		self._collision('vertical')
		self.rect.midbottom = self.hitbox.midbottom

	def _collision(self, axis):
		for sprite in self.obstacle_sprites:
			if sprite.hitbox.colliderect(self.hitbox):
				if axis == 'horizontal':
					if self.hitbox.x > sprite.hitbox.x:
						self.hitbox.left = sprite.hitbox.right
					else:
						self.hitbox.right = sprite.hitbox.left
				else:
					if self.hitbox.y > sprite.hitbox.y:
						self.hitbox.top = sprite.hitbox.bottom
					else:
						self.hitbox.bottom = sprite.hitbox.top

	# ── Combattimento ─────────────────────────────────────────────────────

	def _attack(self):
		if self.can_attack:
			self.player.take_damage(self.damage)
			self.can_attack  = False
			self.attack_time = pygame.time.get_ticks()
			self.frame_index = 0.0   # riparte dall'inizio dell'animazione attacco
			try:
				import sound_manager
				sound_manager.play('player_hit', volume=1.0)
			except Exception:
				pass

	def _cooldowns(self):
		now = pygame.time.get_ticks()
		if not self.can_attack:
			if now - self.attack_time >= self.attack_cooldown:
				self.can_attack = True
		if self.is_hit:
			if now - self.hit_time >= self.hit_cooldown:
				self.is_hit = False

	def take_damage(self, amount):
		if self.is_dead:
			return
		self.health  -= amount
		self.is_hit   = True
		self.hit_time = pygame.time.get_ticks()
		try:
			import sound_manager
			sound_manager.play('enemy_death', volume=0.5)
		except Exception:
			pass
		if self.health <= 0:
			self.health  = 0
			self.is_dead = True
			self.frame_index = 0.0
			self.status  = 'death'
			# Non chiamare self.kill() subito: lascia finire l'animazione morte

	# ── HUD boss ──────────────────────────────────────────────────────────

	def draw_boss_ui(self, screen, camera_offset):
		"""
		Disegna nome e barra HP del boss sopra di lui.
		Va chiamato dal castle_level DOPO il draw degli sprite,
		passando lo screen e il camera_offset del YSortCameraGroup.
		"""
		if self.is_dead:
			return

		sx = self.rect.centerx - camera_offset.x
		sy = self.rect.top     - camera_offset.y

		# Nome
		name_surf = self._font_name.render(self.name, True, (220, 60, 60))
		screen.blit(name_surf, (sx - name_surf.get_width() // 2, sy - 36))

		# Barra HP
		bar_w = 140
		bar_h = 10
		bx    = sx - bar_w // 2
		by    = sy - 20

		pygame.draw.rect(screen, (40, 10, 10),   (bx, by, bar_w, bar_h), border_radius=4)
		fill_w = int((self.health / self.max_health) * bar_w)
		if fill_w > 0:
			color = (200, 40, 40) if self.health > self.max_health * 0.3 else (255, 100, 0)
			pygame.draw.rect(screen, color, (bx, by, fill_w, bar_h), border_radius=4)
		pygame.draw.rect(screen, (140, 30, 30), (bx, by, bar_w, bar_h), 1, border_radius=4)

	# ── Update principale ─────────────────────────────────────────────────

	def update(self, events=[]):
		self._anim_t += 0.05

		direction, distance = self._get_player_distance()
		self._cooldowns()

		if self.is_dead:
			self._animate()
			# Rimuovi lo sprite solo quando l'animazione di morte è finita
			if self._death_done:
				self.kill()
			return

		self._get_status(direction, distance)

		if distance <= self.attack_radius:
			self._attack()
		elif distance <= self.aggro_radius:
			self._move(direction)
		# else: idle — nessun movimento

		self._animate()

		# Lampeggio quando colpito
		if self.is_hit:
			alpha = 110 if (pygame.time.get_ticks() // 60) % 2 == 0 else 255
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)
