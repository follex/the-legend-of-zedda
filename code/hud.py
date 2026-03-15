# code/hud.py
import pygame
import os


class HUD:
	def __init__(self, screen, player):
		self.screen = screen
		self.player = player

		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		self.font_large = pygame.font.Font(font_path, 18)
		self.font_small = pygame.font.Font(font_path, 12)
		self.font_tiny  = pygame.font.Font(font_path, 9)

		self.bar_w      = 200
		self.bar_h      = 20
		self.margin     = 20
		self.bar_border = 3

		# Cache icone inventario
		self._icon_cache = {}

	def _draw_bar(self, x, y, current, maximum, color_fill, color_bg, label):
		bg_rect = pygame.Rect(x, y, self.bar_w, self.bar_h)
		pygame.draw.rect(self.screen, color_bg, bg_rect, border_radius=4)

		if maximum > 0:
			fill_w = int((current / maximum) * self.bar_w)
			fill_w = max(0, fill_w)
			fill_rect = pygame.Rect(x, y, fill_w, self.bar_h)
			pygame.draw.rect(self.screen, color_fill, fill_rect, border_radius=4)

		pygame.draw.rect(self.screen, '#111111', bg_rect, self.bar_border, border_radius=4)

		text = f'{label}  {current}/{maximum}'
		surf = self.font_small.render(text, True, '#EEEEEE')
		self.screen.blit(surf, (x + 6, y + 3))

	def _draw_quickbar(self):
		"""
		Barra degli oggetti rapidi — 8 slot in basso al centro dello schermo.
		Slot 1–8 selezionabili con i tasti numerici, slot attivo evidenziato.
		"""
		sw, sh     = self.screen.get_size()
		slot_size  = 48
		slot_pad   = 6
		n_slots    = 8
		bar_w      = n_slots * (slot_size + slot_pad) - slot_pad
		bar_x      = (sw - bar_w) // 2
		bar_y      = sh - slot_size - 16

		# Sfondo barra
		bg = pygame.Surface((bar_w + 16, slot_size + 16), pygame.SRCALPHA)
		bg.fill((0, 0, 0, 130))
		pygame.draw.rect(bg, (100, 90, 50, 180), (0, 0, bar_w + 16, slot_size + 16), 2, border_radius=8)
		self.screen.blit(bg, (bar_x - 8, bar_y - 8))

		for i in range(n_slots):
			sx = bar_x + i * (slot_size + slot_pad)
			sy = bar_y

			slot = self.player.inventory[i] if i < len(self.player.inventory) else None
			is_active = (i == self.player.selected_slot)

			# Sfondo slot
			slot_surf = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
			if is_active:
				slot_surf.fill((80, 70, 20, 210))
				border_color = (240, 210, 80)
				border_w     = 2
			else:
				slot_surf.fill((30, 30, 50, 180))
				border_color = (70, 70, 90)
				border_w     = 1
			pygame.draw.rect(slot_surf, border_color,
			                 (0, 0, slot_size, slot_size), border_w, border_radius=5)
			self.screen.blit(slot_surf, (sx, sy))

			# Numero tasto
			num_surf = self.font_tiny.render(str(i + 1), True,
			                                 (220, 200, 80) if is_active else (100, 100, 110))
			self.screen.blit(num_surf, (sx + 3, sy + 3))

			if slot is not None:
				# Icona
				icon = self._get_icon(slot.item_cls)
				icon_s = pygame.transform.scale(icon, (slot_size - 14, slot_size - 14))
				self.screen.blit(icon_s, (sx + 7, sy + 7))

				# Quantità
				if slot.quantity > 1:
					qty = self.font_tiny.render(str(slot.quantity), True, (255, 255, 255))
					self.screen.blit(qty, (sx + slot_size - qty.get_width() - 3,
					                       sy + slot_size - qty.get_height() - 2))

	def _get_icon(self, item_cls):
		key = id(item_cls)
		if key not in self._icon_cache:
			sprite_path = getattr(item_cls, 'sprite_path', '')
			plugin_dir  = getattr(item_cls, '_plugin_dir', None)
			icon = None

			if sprite_path:
				if plugin_dir:
					full = os.path.join(plugin_dir, sprite_path)
					if os.path.exists(full):
						icon = pygame.image.load(full).convert_alpha()
				if icon is None:
					base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
					full = os.path.join(base, sprite_path)
					if os.path.exists(full):
						icon = pygame.image.load(full).convert_alpha()

			if icon is None:
				icon = self._make_placeholder_icon(item_cls)

			self._icon_cache[key] = icon
		return self._icon_cache[key]

	def _make_placeholder_icon(self, item_cls):
		surf = pygame.Surface((32, 32), pygame.SRCALPHA)
		item_type = getattr(item_cls, 'item_type', 'consumable')
		colors = {
			'consumable': (80, 200, 80, 220),
			'key':        (220, 200, 50, 220),
			'treasure':   (220, 160, 30, 220),
			'equipment':  (100, 160, 220, 220),
			'quest':      (220, 80, 80, 220),
		}
		color = colors.get(item_type, (160, 160, 160, 220))
		pygame.draw.rect(surf, color, (0, 0, 32, 32), border_radius=6)
		pygame.draw.rect(surf, (255, 255, 255, 180), (0, 0, 32, 32), 2, border_radius=6)
		name = getattr(item_cls, 'name', '?')
		try:
			font   = pygame.font.SysFont('Arial', 18, bold=True)
			letter = name[0].upper() if name else '?'
			txt    = font.render(letter, True, (255, 255, 255))
			surf.blit(txt, txt.get_rect(center=(16, 16)))
		except Exception:
			pass
		return surf

	def draw(self):
		# ── Calcola larghezza pannello in base al nome ─────────────────
		name_text = f'{self.player.player_name} Porceddu  —  Lv.{self.player.level}'
		name_w    = self.font_small.size(name_text)[0]
		panel_w   = max(260, name_w + 40)

		# ── Pannello sfondo semi-trasparente ──────────────────────────
		panel = pygame.Surface((panel_w, 110), pygame.SRCALPHA)
		panel.fill((0, 0, 0, 140))
		self.screen.blit(panel, (self.margin - 10, self.margin - 10))

		# ── Barra HP ──────────────────────────────────────────────────
		self._draw_bar(
			x=self.margin, y=self.margin,
			current=self.player.health,
			maximum=self.player.max_health,
			color_fill='#c0392b',
			color_bg='#4a0000',
			label='HP'
		)

		# ── Barra EXP ─────────────────────────────────────────────────
		self._draw_bar(
			x=self.margin, y=self.margin + 28,
			current=self.player.exp,
			maximum=self.player.exp_to_next,
			color_fill='#f0d080',
			color_bg='#4a3a00',
			label='EXP'
		)

		# ── Nome e livello ────────────────────────────────────────────
		name_surf = self.font_small.render(name_text, True, '#f0d080')
		self.screen.blit(name_surf, (self.margin, self.margin + 56))

		# ── Arma equipaggiata ─────────────────────────────────────────
		weapon_surf = self.font_small.render(
			f'Arma: {self.player.weapon}  ATK: {self.player.attack_power}', True, '#aaaaaa'
		)
		self.screen.blit(weapon_surf, (self.margin, self.margin + 74))

		# ── Barra oggetti rapidi ──────────────────────────────────────
		self._draw_quickbar()

		# ── Obiettivo quest ──────────────────────────────────────────
		if hasattr(self, 'quest') and self.quest and self.quest.is_active:
			self._draw_quest_objective()
	def set_quest(self, quest):
		"""Collega una quest all'HUD per mostrare l'obiettivo."""
		self.quest = quest

	def _draw_quest_objective(self):
		"""Mostra l'obiettivo attivo in alto a destra."""
		sw = self.screen.get_width()
		objective = self.quest.current_objective()
		if not objective:
			return

		title_surf = self.font_small.render(
			f'- {self.quest.title} -', True, '#f0d080')
		obj_surf = self.font_small.render(
			f'> {objective}', True, '#dddddd')

		panel_w = max(title_surf.get_width(), obj_surf.get_width()) + 24
		panel_h = 52
		panel_x = sw - panel_w - self.margin
		panel_y = self.margin - 10

		panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel.fill((0, 0, 0, 140))
		self.screen.blit(panel, (panel_x, panel_y))

		self.screen.blit(title_surf, (panel_x + 12, panel_y + 6))
		self.screen.blit(obj_surf,   (panel_x + 12, panel_y + 28))