from ursina import *
from player import Player
from enemy import Enemy
from environment import Environment
from random import randint
from camera import setup_camera  # Add this import

class Game(Entity):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.collider = 'box'  # Add this in __init__ method

    def setup(self):
        self.player = Player()
        self.spawn_enemies()
        self.setup_environment()

    def spawn_enemies(self):
        for _ in range(5):  # Spawn 5 enemies for example
            enemy = Enemy()
            self.enemies.append(enemy)

    def setup_environment(self):
        # Initialize the game environment here
        Environment()

    def update(self):
        if not self.game_over:
            self.player.update()
            for enemy in self.enemies:
                enemy.update()
            self.check_collisions()

    def check_collisions(self):
        for enemy in self.enemies:
            if self.player.intersects(enemy).hit:
                self.game_over = True
                print("Game Over! Your score:", self.score)

    def restart(self):
        self.game_over = False
        self.score = 0
        self.setup()

# Create an instance of the Game class and run the game
if __name__ == "__main__":
    app = Ursina()
    game = Game()
    game.setup()
    setup_camera()  # Call this to set up the camera
    app.run()