from ursina import *
import random  # Make sure random is imported

try:
    from player import Player
    from enemy import Enemy
    from environment import Environment
except ImportError as e:
    print(f"Import error in game.py: {e}")
    raise

class Game(Entity):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.collider = 'box'  # Add this in __init__ method

    def setup(self):
        try:
            self.player = Player()
            self.spawn_enemies()
            self.setup_environment()
        except Exception as e:
            print(f"Error during game setup: {e}")
            import traceback
            traceback.print_exc()
            raise

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
        # Use a copy of the list to avoid modification during iteration
        for enemy in list(self.enemies):
            if not enemy or not self.player:
                continue
                
            try:
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
            except Exception as e:
                print(f"Error in collision detection: {e}")

    def restart(self):
        self.game_over = False
        self.score = 0
        self.setup()

# Only run this if game.py is run directly
if __name__ == "__main__":
    try:
        from camera import setup_camera
        
        app = Ursina(title="snakeX3000")
        game = Game()
        game.setup()
        
        camera_controller = setup_camera(game.player)
        app.run()
    except Exception as e:
        print(f"Error starting game from game.py: {e}")
        import traceback
        traceback.print_exc()