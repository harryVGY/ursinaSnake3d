from ursina import *
from player import Player
from enemy import Enemy
from environment import Environment
from random import randint
# Remove any camera imports here to avoid circular imports

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
            # Fix collision detection using more robust method
            hit_info = self.player.intersects(enemy)
            if hit_info.hit:
                print(f"Hit detected! Distance: {hit_info.distance}")
                # Increase score
                self.score += 1
                print(f"Score: {self.score}")
                # Remove the enemy
                enemy.disable()
                self.enemies.remove(enemy)
                # Grow the snake
                self.player.grow()
                # Spawn a new enemy
                new_enemy = Enemy(position=(random.uniform(-15, 15), 1, random.uniform(-15, 15)))
                self.enemies.append(new_enemy)

    def restart(self):
        self.game_over = False
        self.score = 0
        self.setup()

# Create an instance of the Game class and run the game
if __name__ == "__main__":
    app = Ursina(icon="../assets/models/snake.ico", title="snakeX3000")
    game = Game()
    game.setup()

    # Import camera module only when running as main script
    # to avoid circular imports
    from camera import setup_camera
    camera_controller = setup_camera(game.player)

    app.run()