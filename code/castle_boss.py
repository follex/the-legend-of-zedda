# code/castle_boss.py
"""
Boss finale — Il Guardiano di Casteddu.
Stat altissime, aggro_radius grande, effetti visivi speciali.
"""
import pygame
import os
import math


BOSS_HEALTH       = 800
BOSS_DAMAGE       = 35
BOSS_SPEED        = 2.5
BOSS_AGGRO_RADIUS = 400
BOSS_ATTACK_RADIUS = 65
BOSS_EXP          = 500


class CastleBoss(pygame.sprite.Sprite):
    """Boss finale del gioco."""

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

        # ── Sprite ────────────────────────────────────────────────────
        self.image  = self._make_sprite()
        self.rect   = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-20, -20)

        # ── AI ────────────────────────────────────────────────────────
        self.status          = 'idle'
        self.can_attack      = True
        self.attack_cooldown = 1200   # ms tra un attacco e l'altro
        self.attack_time     = 0
        self.hit_cooldown    = 500
        self.hit_time        = 0
        self.is_hit          = False

        # ── Effetti visivi ────────────────────────────────────────────
        self._anim_t     = 0.0
        self._idle_bob   = 0.0
        self._base_y     = float(pos[1])
        self._aura_t     = 0.0

        # Font per nome e barra HP
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

    def _make_sprite(self):
        """Genera lo sprite del boss proceduralmente."""
        size = 96
        # Usiamo convert_alpha() invece di SRCALPHA diretto per compatibilità col Y-sort
        surf = pygame.Surface((size, size))
        surf.fill((255, 0, 255))   # magenta = colore trasparente
        surf.set_colorkey((255, 0, 255))

        # Corpo principale — figura oscura imponente
        body_color  = (40,  20,  50)
        armor_color = (60,  35,  80)
        edge_color  = (100, 60, 120)
        eye_color   = (220, 60,  60)
        rune_color  = (140, 80, 180)

        # Mantello/corpo
        pygame.draw.ellipse(surf, body_color,  (16, 28, 64, 60))
        pygame.draw.ellipse(surf, armor_color, (20, 32, 56, 52))

        # Armatura pettorale
        pygame.draw.rect(surf, armor_color, (28, 36, 40, 30), border_radius=4)
        pygame.draw.rect(surf, edge_color,  (28, 36, 40, 30), 2, border_radius=4)

        # Testa con elmo
        pygame.draw.ellipse(surf, body_color,  (22, 8,  52, 40))
        pygame.draw.ellipse(surf, armor_color, (24, 10, 48, 36))

        # Corna dell'elmo
        pygame.draw.polygon(surf, edge_color, [(24, 16), (14, 2),  (28, 20)])
        pygame.draw.polygon(surf, edge_color, [(72, 16), (82, 2),  (68, 20)])

        # Occhi che brillano rosso
        pygame.draw.ellipse(surf, eye_color, (32, 22, 12, 8))
        pygame.draw.ellipse(surf, eye_color, (52, 22, 12, 8))
        # Pupille
        pygame.draw.ellipse(surf, (255, 120, 120), (35, 24, 6, 4))
        pygame.draw.ellipse(surf, (255, 120, 120), (55, 24, 6, 4))

        # Rune sull'armatura
        for i, (rx, ry) in enumerate([(36, 42), (48, 42), (40, 52), (52, 52)]):
            pygame.draw.circle(surf, rune_color, (rx, ry), 3)
            pygame.draw.circle(surf, (200, 120, 255), (rx, ry), 1)

        # Spada/arma nella mano destra
        pygame.draw.rect(surf, (80, 70, 90),  (74, 40, 8, 36))   # lama
        pygame.draw.rect(surf, edge_color,    (74, 40, 8, 36), 1)
        pygame.draw.rect(surf, (120, 100, 60),(70, 54, 16, 6))    # guardia
        pygame.draw.rect(surf, (160, 140, 80),(76, 82, 4, 8))     # impugnatura

        # Aura oscura ai bordi (senza alpha — usiamo colorkey)
        pygame.draw.ellipse(surf, (30, 10, 40), (2, 2, size-4, size-4), 2)

        return surf

    def _get_player_distance(self):
        ev = pygame.math.Vector2(self.rect.center)
        pv = pygame.math.Vector2(self.player.rect.center)
        dist = ev.distance_to(pv)
        direction = (pv - ev).normalize() if dist > 0 else pygame.math.Vector2()
        return direction, dist

    def _move(self, direction):
        self.hitbox.x += direction.x * self.speed
        self._collision('horizontal')
        self.hitbox.y += direction.y * self.speed
        self._collision('vertical')
        self.rect.center = self.hitbox.center

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

    def _attack(self):
        if self.can_attack:
            self.player.take_damage(self.damage)
            self.can_attack  = False
            self.attack_time = pygame.time.get_ticks()
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
        self.health  -= amount
        self.is_hit   = True
        self.hit_time = pygame.time.get_ticks()
        try:
            import sound_manager
            sound_manager.play('enemy_death', volume=0.5)
        except Exception:
            pass
        if self.health <= 0:
            self.kill()

    def _draw_boss_ui(self, screen, camera_offset):
        """Disegna nome e barra HP del boss sopra di lui."""
        sx = self.rect.centerx - camera_offset.x
        sy = self.rect.top - camera_offset.y

        # Nome
        name_surf = self._font_name.render(self.name, True, (220, 60, 60))
        screen.blit(name_surf, (sx - name_surf.get_width() // 2, sy - 32))

        # Barra HP
        bar_w = 120
        bar_h = 8
        bx    = sx - bar_w // 2
        by    = sy - 18

        # Sfondo
        pygame.draw.rect(screen, (40, 10, 10), (bx, by, bar_w, bar_h), border_radius=3)
        # Riempimento
        fill_w = int((self.health / self.max_health) * bar_w)
        if fill_w > 0:
            color = (200, 40, 40) if self.health > self.max_health * 0.3 else (255, 80, 0)
            pygame.draw.rect(screen, color, (bx, by, fill_w, bar_h), border_radius=3)
        # Bordo
        pygame.draw.rect(screen, (140, 30, 30), (bx, by, bar_w, bar_h), 1, border_radius=3)

    def update(self, events=[]):
        self._anim_t += 0.05
        self._aura_t += 0.03

        direction, distance = self._get_player_distance()
        self._cooldowns()

        if distance <= self.attack_radius:
            self.status = 'attack'
            self._attack()
        elif distance <= self.aggro_radius:
            self.status = 'move'
            self._move(direction)
        else:
            self.status = 'idle'
            # Bob verticale in idle
            self._idle_bob = math.sin(self._anim_t) * 3
            self.rect.centery = int(self._base_y + self._idle_bob)

        # Lampeggio quando colpito
        if self.is_hit:
            alpha = 100 if (pygame.time.get_ticks() // 60) % 2 == 0 else 255
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)