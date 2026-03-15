# code/inventory_ui.py
import pygame
import os


SLOT_SIZE    = 56    # dimensione di ogni slot in pixel
SLOT_PADDING = 8     # spazio tra slot
COLS         = 6     # colonne della griglia
ROWS         = 4     # righe della griglia


class InventoryUI:
	"""
	Schermata inventario — aperta/chiusa con il tasto I.
	Mostra una griglia COLS×ROWS con gli oggetti del player.
	Click sinistro su uno slot → lo seleziona e mostra la descrizione.
	Tasto E con slot selezionato → usa l'oggetto.
	"""

	def __init__(self, screen, player):
		self.screen   = screen
		self.player   = player
		self.visible  = False

		self._selected = None    # indice slot selezionato nella UI

		# Font
		font_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			'..', 'font', 'joystix.ttf'
		)
		try:
			self.font_title = pygame.font.Font(font_path, 18)
			self.font_body  = pygame.font.Font(font_path, 11)
			self.font_small = pygame.font.Font(font_path, 10)
		except Exception:
			self.font_title = pygame.font.SysFont('Arial', 18, bold=True)
			self.font_body  = pygame.font.SysFont('Arial', 11)
			self.font_small = pygame.font.SysFont('Arial', 10)

		# Dimensioni pannello
		self.panel_w = COLS * (SLOT_SIZE + SLOT_PADDING) + SLOT_PADDING + 220
		self.panel_h = ROWS * (SLOT_SIZE + SLOT_PADDING) + SLOT_PADDING + 80
		sw, sh = screen.get_size()
		self.panel_x = (sw - self.panel_w) // 2
		self.panel_y = (sh - self.panel_h) // 2

		# Icone placeholder cache
		self._icon_cache = {}

	# ── Apri / chiudi ─────────────────────────────────────────────────────

	def toggle(self):
		self.visible  = not self.visible
		self._selected = None

	# ── Disegna ───────────────────────────────────────────────────────────

	def draw(self):
		if not self.visible:
			return

		# Overlay scuro semi-trasparente
		overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 160))
		self.screen.blit(overlay, (0, 0))

		# Pannello principale
		panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
		panel.fill((20, 20, 35, 230))
		pygame.draw.rect(panel, (180, 160, 80), (0, 0, self.panel_w, self.panel_h), 2, border_radius=10)
		self.screen.blit(panel, (self.panel_x, self.panel_y))

		# Titolo
		title = self.font_title.render('INVENTARIO', True, (240, 210, 100))
		self.screen.blit(title, (self.panel_x + 16, self.panel_y + 14))

		# Suggerimento tasti
		hint = self.font_small.render('E: usa   I / ESC: chiudi', True, (140, 140, 140))
		self.screen.blit(hint, (self.panel_x + 16, self.panel_y + 42))

		# Griglia slot
		self._draw_grid()

		# Pannello descrizione a destra
		self._draw_description()

	def _draw_grid(self):
		grid_x = self.panel_x + SLOT_PADDING
		grid_y = self.panel_y + 68

		for i in range(ROWS * COLS):
			col = i % COLS
			row = i // COLS
			sx  = grid_x + col * (SLOT_SIZE + SLOT_PADDING)
			sy  = grid_y + row * (SLOT_SIZE + SLOT_PADDING)

			slot = self.player.inventory[i] if i < len(self.player.inventory) else None

			# Sfondo slot
			is_selected = (i == self._selected)
			is_active   = (i == self.player.selected_slot)
			if is_selected:
				bg_color = (80, 70, 30, 200)
				border_color = (240, 210, 100)
			elif is_active:
				bg_color = (30, 60, 80, 200)
				border_color = (100, 180, 240)
			else:
				bg_color = (35, 35, 55, 200)
				border_color = (80, 80, 100)

			slot_surf = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
			slot_surf.fill(bg_color)
			pygame.draw.rect(slot_surf, border_color, (0, 0, SLOT_SIZE, SLOT_SIZE), 2, border_radius=5)
			self.screen.blit(slot_surf, (sx, sy))

			if slot is not None:
				# Icona
				icon = self._get_icon(slot.item_cls)
				icon_scaled = pygame.transform.scale(icon, (SLOT_SIZE - 12, SLOT_SIZE - 12))
				self.screen.blit(icon_scaled, (sx + 6, sy + 6))

				# Quantità (in basso a destra)
				if slot.quantity > 1:
					qty = self.font_small.render(str(slot.quantity), True, (255, 255, 255))
					self.screen.blit(qty, (sx + SLOT_SIZE - qty.get_width() - 4,
					                       sy + SLOT_SIZE - qty.get_height() - 2))

			# Numero slot rapido (1–8 per i primi 8)
			if i < 8:
				num = self.font_small.render(str(i + 1), True, (120, 120, 120))
				self.screen.blit(num, (sx + 3, sy + 3))

	def _draw_description(self):
		desc_x = self.panel_x + COLS * (SLOT_SIZE + SLOT_PADDING) + SLOT_PADDING + 10
		desc_y = self.panel_y + 68
		desc_w = 200
		desc_h = self.panel_h - 90

		bg = pygame.Surface((desc_w, desc_h), pygame.SRCALPHA)
		bg.fill((15, 15, 30, 200))
		pygame.draw.rect(bg, (80, 80, 100), (0, 0, desc_w, desc_h), 1, border_radius=6)
		self.screen.blit(bg, (desc_x, desc_y))

		if self._selected is None or self._selected >= len(self.player.inventory):
			hint = self.font_small.render('Clicca uno slot', True, (100, 100, 120))
			self.screen.blit(hint, (desc_x + 10, desc_y + 10))
			return

		slot = self.player.inventory[self._selected]
		if slot is None:
			hint = self.font_small.render('Slot vuoto', True, (100, 100, 120))
			self.screen.blit(hint, (desc_x + 10, desc_y + 10))
			return

		y = desc_y + 10

		# Nome
		name_surf = self.font_body.render(slot.name, True, (240, 210, 100))
		self.screen.blit(name_surf, (desc_x + 10, y))
		y += name_surf.get_height() + 6

		# Tipo
		type_surf = self.font_small.render(f'[{slot.item_type}]', True, (160, 160, 180))
		self.screen.blit(type_surf, (desc_x + 10, y))
		y += type_surf.get_height() + 8

		# Separatore
		pygame.draw.line(self.screen, (80, 80, 100),
		                 (desc_x + 8, y), (desc_x + desc_w - 8, y))
		y += 8

		# Descrizione (a capo automatico)
		desc_text = slot.description or 'Nessuna descrizione.'
		for line in self._wrap_text(desc_text, self.font_small, desc_w - 20):
			surf = self.font_small.render(line, True, (200, 200, 210))
			self.screen.blit(surf, (desc_x + 10, y))
			y += surf.get_height() + 3

		y += 10
		# Quantità
		qty_surf = self.font_small.render(f'Quantità: {slot.quantity}', True, (160, 200, 160))
		self.screen.blit(qty_surf, (desc_x + 10, y))

		if slot.item_type == 'consumable':
			y += qty_surf.get_height() + 8
			use_surf = self.font_small.render('Premi E per usare', True, (100, 200, 100))
			self.screen.blit(use_surf, (desc_x + 10, y))

	def _get_icon(self, item_cls):
		"""Cache delle icone per evitare di ricaricare ogni frame."""
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

	def _wrap_text(self, text, font, max_width):
		"""Divide il testo in righe che non superano max_width pixel."""
		words = text.split()
		lines = []
		current = ''
		for word in words:
			test = f'{current} {word}'.strip()
			if font.size(test)[0] <= max_width:
				current = test
			else:
				if current:
					lines.append(current)
				current = word
		if current:
			lines.append(current)
		return lines

	# ── Gestione eventi ───────────────────────────────────────────────────

	def handle_event(self, event):
		"""
		Gestisce click e tasti quando l'inventario è aperto.
		Ritorna True se l'evento è stato consumato.
		"""
		if not self.visible:
			return False

		if event.type == pygame.KEYDOWN:
			if event.key in (pygame.K_i, pygame.K_ESCAPE):
				self.toggle()
				return True
			if event.key == pygame.K_e and self._selected is not None:
				self.player.use_item(self._selected)
				return True

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			slot_i = self._get_slot_at(event.pos)
			if slot_i is not None:
				self._selected = slot_i
				# Doppio click — usa l'oggetto
			return True   # assorbe il click anche se fuori dalla griglia

		return False

	def _get_slot_at(self, mouse_pos):
		"""Restituisce l'indice dello slot sotto il cursore, o None."""
		grid_x = self.panel_x + SLOT_PADDING
		grid_y = self.panel_y + 68
		mx, my = mouse_pos

		for i in range(ROWS * COLS):
			col = i % COLS
			row = i // COLS
			sx  = grid_x + col * (SLOT_SIZE + SLOT_PADDING)
			sy  = grid_y + row * (SLOT_SIZE + SLOT_PADDING)
			rect = pygame.Rect(sx, sy, SLOT_SIZE, SLOT_SIZE)
			if rect.collidepoint(mx, my):
				return i
		return None