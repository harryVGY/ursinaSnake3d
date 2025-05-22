from ursina import *
import random

try:
    from player import Player
    from enemy import Enemy
    from environment import Environment
    from powerup import PowerUp
    from ui import UI  # Import the UI class
    from camera import setup_camera
except ImportError as e:
    print(f"Import error in game.py: {e}")
    raise

class Game(Entity):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.game_over = False
        self.collider = 'box'  # Add this in __init__ method
        self.ui = None  # Initialize UI reference
        self.started = False
        self.mode = 'normal'
        self.mode_text = None
        
        # Power-up spawning
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 15  # Spawn a power-up every 15 seconds
        self.max_powerups = 3  # Maximum number of power-ups allowed at once

    def setup(self):
        try:
            # Setup UI first
            self.ui = UI()
            
            # Show mode selection text
            self.mode_text = Text(text="Choose mode: 1=Normal, 2=Crazy", origin=(0, 0), scale=2, color=color.azure)
        except Exception as e:
            print(f"Error during game setup: {e}")
            import traceback
            traceback.print_exc()
            raise

    def start_game(self):
        """Initialize game elements after mode selection"""
        if self.mode_text:
            destroy(self.mode_text)
        
        # Setup player and pass UI reference for health updates
        self.player = Player()
        self.player.crazy_mode = (self.mode == 'crazy')
        self.player.max_health = self.ui.max_health  # Sync max health
        self.player.health = self.ui.health  # Sync initial health
        
        # Setup the rest of the game
        self.setup_environment()
        self.spawn_enemies()
        self.spawn_powerup()
        # Initialize camera after player is created
        self.camera_controller = setup_camera(self.player)
        # Set default camera view to third-person
        self.set_camera_view('third')
        self.started = True

    def spawn_enemies(self):
        for _ in range(5):  # Spawn 5 enemies for example
            enemy = Enemy()
            self.enemies.append(enemy)

    def setup_environment(self):
        # Initialize the game environment here
        self.environment = Environment()

    def update(self):
        if not self.started:
            return

        if not self.game_over:
            # Update player and enemies
            self.player.update()
            # Clamp player within city bounds
            x = min(max(self.player.position.x, -20), 20)
            z = min(max(self.player.position.z, -20), 20)
            if x != self.player.position.x or z != self.player.position.z:
                self.player.position = Vec3(x, self.player.position.y, z)

            for enemy in self.enemies:
                enemy.update()
            self.check_collisions()
            self.update_powerups()
            
            # Update UI score from game state
            if self.ui:
                self.ui.set_score(self.score)
            
            # Check for game over condition
            if self.player and self.player.health <= 0:
                self.game_over_sequence()

    def update_powerups(self):
        """Handle power-up spawning and timeouts"""
        # Update power-up spawn timer
        self.powerup_spawn_timer += time.dt
        
        # Spawn new power-up if timer expired and below max limit
        if self.powerup_spawn_timer >= self.powerup_spawn_interval and len(self.powerups) < self.max_powerups:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0

    def spawn_powerup(self):
        """Spawn a random power-up in the game world"""
        # Find a safe position away from buildings
        for _ in range(10):  # Try up to 10 times to find a good spot
            pos_x = random.uniform(-20, 20)
            pos_z = random.uniform(-20, 20)
            
            # Check if position is clear of buildings
            hit_info = raycast(
                origin=Vec3(pos_x, 10, pos_z),  # Cast from above
                direction=Vec3(0, -1, 0),  # Cast downward
                distance=20,
                ignore=[self.player] + self.player.segments
            )
            
            # If no building at position, it's safe to spawn
            if not hit_info.hit or not hasattr(hit_info.entity, 'name') or 'building' not in hit_info.entity.name:
                # Create power-up at position
                powerup = PowerUp(position=(pos_x, 1, pos_z))
                self.powerups.append(powerup)
                print(f"Spawned {powerup.powerup_type} power-up at ({pos_x:.1f}, 1, {pos_z:.1f})")
                return
        
        # If we couldn't find a safe spot after 10 tries, spawn at a default location
        powerup = PowerUp(position=(0, 1, -10))
        self.powerups.append(powerup)
        print(f"Spawned {powerup.powerup_type} power-up at fallback position")

    def check_collisions(self):
        # Check enemy collisions
        for enemy in list(self.enemies):
            if not enemy or not self.player:
                continue
                
            try:
                # Check collision with enemy
                hit_info = self.player.intersects(enemy)
                if hit_info.hit:
                    print(f"Hit enemy! Distance: {hit_info.distance}")
                    # Increase score
                    self.score += 1
                    print(f"Score: {self.score}")
                    # Remove the enemy
                    enemy.disable()
                    self.enemies.remove(enemy)
                    # Grow the snake
                    self.player.grow()
                    # Add to combo
                    self.player.add_combo()
                    # Spawn a new enemy
                    new_enemy = Enemy(position=(random.uniform(-15, 15), 1, random.uniform(-15, 15)))
                    self.enemies.append(new_enemy)
            except Exception as e:
                print(f"Error in enemy collision detection: {e}")
        
        # Check power-up collisions
        for powerup in list(self.powerups):
            if not powerup or not self.player:
                continue
                
            try:
                # Check collision with power-up
                hit_info = self.player.intersects(powerup)
                if hit_info.hit:
                    print(f"Collected power-up: {powerup.powerup_type}")
                    # Activate power-up effect
                    powerup.on_collect(self.player)
                    # Remove from tracking list
                    self.powerups.remove(powerup)
            except Exception as e:
                print(f"Error in power-up collision detection: {e}")
    
    def game_over_sequence(self):
        """Handle game over state when player's health reaches 0"""
        if not self.game_over:
            self.game_over = True
            print("GAME OVER")
            # Create game over text
            Text(text="GAME OVER", origin=(0, 0), scale=3, color=color.red)
            Text(text=f"Final Score: {self.score}", origin=(0, 0), position=(0, -0.1), scale=2, color=color.yellow)
            Text(text="Press R to restart", origin=(0, 0), position=(0, -0.2), scale=1.5, color=color.white)
            
            # Disable player movement
            if self.player:
                self.player.disable_movement = True

    def input(self, key):
        """Handle input for game functionality like restart"""
        # Mode selection before starting
        if not self.started:
            if key == '1' or key == '2':
                self.mode = 'crazy' if key == '2' else 'normal'
                print(f"Mode selected: {self.mode}")
                self.start_game()
            return

        if key == 'r' and self.game_over:
            self.restart()
        
        # Toggle camera view with keys 1/2
        elif key == '1':
            self.set_camera_view('first')
            print("First-person view activated")
        elif key == '2':
            self.set_camera_view('third')
            print("Third-person view activated")
    
    def restart(self):
        """Restart the game when R is pressed after game over"""
        # Clean up existing entities
        for enemy in self.enemies:
            destroy(enemy)
        self.enemies = []
        
        # Clean up power-ups
        for powerup in self.powerups:
            destroy(powerup)
        self.powerups = []
        
        if self.player:
            # Reset player position and segments
            self.player.reset()
            self.player.disable_movement = False
        
        # Reset game state
        self.game_over = False
        self.score = 0
        self.powerup_spawn_timer = 0
        # Immediately reset UI score
        if self.ui:
            self.ui.set_score(self.score)
        
        # Clear game over text
        for entity in scene.entities:
            if isinstance(entity, Text) and "GAME OVER" in entity.text:
                destroy(entity)
            if isinstance(entity, Text) and "Final Score" in entity.text:
                destroy(entity)
            if isinstance(entity, Text) and "Press R" in entity.text:
                destroy(entity)
        
        # Reset UI using the new reset method
        if self.ui:
            self.ui.reset()
            
        # Refresh game elements
        self.spawn_enemies()
        self.spawn_powerup()  # Initial power-up

    def set_camera_view(self, view):
        """Switch camera between first and third person views"""
        if not self.player:
            return
        if view == 'first':
            camera.parent = self.player
            camera.position = Vec3(0, 1, 0)
            camera.rotation = (0, 0, 0)
        else:
            # Parent to player so camera follows with an offset behind and above
            camera.parent = self.player
            camera.position = Vec3(0, 10, -20)  # moved further back
            camera.rotation = (20, 0, 0)  # Tilt downward to look at the player

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