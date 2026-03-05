# plugins/esempio_ufficiale/enemies/goblin.py
from core.interfaces.base_enemy import BaseEnemy

class Goblin(BaseEnemy):
	name       = "Goblin"
	health     = 60
	damage     = 15
	speed      = 3.0
	exp_reward = 20

	# Immagine statica — funziona sempre
	sprite_path = "graphics/goblin.png"

	# Animazioni — commentate per ora, pronte per essere usate
	# animations = {
	#     'idle':       "graphics/goblin_idle.png",
	#     'walk_down':  "graphics/goblin_walk_down.png",
	#     'walk_up':    "graphics/goblin_walk_up.png",
	#     'walk_left':  "graphics/goblin_walk_left.png",
	#     'walk_right': "graphics/goblin_walk_right.png",
	#     'attack':     "graphics/goblin_attack.png",
	#     'hit':        "graphics/goblin_hit.png",
	#     'death':      "graphics/goblin_death.png",
	# }

	def attack(self, player):
		player.take_damage(self.damage)

	def on_death(self):
		self.drop_item("moneta_di_bronzo")