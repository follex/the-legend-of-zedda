# name_input.py
import pygame
import sys
from settings import *

class NameInput:
	def __init__(self, screen, gender, role):
		self.screen  = screen
		self.gender  = gender
		self.role    = role
		self.clock   = pygame.time.Clock()

		self.font_title  = pygame.font.SysFont('georgia', 56, bold=True)
		self.font_sub    = pygame.font.SysFont('georgia', 28)
		self.font_input  = pygame.font.SysFont('georgia', 48, bold=True)
		self.font_small  = pygame.font.SysFont('georgia', 24)

		self.name         = ''
		self.max_chars    = 20
		self.cursor_vis   = True
		self.cursor_timer = 0

		self.role_descriptions = {
			'warrior': ('Guerriero', 'Forte e coraggioso, esperto nel combattimento corpo a corpo.'),
			'archer':  ('Arciere',   'Agile e preciso, colpisce i nemici da lontano con il suo arco.'),
			'mage':    ('Mago',      'Saggio e potente, padroneggia le arti arcane e la magia.'),
		}
		self.gender_label = 'Eroe' if gender == 'male' else 'Eroina'

		self.input_rect   = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 30, 440, 70)
		self.confirm_rect = None

	def draw_confirm_button(self, active):
		color_bg     = '#c8a96e' if active else '#3a3a3a'
		color_border = '#f0d080' if active else '#555555'
		color_text   = '#1a1a1a' if active else '#666666'

		label = self.font_sub.render('▶  CONFERMA', True, color_text)
		w, h  = label.get_width() + 60, label.get_height() + 24
		rect  = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 + 120, w, h)

		pygame.draw.rect(self.screen, color_bg,     rect, border_radius=10)
		pygame.draw.rect(self.screen, color_border, rect, 2, border_radius=10)
		self.screen.blit(label, label.get_rect(center=rect.center))
		self.confirm_rect = rect

	def draw(self):
		self.screen.fill('#1a1a2e')

		title = self.font_title.render('The Legend of Zedda', True, '#f0d080')
		self.screen.blit(title, title.get_rect(centerx=WIDTH // 2, y=30))

		role_name, role_desc = self.role_descriptions[self.role]
		intro_lines = [
			f'Un {self.gender_label} {role_name} parte dal villaggio di {STARTING_VILLAGE}.',
			f'{role_desc}',
			f'La sua missione: salvare la principessa {PRINCESS_NAME} dal {CASTLE_NAME}.',
		]
		for i, line in enumerate(intro_lines):
			color = '#aaaaaa' if i != 2 else '#c8a96e'
			surf  = self.font_small.render(line, True, color)
			self.screen.blit(surf, surf.get_rect(centerx=WIDTH // 2, y=120 + i * 34))

		label = self.font_sub.render(f'Come si chiama il tuo {self.gender_label}?', True, '#dddddd')
		self.screen.blit(label, label.get_rect(centerx=WIDTH // 2, y=HEIGHT // 2 - 90))

		border_color = '#f0d080' if self.name else '#555555'
		pygame.draw.rect(self.screen, '#2a2a3e', self.input_rect, border_radius=8)
		pygame.draw.rect(self.screen, border_color, self.input_rect, 2, border_radius=8)

		display_name = self.name + ('|' if self.cursor_vis else '')
		name_surf = self.font_input.render(display_name, True, '#ffffff')
		self.screen.blit(name_surf, name_surf.get_rect(center=self.input_rect.center))

		if self.name:
			full = self.font_sub.render(f'{self.name} {PLAYER_SURNAME}', True, '#f0d080')
			self.screen.blit(full, full.get_rect(centerx=WIDTH // 2, y=HEIGHT // 2 + 60))

			hint = self.font_small.render('questo sarà il nome completo del tuo personaggio', True, '#666666')
			self.screen.blit(hint, hint.get_rect(centerx=WIDTH // 2, y=HEIGHT // 2 + 96))

		self.draw_confirm_button(active=bool(self.name))

	def run(self):
		while True:
			dt = self.clock.tick(FPS)

			self.cursor_timer += dt
			if self.cursor_timer >= 500:
				self.cursor_vis   = not self.cursor_vis
				self.cursor_timer = 0

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_BACKSPACE:
						self.name = self.name[:-1]
					elif event.key == pygame.K_RETURN:
						if self.name:
							return self.name
					elif event.key == pygame.K_ESCAPE:
						return None
					else:
						if len(self.name) < self.max_chars and event.unicode.isalpha():
							if len(self.name) == 0:
								self.name += event.unicode.upper()
							else:
								self.name += event.unicode

				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					if self.confirm_rect and self.confirm_rect.collidepoint(event.pos) and self.name:
						return self.name

			self.draw()
			pygame.display.update()