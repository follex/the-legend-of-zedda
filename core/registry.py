# core/registry.py

class Registry:
	"""
	Registro centrale di tutti i contenuti caricati dai plugin.
	Il loader popola il registry all'avvio, il gioco lo consulta
	per sapere quali nemici, armi, magie, ecc. sono disponibili.
	
	Uso:
		from core.registry import registry
		
		# Recupera tutti i nemici disponibili
		nemici = registry.get_all('enemies')
		
		# Recupera un nemico specifico per nome
		orco = registry.get('enemies', 'Orco')
	"""

	def __init__(self):
		self._data = {
			'enemies':   {},
			'weapons':   {},
			'spells':    {},
			'items':     {},
			'map_zones': {},
			'ui':        {},
			'hud':       {},
		}
		self._plugin_index = {}  # tiene traccia di quale plugin ha registrato cosa

	def register(self, category: str, name: str, cls, plugin_author: str):
		"""Registra un contenuto nel registry."""
		if category not in self._data:
			print(f"[REGISTRY WARNING] Categoria sconosciuta: '{category}'")
			return False

		if name in self._data[category]:
			existing = self._plugin_index.get(f"{category}:{name}", "sconosciuto")
			print(f"[REGISTRY WARNING] '{name}' in '{category}' già registrato "
				  f"da '{existing}'. Ignorato il plugin di '{plugin_author}'.")
			return False

		self._data[category][name] = cls
		self._plugin_index[f"{category}:{name}"] = plugin_author
		return True

	def get(self, category: str, name: str):
		"""Restituisce una classe per nome e categoria. None se non trovata."""
		return self._data.get(category, {}).get(name, None)

	def get_all(self, category: str) -> dict:
		"""Restituisce tutte le classi di una categoria."""
		return self._data.get(category, {}).copy()

	def summary(self):
		"""Stampa un riepilogo di tutto ciò che è stato caricato."""
		print("\n[REGISTRY] ── Contenuti caricati ──────────────────────")
		for category, items in self._data.items():
			if items:
				nomi = ', '.join(items.keys())
				print(f"  {category:<12} ({len(items)}): {nomi}")
		print("────────────────────────────────────────────────────\n")


# Istanza globale
registry = Registry()