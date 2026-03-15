# code/castle_level.py
"""
Mappa del Castello di Casteddu — generata proceduralmente senza file TMX.
Layout: corridoio di pietra scura che porta al boss finale in cima.
"""
import pygame
import os
import random


# ── Palette colori pietra scura ───────────────────────────────────────────────
C_FLOOR_DARK   = (35,  30,  40)
C_FLOOR_MID    = (45,  38,  52)
C_FLOOR_LIGHT  = (58,  50,  65)
C_WALL_DARK    = (20,  18,  25)
C_WALL_MID     = (30,  26,  36)
C_WALL_LIGHT   = (50,  44,  58)
C_WALL_ACCENT  = (70,  60,  80)
C_TORCH_ORANGE = (200, 120,  40)
C_TORCH_YELLOW = (240, 180,  60)
C_BLOOD        = (80,   15,  15)

TILE = 64   # dimensione tile in pixel

# ── Layout castello (0=vuoto/muro, 1=pavimento, 2=muro decorato, 3=colonna) ──
# La mappa è 15 colonne x 22 righe
# Il boss sta in cima (riga 2-3, colonne 5-9)
CASTLE_LAYOUT = [
    # 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14
    [  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0 ],  # 0
    [  0, 0, 0, 0, 2, 2, 2, 2, 2, 2,  2, 0, 0, 0, 0 ],  # 1  muro nord
    [  0, 0, 0, 0, 2, 1, 1, 1, 1, 1,  2, 0, 0, 0, 0 ],  # 2  sala boss
    [  0, 0, 0, 0, 2, 1, 1, 1, 1, 1,  2, 0, 0, 0, 0 ],  # 3
    [  0, 0, 0, 0, 2, 1, 1, 1, 1, 1,  2, 0, 0, 0, 0 ],  # 4
    [  0, 0, 0, 0, 2, 2, 1, 1, 1, 2,  2, 0, 0, 0, 0 ],  # 5
    [  0, 0, 0, 0, 0, 2, 1, 1, 1, 2,  0, 0, 0, 0, 0 ],  # 6  corridoio stretto
    [  0, 0, 0, 0, 0, 2, 1, 1, 1, 2,  0, 0, 0, 0, 0 ],  # 7
    [  0, 0, 0, 2, 2, 2, 1, 1, 1, 2,  2, 2, 0, 0, 0 ],  # 8  allargamento
    [  0, 0, 0, 2, 1, 1, 1, 1, 1, 1,  1, 2, 0, 0, 0 ],  # 9
    [  0, 0, 0, 2, 1, 3, 1, 1, 1, 3,  1, 2, 0, 0, 0 ],  # 10 colonne
    [  0, 0, 0, 2, 1, 1, 1, 1, 1, 1,  1, 2, 0, 0, 0 ],  # 11
    [  0, 0, 0, 2, 2, 2, 1, 1, 1, 2,  2, 2, 0, 0, 0 ],  # 12
    [  0, 0, 0, 0, 0, 2, 1, 1, 1, 2,  0, 0, 0, 0, 0 ],  # 13 corridoio
    [  0, 0, 0, 0, 0, 2, 1, 1, 1, 2,  0, 0, 0, 0, 0 ],  # 14
    [  0, 0, 0, 2, 2, 2, 1, 1, 1, 2,  2, 2, 0, 0, 0 ],  # 15 sala centrale
    [  0, 0, 0, 2, 1, 1, 1, 1, 1, 1,  1, 2, 0, 0, 0 ],  # 16
    [  0, 0, 0, 2, 1, 3, 1, 1, 1, 3,  1, 2, 0, 0, 0 ],  # 17 colonne
    [  0, 0, 0, 2, 1, 1, 1, 1, 1, 1,  1, 2, 0, 0, 0 ],  # 18
    [  0, 0, 0, 2, 2, 2, 2, 1, 2, 2,  2, 2, 0, 0, 0 ],  # 19 entrata
    [  0, 0, 0, 0, 0, 0, 2, 1, 2, 0,  0, 0, 0, 0, 0 ],  # 20 porta
    [  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0 ],  # 21
]

MAP_COLS = len(CASTLE_LAYOUT[0])
MAP_ROWS = len(CASTLE_LAYOUT)
MAP_W    = MAP_COLS * TILE   # 960
MAP_H    = MAP_ROWS * TILE   # 1408

# Spawn player: riga 20 col 7 — cella pavimento davanti alla porta
PLAYER_SPAWN = (7 * TILE + TILE // 2, 20 * TILE + TILE // 2)   # (480, 1312)

# Spawn boss: riga 3 col 7 — sala del boss in cima
BOSS_SPAWN   = (7 * TILE + TILE // 2,  3 * TILE + TILE // 2)   # (480, 224)


class CastleTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, is_floor=False, is_wall=False):
        super().__init__(groups)
        self.image    = surf
        self.rect     = self.image.get_rect(topleft=pos)
        self.hitbox   = self.rect.inflate(0, -10) if is_floor else self.rect.copy()
        self.is_floor = is_floor
        self.is_wall  = is_wall


def _make_floor_tile(variant=0):
    """Genera un tile di pavimento in pietra scura."""
    surf = pygame.Surface((TILE, TILE))
    base = [C_FLOOR_DARK, C_FLOOR_MID, C_FLOOR_LIGHT][variant % 3]
    surf.fill(base)

    # Giunture tra tile
    line_col = tuple(max(0, c - 15) for c in base)
    pygame.draw.line(surf, line_col, (0, 0), (TILE-1, 0))
    pygame.draw.line(surf, line_col, (0, 0), (0, TILE-1))

    # Dettagli pietra
    rng = random.Random(variant * 137 + 42)
    for _ in range(3):
        x = rng.randint(4, TILE-8)
        y = rng.randint(4, TILE-8)
        w = rng.randint(4, 12)
        h = rng.randint(2, 6)
        c = tuple(min(255, c + rng.randint(-8, 8)) for c in base)
        pygame.draw.rect(surf, c, (x, y, w, h))

    return surf


def _make_wall_tile(variant=0):
    """Genera un tile di muro in pietra."""
    surf = pygame.Surface((TILE, TILE))
    base = [C_WALL_DARK, C_WALL_MID][variant % 2]
    surf.fill(base)

    # Blocchi di pietra
    rng = random.Random(variant * 97 + 13)
    for row in range(2):
        for col in range(2):
            x = col * (TILE//2) + 2
            y = row * (TILE//2) + 2
            w = TILE//2 - 4
            h = TILE//2 - 4
            c = tuple(min(255, c + rng.randint(-5, 12)) for c in base)
            pygame.draw.rect(surf, c, (x, y, w, h))
            pygame.draw.rect(surf, C_WALL_DARK, (x, y, w, h), 1)

    # Dettaglio superiore (ombra)
    pygame.draw.line(surf, C_WALL_ACCENT, (0, TILE-4), (TILE-1, TILE-4), 2)

    return surf


def _make_column_tile():
    """Genera un tile colonna."""
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))

    # Base colonna
    pygame.draw.rect(surf, C_WALL_MID,    (12, 8, 40, 48))
    pygame.draw.rect(surf, C_WALL_LIGHT,  (14, 10, 36, 44))
    pygame.draw.rect(surf, C_WALL_DARK,   (12, 8, 40, 48), 2)

    # Capitello
    pygame.draw.rect(surf, C_WALL_ACCENT, (8, 8, 48, 8))
    pygame.draw.rect(surf, C_WALL_ACCENT, (8, 50, 48, 8))

    # Ombra laterale
    pygame.draw.line(surf, C_WALL_DARK, (12, 8), (12, 56), 3)

    return surf


class CastleLevel:
    """
    Livello del castello generato proceduralmente.
    Interfaccia compatibile con Level — stessi attributi pubblici.
    """

    def __init__(self, screen, player_name='', gender='male',
                 role='warrior', save_data=None):
        self.screen      = screen
        self.player_name = player_name
        self.gender      = gender
        self.role        = role
        self.map_file    = 'data/maps/castello_casteddu.tmx'  # nome virtuale
        self.travel_to   = None

        self.visible_sprites  = YSortCameraGroup(screen)
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites   = pygame.sprite.Group()
        self.enemy_sprites    = pygame.sprite.Group()
        self.item_sprites     = pygame.sprite.Group()
        self.npc_sprites      = pygame.sprite.Group()

        self._build_map()
        self._setup_player(save_data)
        self._setup_boss()
        self._setup_ui(save_data)

        # Musica
        try:
            import sound_manager
            sound_manager.play_music('castello_casteddu', volume=0.6)
        except Exception:
            pass

    def _build_map(self):
        """Costruisce i tile del castello proceduralmente."""
        # Pre-genera i tile con varianti
        floor_tiles  = [_make_floor_tile(i) for i in range(6)]
        wall_tiles   = [_make_wall_tile(i)  for i in range(4)]
        column_tile  = _make_column_tile()

        rng = random.Random(42)

        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                cell = CASTLE_LAYOUT[row][col]
                pos  = (col * TILE, row * TILE)

                if cell == 1:
                    # Pavimento
                    variant = rng.randint(0, 5)
                    surf    = floor_tiles[variant]
                    CastleTile(pos, surf, [self.visible_sprites],
                               is_floor=True)

                elif cell == 2:
                    # Muro — prima metti pavimento sotto, poi muro sopra
                    floor_s = floor_tiles[0]
                    CastleTile(pos, floor_s, [self.visible_sprites],
                               is_floor=True)
                    variant = rng.randint(0, 3)
                    surf    = wall_tiles[variant]
                    CastleTile(pos, surf,
                               [self.visible_sprites, self.obstacle_sprites],
                               is_wall=True)

                elif cell == 3:
                    # Colonna — pavimento sotto + colonna sopra
                    floor_s = floor_tiles[0]
                    CastleTile(pos, floor_s, [self.visible_sprites],
                               is_floor=True)
                    CastleTile(pos, column_tile,
                               [self.visible_sprites, self.obstacle_sprites],
                               is_wall=True)

    def _setup_player(self, save_data):
        from player import Player
        from save_manager import apply_to_player, apply_inventory

        self.player = Player(
            pos=PLAYER_SPAWN,
            groups=[self.visible_sprites],
            obstacle_sprites=self.obstacle_sprites,
            player_name=self.player_name,
            role=self.role,
        )
        self.player.gender       = self.gender
        self.player.attack_group = [self.visible_sprites, self.attack_sprites]
        self.player.map_w        = MAP_W
        self.player.map_h        = MAP_H
        # Forza il rect del player nella posizione corretta
        self.player.rect.center  = PLAYER_SPAWN
        self.player.hitbox.center = PLAYER_SPAWN

        if save_data:
            apply_to_player(save_data, self.player)
            apply_inventory(save_data, self.player)

        # Forza sempre la posizione di spawn del castello
        # (sovrascrive la posizione salvata da Gonnostramatza)
        self.player.rect.center   = PLAYER_SPAWN
        self.player.hitbox.center = PLAYER_SPAWN

    def _setup_boss(self):
        """Spawna il boss finale."""
        from castle_boss import CastleBoss
        self.boss = CastleBoss(
            pos=BOSS_SPAWN,
            groups=[self.visible_sprites, self.enemy_sprites],
            obstacle_sprites=self.obstacle_sprites,
            player=self.player,
        )

    def _setup_ui(self, save_data):
        from hud import HUD
        from inventory_ui import InventoryUI
        from dialogue_ui import DialogueUI
        from quest import build_main_quest
        from settings import PRINCESS_NAME, CASTLE_NAME
        import save_manager

        self.hud          = HUD(self.screen, self.player)
        self.inventory_ui = InventoryUI(self.screen, self.player)
        self.dialogue_ui  = DialogueUI(self.screen)

        self.main_quest = build_main_quest(
            player_name=self.player_name,
            princess_name=PRINCESS_NAME,
            castle_name=CASTLE_NAME,
        )
        if save_data:
            save_manager.apply_quest(save_data, self.main_quest)

        self.hud.set_quest(self.main_quest)
        self.save_data = None

    def _player_attack_logic(self):
        if self.player.attacking and self.player.weapon_sprite:
            for enemy in list(self.enemy_sprites):
                if enemy not in self.player.hit_this_attack:
                    if self.player.weapon_sprite.rect.colliderect(enemy.hitbox):
                        enemy.take_damage(self.player.attack_power)
                        self.player.hit_this_attack.add(enemy)
                        if not enemy.alive():
                            self.player.gain_exp(enemy.exp_reward)
                            self._on_boss_defeated()

    def _on_boss_defeated(self):
        """Chiamato quando il boss viene sconfitto — attiva il finale."""
        self.main_quest.advance()   # completa la quest
        # Dialogo finale
        from settings import PRINCESS_NAME, PLAYER_SURNAME
        gender = getattr(self.player, 'gender', 'male')
        if gender == 'female':
            eroe = f'eroina {self.player_name} {PLAYER_SURNAME}'
        else:
            eroe = f'eroe {self.player_name} {PLAYER_SURNAME}'

        self.dialogue_ui.open([
            f'Il Guardiano di Casteddu è caduto!',
            f'La Principessa {PRINCESS_NAME} è libera grazie a te, {eroe}!',
            f'La Sardegna intera canta il tuo nome. La leggenda di Zedda '
            f'vivrà per sempre nelle storie del popolo.',
            'FINE — Grazie per aver giocato a The Legend of Zedda!',
        ])

    def _check_item_pickup(self):
        from item_drop import ItemDrop
        for drop in list(self.item_sprites):
            dist = pygame.math.Vector2(self.player.rect.center).distance_to(
                   pygame.math.Vector2(drop.rect.center))
            if dist <= ItemDrop.PICK_UP_RADIUS:
                if self.player.pick_up_item(drop.item_cls):
                    drop.kill()
                    try:
                        import sound_manager
                        sound_manager.play('pickup', volume=0.8)
                    except Exception:
                        pass

    def _open_world_map(self):
        from world_map import WorldMapScreen
        from zones import get_all_zones
        zones = get_all_zones(quest=self.main_quest)
        wm    = WorldMapScreen(self.screen, zones, current_map=self.map_file)
        return wm.run()

    def save(self):
        import save_manager
        return save_manager.save(self.player, self.main_quest, level=self)

    def run(self, events=[]):
        dt = 16

        for npc in self.npc_sprites:
            npc.check_player_proximity(self.player)

        for event in events:
            if self.dialogue_ui.visible:
                self.dialogue_ui.handle_event(event)
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                dest = self._open_world_map()
                if dest:
                    self.travel_to = dest
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                self.inventory_ui.toggle()
                continue
            if self.inventory_ui.visible:
                self.inventory_ui.handle_event(event)
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for npc in self.npc_sprites:
                    if npc.try_talk(self.dialogue_ui):
                        break

        self.dialogue_ui.update(dt)

        paused = self.dialogue_ui.visible or self.inventory_ui.visible
        if not paused:
            self.visible_sprites.update(events=events)
            self.attack_sprites.update()
            self._player_attack_logic()
            self._check_item_pickup()

        self.visible_sprites.custom_draw(self.player)

        # Disegna UI del boss se ancora vivo
        if self.boss.alive():
            self.boss._draw_boss_ui(self.screen, self.visible_sprites.offset)

        self.hud.draw()
        self.inventory_ui.draw()
        self.dialogue_ui.draw()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, screen):
        super().__init__()
        self.display_surf = screen
        self.half_w = screen.get_width()  // 2
        self.half_h = screen.get_height() // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player=None):
        if player:
            cam_x = player.rect.centerx - self.half_w
            cam_y = player.rect.centery  - self.half_h
            cam_x = max(0, min(cam_x, MAP_W - self.half_w * 2))
            cam_y = max(0, min(cam_y, MAP_H - self.half_h * 2))
            self.offset.x = cam_x
            self.offset.y = cam_y
        else:
            self.offset = pygame.math.Vector2(0, 0)

        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            if hasattr(sprite, 'is_floor') and sprite.is_floor:
                self.display_surf.blit(sprite.image,
                                       sprite.rect.topleft - self.offset)

        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            if not hasattr(sprite, 'is_floor') or not sprite.is_floor:
                self.display_surf.blit(sprite.image,
                                       sprite.rect.topleft - self.offset)