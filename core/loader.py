# core/loader.py
import os
import json
import importlib.util
import inspect
from core.registry import registry
from core.interfaces import (
	BaseEnemy, BaseWeapon, BaseSpell,
	BaseItem, BaseMapZone, BaseUI, BaseHUD
)

# Mappa categoria → classe base di riferimento
CATEGORY_MAP = {
	'enemies':   BaseEnemy,
	'weapons':   BaseWeapon,
	'spells':    BaseSpell,
	'items':     BaseItem,
	'map_zones': BaseMapZone,
	'ui':        BaseUI,
	'hud':       BaseHUD,
}

REQUIRED_MANIFEST_FIELDS = ['name', 'author', 'version', 'contributes']


def load_all_plugins(plugins_dir: str = None):
	"""
	Scansiona la cartella plugins/, valida e carica tutti i plugin trovati.
	Chiamato una sola volta all'avvio del gioco.
	"""
	if plugins_dir is None:
		base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		plugins_dir = os.path.join(base, 'plugins')

	if not os.path.exists(plugins_dir):
		print("[LOADER WARNING] Cartella 'plugins/' non trovata. Nessun plugin caricato.")
		return

	print("\n[LOADER] ── Scansione plugin ───────────────────────────")

	contributors = [
		d for d in os.listdir(plugins_dir)
		if os.path.isdir(os.path.join(plugins_dir, d))
		and not d.startswith('_')
	]

	if not contributors:
		print("[LOADER] Nessun plugin trovato.")

	loaded_count  = 0
	warning_count = 0

	for contributor in sorted(contributors):
		plugin_dir    = os.path.join(plugins_dir, contributor)
		manifest_path = os.path.join(plugin_dir, 'plugin.json')

		# ── Controlla il manifest ──────────────────────────────────────
		if not os.path.exists(manifest_path):
			print(f"[PLUGIN WARNING] '{contributor}' → plugin.json mancante. Plugin ignorato.")
			warning_count += 1
			continue

		try:
			with open(manifest_path, 'r', encoding='utf-8') as f:
				manifest = json.load(f)
		except json.JSONDecodeError as e:
			print(f"[PLUGIN WARNING] '{contributor}' → plugin.json non valido: {e}. Plugin ignorato.")
			warning_count += 1
			continue

		# ── Controlla i campi obbligatori ──────────────────────────────
		missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest]
		if missing:
			print(f"[PLUGIN WARNING] '{contributor}' → campi mancanti in plugin.json: "
				  f"{', '.join(missing)}. Plugin ignorato.")
			warning_count += 1
			continue

		author = manifest['author']
		name   = manifest['name']
		print(f"[PLUGIN] Caricamento: '{name}' di {author} (v{manifest['version']})")

		contributes = manifest.get('contributes', {})

		# ── Carica ogni categoria dichiarata ──────────────────────────
		for category, files in contributes.items():

			if category not in CATEGORY_MAP:
				print(f"  [WARNING] Categoria sconosciuta: '{category}'. Ignorata.")
				warning_count += 1
				continue

			base_class = CATEGORY_MAP[category]

			for relative_path in files:
				full_path = os.path.join(plugin_dir, relative_path)

				# Controlla che il file esista
				if not os.path.exists(full_path):
					print(f"  [WARNING] File non trovato: '{relative_path}'. Ignorato.")
					warning_count += 1
					continue

				# Carica il modulo Python dinamicamente
				classes = _load_module(full_path, base_class, author)

				for cls_name, cls in classes.items():
					# Valida le animazioni dichiarate
					warning_count += _validate_animations(cls, plugin_dir, author)
					# Registra la classe nel registry
					success = registry.register(category, cls_name, cls, author)
					if success:
						loaded_count += 1
						print(f"  [OK] {category}/{cls_name}")

	print(f"\n[LOADER] Completato: {loaded_count} contenuti caricati, "
		  f"{warning_count} warning.")
	print("────────────────────────────────────────────────────\n")
	registry.summary()


def _validate_animations(cls, plugin_dir: str, author: str) -> int:
	"""
	Controlla che i file delle animazioni dichiarati esistano su disco
	e che le chiavi usate siano valide.
	Restituisce il numero di warning trovati.
	"""
	warnings   = 0
	animations = getattr(cls, 'animations', {})
	valid_keys = getattr(cls, 'VALID_ANIMATION_KEYS', set())

	for action, anim_path in animations.items():
		# Chiave non riconosciuta
		if valid_keys and action not in valid_keys:
			print(f"  [WARNING] '{cls.__name__}' → "
				  f"chiave animazione sconosciuta: '{action}'")
			warnings += 1
			continue
		# File non trovato su disco
		full = os.path.join(plugin_dir, anim_path)
		if not os.path.exists(full):
			print(f"  [WARNING] '{cls.__name__}' → "
				  f"file animazione non trovato: '{anim_path}'")
			warnings += 1

	return warnings


def _load_module(filepath: str, base_class, author: str) -> dict:
	"""
	Carica un file .py e restituisce un dizionario
	{nome_classe: classe} per ogni classe che eredita da base_class.
	"""
	classes = {}

	try:
		spec   = importlib.util.spec_from_file_location("plugin_module", filepath)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)

		for obj_name in dir(module):
			obj = getattr(module, obj_name)
			if (inspect.isclass(obj)
					and issubclass(obj, base_class)
					and obj is not base_class
					and not inspect.isabstract(obj)):
				classes[obj_name] = obj

		if not classes:
			print(f"  [WARNING] '{os.path.basename(filepath)}' → "
				  f"nessuna classe valida trovata che erediti da {base_class.__name__}.")

	except Exception as e:
		print(f"  [WARNING] Errore nel caricare '{os.path.basename(filepath)}': {e}")

	return classes