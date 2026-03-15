# code/sound_manager.py
import pygame
import os

_sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sounds')

_sounds = {}
_music_volume = 0.5
_sfx_volume   = 1.0

def _load():
	files = {
		'attack':      'attack.wav',
		'player_hit':  'player_hit.wav',
		'pickup':      'pickup.wav',
		'level_up':    'level_up.wav',
		'game_over':   'game_over.wav',
		'enemy_death': 'enemy_death.wav',
	}
	for key, filename in files.items():
		path = os.path.join(_sounds_dir, filename)
		if os.path.exists(path):
			try:
				_sounds[key] = pygame.mixer.Sound(path)
			except Exception as e:
				print(f'[SOUND] Impossibile caricare {filename}: {e}')
		else:
			print(f'[SOUND] File non trovato: {path}')

def init():
	"""Inizializza il mixer e carica i suoni. Chiamare dopo pygame.init()."""
	try:
		pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
		_load()
		print(f'[SOUND] {len(_sounds)}/6 effetti caricati.')
	except Exception as e:
		print(f'[SOUND] Errore inizializzazione mixer: {e}')

def play(name, volume=1.0):
	"""Riproduce un effetto sonoro per nome."""
	sound = _sounds.get(name)
	if sound:
		sound.set_volume(volume * _sfx_volume)
		sound.play()

def play_music(map_name, volume=None):
	"""
	Avvia la musica di sottofondo per la mappa indicata.
	Cerca sounds/<map_name>.mp3 oppure sounds/<map_name>.ogg.
	Se la stessa musica è già in riproduzione non fa nulla.
	"""
	if volume is None:
		volume = _music_volume

	# Cerca il file con estensione .mp3 o .ogg
	path = None
	for ext in ('.mp3', '.ogg', '.wav'):
		candidate = os.path.join(_sounds_dir, f'{map_name}{ext}')
		if os.path.exists(candidate):
			path = candidate
			break

	if path is None:
		print(f'[MUSIC] File non trovato per la mappa: {map_name}')
		return

	# Se è già in riproduzione non ricominciare
	try:
		if pygame.mixer.music.get_busy():
			# Controlla se è già lo stesso file
			if getattr(play_music, '_current', None) == path:
				return
		pygame.mixer.music.load(path)
		pygame.mixer.music.set_volume(volume)
		pygame.mixer.music.play(loops=-1)   # -1 = loop infinito
		play_music._current = path
		print(f'[MUSIC] Riproduco: {os.path.basename(path)}')
	except Exception as e:
		print(f'[MUSIC] Errore riproduzione {path}: {e}')

def stop_music(fadeout_ms=500):
	"""Ferma la musica con un fadeout."""
	try:
		pygame.mixer.music.fadeout(fadeout_ms)
		play_music._current = None
	except Exception:
		pass

def set_music_volume(volume):
	"""Imposta il volume della musica (0.0 – 1.0)."""
	global _music_volume
	_music_volume = max(0.0, min(1.0, volume))
	try:
		pygame.mixer.music.set_volume(_music_volume)
	except Exception:
		pass

def set_sfx_volume(volume):
	"""Imposta il volume degli effetti sonoro (0.0 – 1.0)."""
	global _sfx_volume
	_sfx_volume = max(0.0, min(1.0, volume))