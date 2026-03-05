# core/event_bus.py

class EventBus:
	"""
	Sistema di comunicazione globale tra moduli.
	Permette ai plugin di parlare col core senza dipendenze dirette.
	
	Uso:
		from core.event_bus import event_bus
		
		# Ascolta un evento
		event_bus.on('enemy_killed', mia_funzione)
		
		# Emetti un evento
		event_bus.emit('enemy_killed', {'enemy': 'Orco', 'pos': (10, 5)})
	"""

	def __init__(self):
		self._listeners = {}   # { 'nome_evento': [callback1, callback2, ...] }

	def on(self, event: str, callback):
		"""Registra una funzione da chiamare quando l'evento viene emesso."""
		if event not in self._listeners:
			self._listeners[event] = []
		self._listeners[event].append(callback)

	def off(self, event: str, callback):
		"""Rimuove un listener da un evento."""
		if event in self._listeners:
			self._listeners[event] = [
				cb for cb in self._listeners[event] if cb != callback
			]

	def emit(self, event: str, data: dict = {}):
		"""Emette un evento e chiama tutti i listener registrati."""
		if event in self._listeners:
			for callback in self._listeners[event]:
				try:
					callback(data)
				except Exception as e:
					print(f"[EVENT BUS ERROR] Errore nel listener '{event}': {e}")

	def clear(self, event: str = None):
		"""Rimuove tutti i listener (o solo quelli di un evento specifico)."""
		if event:
			self._listeners.pop(event, None)
		else:
			self._listeners.clear()


# Istanza globale — tutti i moduli importano questa
event_bus = EventBus()