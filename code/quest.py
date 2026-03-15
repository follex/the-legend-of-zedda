# code/quest.py
"""
Sistema quest minimale.
Ogni quest ha un id, un titolo, una lista di step e uno stato.
"""

# Stati possibili
NOT_STARTED = 'not_started'
ACTIVE      = 'active'
COMPLETED   = 'completed'


class Quest:
	def __init__(self, quest_id, title, steps):
		"""
		quest_id : stringa univoca es. 'main_quest'
		title    : titolo breve mostrato nell'HUD
		steps    : lista di stringhe, una per ogni step dell'obiettivo
		"""
		self.quest_id     = quest_id
		self.title        = title
		self.steps        = steps
		self.current_step = 0
		self.status       = NOT_STARTED

	def start(self):
		if self.status == NOT_STARTED:
			self.status = ACTIVE

	def advance(self):
		"""Avanza al prossimo step. Se era l'ultimo, completa la quest."""
		if self.status != ACTIVE:
			return
		self.current_step += 1
		if self.current_step >= len(self.steps):
			self.status = COMPLETED

	def current_objective(self):
		"""Testo dell'obiettivo corrente da mostrare nell'HUD."""
		if self.status == NOT_STARTED:
			return ''
		if self.status == COMPLETED:
			return '✓ Quest completata!'
		if self.current_step < len(self.steps):
			return self.steps[self.current_step]
		return ''

	@property
	def is_active(self):
		return self.status == ACTIVE

	@property
	def is_completed(self):
		return self.status == COMPLETED


# ── Quest del gioco ───────────────────────────────────────────────────────────

def build_main_quest(player_name='', princess_name='Zedda', castle_name='Castello di Casteddu'):
	"""Crea e restituisce la quest principale."""
	return Quest(
		quest_id='main_quest',
		title='Salva la Principessa',
		steps=[
			f'Parla con il Vecchio Saggio a Gonnostramatza',
			f'Attraversa la foresta e raggiungi il {castle_name}',
			f'Sconfiggi il guardiano del castello',
			f'Libera la Principessa {princess_name}',
		]
	)