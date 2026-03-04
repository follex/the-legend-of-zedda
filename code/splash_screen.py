# splash_screen.py
import pygame
import sys

class SplashScreen:
    def __init__(self, screen, clock, logo_path='../graphics/logo.jpg'):
        self.screen = screen
        self.clock  = clock
        self.width  = screen.get_width()
        self.height = screen.get_height()

        # Carica e scala il logo
        raw = pygame.image.load(logo_path).convert()
        logo_max_w = int(self.width  * 0.75)
        logo_max_h = int(self.height * 0.75)
        raw_w, raw_h = raw.get_size()
        scale = min(logo_max_w / raw_w, logo_max_h / raw_h)
        new_size = (int(raw_w * scale), int(raw_h * scale))
        self.logo = pygame.transform.smoothscale(raw, new_size)
        self.logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 2))

        # Superficie nera per il fade
        self.overlay = pygame.Surface((self.width, self.height))
        self.overlay.fill((0, 0, 0))

        # Durate in millisecondi
        self.fade_in_ms  = 1500
        self.hold_ms     = 2000
        self.fade_out_ms = 1000

    def run(self):
        total = self.fade_in_ms + self.hold_ms + self.fade_out_ms
        start = pygame.time.get_ticks()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

            elapsed = pygame.time.get_ticks() - start

            if elapsed < self.fade_in_ms:
                alpha = 255 - int((elapsed / self.fade_in_ms) * 255)
            elif elapsed < self.fade_in_ms + self.hold_ms:
                alpha = 0
            elif elapsed < total:
                t = elapsed - self.fade_in_ms - self.hold_ms
                alpha = int((t / self.fade_out_ms) * 255)
            else:
                return

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.logo, self.logo_rect)
            self.overlay.set_alpha(alpha)
            self.screen.blit(self.overlay, (0, 0))

            pygame.display.update()
            self.clock.tick(60)