# code/player.py
import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)

        # ── Animazioni ────────────────────────────────────────────────
        self.animations = self._load_animations()
        self.status      = 'down_idle'
        self.frame_index     = 0
        self.animation_speed = 0.15

        # ── Immagine e posizione ───────────────────────────────────────
        self.image = self.animations[self.status][0]
        self.rect  = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-6, -26)

        # ── Movimento ─────────────────────────────────────────────────
        self.direction = pygame.math.Vector2()
        self.speed     = 5

        # ── Mappa ─────────────────────────────────────────────────────
        self.map_w = 40 * 64
        self.map_h = 30 * 64

        # ── Collisioni ────────────────────────────────────────────────
        self.obstacle_sprites = obstacle_sprites

    def _load_animations(self):
        base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'graphics', 'player'
        )

        animations = {
            'up':       [], 'down':       [], 'left':       [], 'right':       [],
            'up_idle':  [], 'down_idle':  [], 'left_idle':  [], 'right_idle':  [],
            'up_attack':[], 'down_attack':[], 'left_attack':[], 'right_attack':[],
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

        # Fallback se una cartella era vuota
        for key in animations:
            if not animations[key]:
                fallback = os.path.join(base, 'down_idle', 'idle_down.png')
                if os.path.exists(fallback):
                    animations[key] = [pygame.image.load(fallback).convert_alpha()]

        return animations

    def _get_status(self):
        if self.direction.magnitude() == 0:
            if '_idle' not in self.status and '_attack' not in self.status:
                self.status = self.status + '_idle'
        else:
            self.status = self.status.replace('_idle', '')

    def _animate(self):
        frames = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[int(self.frame_index)]
        self.rect  = self.image.get_rect(center=self.hitbox.center)

    def _input(self):
        keys = pygame.key.get_pressed()

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

    def _move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Muovi X e controlla collisioni
        self.hitbox.x += self.direction.x * self.speed
        self._collision('horizontal')
        self._check_map_bounds()

        # Muovi Y e controlla collisioni
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
        if self.hitbox.left < 0:
            self.hitbox.left = 0
        if self.hitbox.right > self.map_w:
            self.hitbox.right = self.map_w
        if self.hitbox.top < 0:
            self.hitbox.top = 0
        if self.hitbox.bottom > self.map_h:
            self.hitbox.bottom = self.map_h

    def update(self):
        self._input()
        self._get_status()
        self._move()
        self._animate()