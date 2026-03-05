# code/player.py
import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)

        # ── Animazioni ────────────────────────────────────────────────
        self.animations = self._load_animations()
        self.status     = 'down_idle'   # animazione corrente
        self.frame_index     = 0
        self.animation_speed = 0.15

        # ── Immagine e posizione ───────────────────────────────────────
        self.image = self.animations[self.status][0]
        self.rect  = self.image.get_rect(center=pos)

        # Hitbox più stretta del tile — il player "affonda" un po'
        self.hitbox = self.rect.inflate(-6, -26)

        # ── Movimento ─────────────────────────────────────────────────
        self.direction = pygame.math.Vector2()
        self.speed     = 5

        # ── Collisioni ────────────────────────────────────────────────
        self.obstacle_sprites = obstacle_sprites

    def _load_animations(self):
        """Carica tutti i frame delle animazioni dalla cartella graphics/player/."""
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

            # Ordina i file per nome (down_0, down_1, down_2, down_3)
            files = sorted(
                [f for f in os.listdir(folder) if f.endswith('.png')],
                key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
            )

            for f in files:
                path = os.path.join(folder, f)
                surf = pygame.image.load(path).convert_alpha()
                animations[anim_name].append(surf)

        # Fallback: se una cartella era vuota usa down_idle
        for key in animations:
            if not animations[key]:
                fallback = os.path.join(base, 'down_idle', 'idle_down.png')
                if os.path.exists(fallback):
                    animations[key] = [pygame.image.load(fallback).convert_alpha()]

        return animations

    def _get_status(self):
        """Determina l'animazione corrente in base al movimento."""
        # Se fermo → idle
        if self.direction.magnitude() == 0:
            if '_idle' not in self.status and '_attack' not in self.status:
                self.status = self.status + '_idle'
        # Se in movimento → rimuovi _idle
        else:
            self.status = self.status.replace('_idle', '')

    def _animate(self):
        """Avanza il frame dell'animazione corrente."""
        frames = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[int(self.frame_index)]
        self.rect  = self.image.get_rect(center=self.hitbox.center)

    def _input(self):
        """Legge i tasti e aggiorna direzione e status."""
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
        """Muove il player con collisioni separate per X e Y."""
        # Normalizza il vettore per evitare movimento più veloce in diagonale
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Muovi X e controlla collisioni orizzontali
        self.hitbox.x += self.direction.x * self.speed
        self._collision('horizontal')

        # Muovi Y e controlla collisioni verticali
        self.hitbox.y += self.direction.y * self.speed
        self._collision('vertical')

        # Aggiorna il rect visivo dalla hitbox
        self.rect.center = self.hitbox.center

    def _collision(self, direction):
        """Risolve le collisioni con gli ostacoli."""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:   # muovo a destra
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:   # muovo a sinistra
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:   # muovo in giù
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:   # muovo in su
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self):
        self._input()
        self._get_status()
        self._move()
        self._animate()