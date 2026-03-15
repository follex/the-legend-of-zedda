# code/world_map.py
"""
Schermata Mappa del Mondo — aperta con M durante il gioco.
Mostra la cartina della Sardegna fantasy con segnaposti per ogni zona.
Il giocatore può cliccare su un segnaposto e premere INVIO per viaggiare.
"""
import pygame
import os
import sys


# ── Costanti layout ───────────────────────────────────────────────────────────
PANEL_W      = 310     # larghezza pannello info a sinistra
MAP_MARGIN_X = 20      # margine sinistro della cartina
MAP_MARGIN_Y = 20      # margine verticale della cartina
MARKER_RADIUS = 10     # raggio segnaposto normale
MARKER_RADIUS_SEL = 14 # raggio segnaposto selezionato

# Colori
C_BG         = (8,  12,  20)
C_PANEL_BG   = (15, 20,  35, 220)
C_BORDER     = (100, 80, 30)
C_BORDER2    = (60,  45, 15)
C_TITLE      = (240, 210, 80)
C_TEXT       = (200, 190, 160)
C_TEXT_DIM   = (120, 110,  80)
C_MARKER     = (220, 180,  40)
C_MARKER_SEL = (255, 220,  60)
C_MARKER_CUR = (80,  200, 120)   # verde — mappa corrente
C_MARKER_RIM = (40,   30,  10)
C_HINT       = (60,   50,  25)


class WorldMapScreen:
    """
    Schermata mappa mondo.
    zones: lista di dict con chiavi:
        name         — nome della zona
        description  — descrizione
        map_file     — percorso file .tmx
        map_position — (x, y) sull'immagine originale 1024x1536
        unlocked     — bool, se il giocatore può viaggiarci
    current_map: nome della mappa corrente
    """

    def __init__(self, screen, zones, current_map=''):
        self.screen      = screen
        self.zones       = zones
        self.current_map = current_map
        self.selected    = 0       # indice zona selezionata
        self.result      = None    # mappa scelta per il viaggio

        # Seleziona di default la mappa corrente
        for i, z in enumerate(zones):
            if z.get('map_file', '') == current_map or z.get('name', '') == current_map:
                self.selected = i
                break

        # Font
        font_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'font', 'joystix.ttf'
        )
        try:
            self.font_title  = pygame.font.Font(font_path, 18)
            self.font_body   = pygame.font.Font(font_path, 11)
            self.font_small  = pygame.font.Font(font_path, 10)
            self.font_tiny   = pygame.font.Font(font_path, 9)
        except Exception:
            self.font_title  = pygame.font.SysFont('Arial', 18, bold=True)
            self.font_body   = pygame.font.SysFont('Arial', 11)
            self.font_small  = pygame.font.SysFont('Arial', 10)
            self.font_tiny   = pygame.font.SysFont('Arial', 9)

        # Carica e scala la cartina
        self._load_map_image()

        # Animazione pulsazione segnaposto selezionato
        self._pulse_t   = 0.0
        self._pulse_val = 1.0

    def _load_map_image(self):
        """Carica World_of_Zedda.png e la scala per entrare nello schermo."""
        img_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'graphics', 'world_map', 'World_of_Zedda.png'
        )
        sw, sh = self.screen.get_size()

        if os.path.exists(img_path):
            raw = pygame.image.load(img_path).convert_alpha()
            # Calcola scala per far entrare la cartina nella parte destra
            available_h = sh - MAP_MARGIN_Y * 2
            available_w = sw - PANEL_W - MAP_MARGIN_X * 3
            scale = min(available_h / raw.get_height(),
                        available_w / raw.get_width())
            new_w = int(raw.get_width()  * scale)
            new_h = int(raw.get_height() * scale)
            self._map_img   = pygame.transform.smoothscale(raw, (new_w, new_h))
            self._map_scale = scale
        else:
            # Placeholder se manca l'immagine
            self._map_img   = pygame.Surface((400, 600), pygame.SRCALPHA)
            self._map_img.fill((20, 40, 30, 180))
            pygame.draw.rect(self._map_img, (60, 80, 50),
                             (0, 0, 400, 600), 2)
            txt = self.font_body.render('World_of_Zedda.png', True, (100, 120, 80))
            self._map_img.blit(txt, (10, 10))
            self._map_scale = 1.0

        # Posizione della cartina sullo schermo
        map_w = self._map_img.get_width()
        map_h = self._map_img.get_height()
        self._map_x = PANEL_W + MAP_MARGIN_X * 2 + (
            (sw - PANEL_W - MAP_MARGIN_X * 3 - map_w) // 2)
        self._map_y = MAP_MARGIN_Y + ((sh - MAP_MARGIN_Y * 2 - map_h) // 2)

    def _marker_screen_pos(self, zone):
        """Converte le coordinate originali della zona in coordinate schermo."""
        ox, oy = zone.get('map_position', (512, 768))
        sx = self._map_x + int(ox * self._map_scale)
        sy = self._map_y + int(oy * self._map_scale)
        return sx, sy

    def _draw_background(self):
        sw, sh = self.screen.get_size()
        self.screen.fill(C_BG)
        # Griglia decorativa
        for x in range(0, sw, 32):
            for y in range(0, sh, 32):
                pygame.draw.circle(self.screen, (18, 25, 38), (x, y), 1)
        # Bordo
        pygame.draw.rect(self.screen, C_BORDER,  (12, 12, sw-24, sh-24), 2, border_radius=4)
        pygame.draw.rect(self.screen, C_BORDER2, (16, 16, sw-32, sh-32), 1, border_radius=4)

    def _draw_panel(self):
        sw, sh = self.screen.get_size()

        # Sfondo pannello
        panel = pygame.Surface((PANEL_W - 20, sh - 40), pygame.SRCALPHA)
        panel.fill(C_PANEL_BG)
        pygame.draw.rect(panel, C_BORDER, (0, 0, PANEL_W - 20, sh - 40), 1, border_radius=6)
        self.screen.blit(panel, (20, 20))

        y = 36

        # Titolo
        title = self.font_title.render('MAPPA DEL MONDO', True, C_TITLE)
        self.screen.blit(title, (30, y))
        y += title.get_height() + 4

        pygame.draw.line(self.screen, C_BORDER,
                         (28, y), (PANEL_W - 12, y))
        y += 12

        # Info zona selezionata
        if self.zones and self.selected < len(self.zones):
            zone = self.zones[self.selected]

            # Nome zona
            name = self.font_title.render(zone.get('name', ''), True, C_TITLE)
            self.screen.blit(name, (30, y))
            y += name.get_height() + 8

            # Tag zona corrente
            is_current = self._is_current(zone)
            if is_current:
                tag = self.font_tiny.render('[ SEI QUI ]', True, C_MARKER_CUR)
                self.screen.blit(tag, (30, y))
                y += tag.get_height() + 8

            # Separatore
            pygame.draw.line(self.screen, C_BORDER2, (28, y), (PANEL_W - 12, y))
            y += 10

            # Descrizione con wrap
            desc = zone.get('description', 'Nessuna descrizione.')
            for line in self._wrap(desc, self.font_body, PANEL_W - 52):
                surf = self.font_body.render(line, True, C_TEXT)
                self.screen.blit(surf, (30, y))
                y += surf.get_height() + 3

            y += 16
            pygame.draw.line(self.screen, C_BORDER2, (28, y), (PANEL_W - 12, y))
            y += 12

            # Azione disponibile
            if not is_current and zone.get('unlocked', True):
                hint = self.font_small.render('INVIO - Viaggia qui', True, C_MARKER_SEL)
                self.screen.blit(hint, (30, y))
            elif is_current:
                hint = self.font_small.render('Sei gia\' in questa zona', True, C_TEXT_DIM)
                self.screen.blit(hint, (30, y))
            else:
                hint = self.font_small.render('Zona non ancora scoperta', True, (120, 60, 60))
                self.screen.blit(hint, (30, y))

        # Legenda in basso
        legend_y = sh - 90
        pygame.draw.line(self.screen, C_BORDER2, (28, legend_y), (PANEL_W - 12, legend_y))
        legend_y += 8

        items = [
            (C_MARKER_CUR, 'Posizione attuale'),
            (C_MARKER,     'Zona raggiungibile'),
        ]
        for color, label in items:
            pygame.draw.circle(self.screen, color, (38, legend_y + 6), 5)
            surf = self.font_tiny.render(label, True, C_TEXT_DIM)
            self.screen.blit(surf, (50, legend_y))
            legend_y += 16

        # Hint tasti — nel pannello sinistro in basso
        hint_y = sh - 165
        pygame.draw.line(self.screen, C_BORDER2, (28, hint_y), (PANEL_W - 12, hint_y))
        hint_y += 10
        hints_list = [
            ('FRECCE / CLICK', 'seleziona zona'),
            ('INVIO',          'viaggia qui'),
            ('M / ESC',        'chiudi mappa'),
        ]
        for key, desc in hints_list:
            key_surf  = self.font_body.render(key + ':',  True, C_TITLE)
            desc_surf = self.font_body.render(desc, True, C_TEXT_DIM)
            self.screen.blit(key_surf,  (30, hint_y))
            self.screen.blit(desc_surf, (30 + key_surf.get_width() + 4, hint_y))
            hint_y += key_surf.get_height() + 7

    def _draw_map(self):
        # Cartina
        self.screen.blit(self._map_img, (self._map_x, self._map_y))

        # Bordo cartina
        pygame.draw.rect(self.screen, C_BORDER,
                         (self._map_x - 2, self._map_y - 2,
                          self._map_img.get_width() + 4,
                          self._map_img.get_height() + 4), 2, border_radius=3)

    def _draw_markers(self):
        for i, zone in enumerate(self.zones):
            sx, sy = self._marker_screen_pos(zone)
            is_sel     = (i == self.selected)
            is_current = self._is_current(zone)
            unlocked   = zone.get('unlocked', True)

            if is_current:
                color = C_MARKER_CUR
            elif unlocked:
                color = C_MARKER
            else:
                color = (80, 60, 40)

            radius = MARKER_RADIUS
            # Alone pulsante solo se selezionato E non è la mappa corrente
            if is_sel and not is_current:
                pulse_r = int(radius + 6 + 4 * self._pulse_val)
                pulse_s = pygame.Surface((pulse_r*2+2, pulse_r*2+2), pygame.SRCALPHA)
                alpha   = int(120 * (1 - self._pulse_val))
                pygame.draw.circle(pulse_s, (*C_MARKER_SEL, alpha),
                                   (pulse_r+1, pulse_r+1), pulse_r)
                self.screen.blit(pulse_s, (sx - pulse_r - 1, sy - pulse_r - 1))
                radius = MARKER_RADIUS_SEL
                color  = C_MARKER_SEL
            elif is_sel and is_current:
                # Alone verde per la posizione corrente selezionata
                pulse_r = int(radius + 6 + 4 * self._pulse_val)
                pulse_s = pygame.Surface((pulse_r*2+2, pulse_r*2+2), pygame.SRCALPHA)
                alpha   = int(100 * (1 - self._pulse_val))
                pygame.draw.circle(pulse_s, (*C_MARKER_CUR, alpha),
                                   (pulse_r+1, pulse_r+1), pulse_r)
                self.screen.blit(pulse_s, (sx - pulse_r - 1, sy - pulse_r - 1))
                radius = MARKER_RADIUS_SEL

            # Cerchio esterno (bordo scuro)
            pygame.draw.circle(self.screen, C_MARKER_RIM, (sx, sy), radius + 2)
            # Cerchio principale
            pygame.draw.circle(self.screen, color, (sx, sy), radius)
            # Punto centrale
            pygame.draw.circle(self.screen, (255, 255, 255), (sx, sy), 3)

            # Nome zona sopra il marker
            name_surf = self.font_tiny.render(zone.get('name', ''), True,
                                              C_TITLE if is_sel else C_TEXT_DIM)
            self.screen.blit(name_surf, (sx - name_surf.get_width() // 2, sy - radius - 14))

    def _is_current(self, zone):
        zf = zone.get('map_file', '')
        zn = zone.get('name', '')
        return zf == self.current_map or zn == self.current_map

    def draw(self):
        self._draw_background()
        self._draw_map()
        self._draw_markers()
        self._draw_panel()

    def update(self, dt):
        self._pulse_t += dt * 0.003
        import math
        self._pulse_val = (math.sin(self._pulse_t) + 1) / 2

    def handle_event(self, event):
        """
        Ritorna:
          None         — nessuna azione
          False        — chiudi la mappa (M o ESC)
          str          — map_file della zona scelta (viaggio)
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_m, pygame.K_ESCAPE):
                return False
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.zones)
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.zones)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._travel()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click su un segnaposto
            for i, zone in enumerate(self.zones):
                sx, sy = self._marker_screen_pos(zone)
                dist = ((event.pos[0]-sx)**2 + (event.pos[1]-sy)**2) ** 0.5
                if dist <= MARKER_RADIUS_SEL + 6:
                    if self.selected == i:
                        return self._travel()
                    else:
                        self.selected = i
                        return None

        return None

    def _travel(self):
        """Avvia il viaggio verso la zona selezionata."""
        if not self.zones:
            return None
        zone = self.zones[self.selected]
        if self._is_current(zone):
            return None   # già qui
        if not zone.get('unlocked', True):
            return None   # zona bloccata
        return zone.get('map_file', '')

    def _wrap(self, text, font, max_w):
        words, lines, line = text.split(), [], ''
        for w in words:
            test = f'{line} {w}'.strip()
            if font.size(test)[0] <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    def run(self):
        """Loop autonomo. Ritorna map_file scelto o None se chiuso senza viaggiare."""
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(60)
            self.update(dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                result = self.handle_event(event)
                if result is False:
                    return None
                if isinstance(result, str) and result:
                    return result

            self.draw()
            pygame.display.update()