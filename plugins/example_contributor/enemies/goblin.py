from core.interfaces.base_enemy import BaseEnemy

class Goblin(BaseEnemy):
    name       = "Goblin"
    health     = 60
    damage     = 15
    speed      = 3.0
    exp_reward = 20
    sprite_path = "graphics/goblin.png"

    def attack(self, player):
        player.take_damage(self.damage)

    def on_death(self):
        self.drop_item("moneta_di_bronzo")
