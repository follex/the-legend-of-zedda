# core/interfaces/base_map_zone.py
from abc import ABC, abstractmethod

class BaseMapZone(ABC):
	"""
	Classe base per le zone di mappa.
	Ogni zona è un'area del mondo con la sua tilemap, nemici e oggetti.

	── Zona con file TMX (Tiled) ─────────────────────────────────────────────
	La zona più comune: il contributor crea la mappa con Tiled e la riferisce.

		class ForestaOscura(BaseMapZone):
			name             = "Foresta Oscura"
			description      = "Una foresta piena di pericoli."
			tilemap_path     = "maps/foresta_oscura.tmx"
			background_music = "foresta_oscura"   # cerca sounds/foresta_oscura.mp3
			map_position     = (320, 480)          # posizione sulla cartina mondo
			enemy_spawns     = [
				{'enemy': 'Orco', 'position': (640, 480), 'count': 3},
			]

			def on_enter(self, player): pass
			def on_exit(self, player):  pass

	── Zona procedurale (senza TMX) ──────────────────────────────────────────
	Per zone generate via codice (come il Castello di Casteddu).
	Il contributor definisce una classe Level compatibile.

		class DungeonBuio(BaseMapZone):
			name             = "Dungeon Buio"
			description      = "Profondità senza luce."
			tilemap_path     = "data/maps/dungeon_buio.tmx"  # nome virtuale
			map_position     = (400, 600)
			procedural       = True
			renderer_class   = DungeonBuioLevel   # classe Level compatibile

			def on_enter(self, player): pass
			def on_exit(self, player):  pass
	"""

	name:             str   = "Zona Sconosciuta"
	description:      str   = ""
	tilemap_path:     str   = ""        # file .tmx oppure nome virtuale
	background_music: str   = ""        # cerca sounds/<nome>.mp3
	is_interior:      bool  = False
	map_position:     tuple = None      # (x, y) sulla cartina World_of_Zedda.png
	unlocked:         bool  = True      # visibile e raggiungibile sulla mappa mondo

	# Spawn — usati dalle zone TMX
	enemy_spawns: list = []
	item_spawns:  list = []
	npc_spawns:   list = []

	# Zona procedurale — il contributor fornisce la propria classe Level
	procedural:      bool  = False
	renderer_class         = None

	@abstractmethod
	def on_enter(self, player):
		"""Chiamato quando il player entra nella zona."""
		pass

	@abstractmethod
	def on_exit(self, player):
		"""Chiamato quando il player lascia la zona."""
		pass

	def on_first_visit(self, player):
		"""Chiamato solo la prima volta che il player visita la zona."""
		pass