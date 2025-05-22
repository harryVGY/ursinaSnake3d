from ursina import *
import random  # Make sure random is imported

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
        self.camera_controller = None
        
        # Power-up spawning
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 15  # Spawn a power-up every 15 seconds
        self.max_powerups = 3  # Maximum number of power-ups allowed at once
        
        # Enemy spawning
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 10  # Spawn a new enemy every 10 seconds
        self.max_enemies = 12  # Maximum number of enemies at once

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
        
        # Setup environment first so buildings are ready
        self.setup_environment()
        
        # Find a safe position for the player
        safe_position = self.find_safe_spawn_position()
        
        # Setup player and pass UI reference for health updates
        self.player = Player()
        self.player.position = safe_position  # Set player at safe position
        self.player.crazy_mode = (self.mode == 'crazy')
        self.player.max_health = self.ui.max_health  # Sync max health
        self.player.health = self.ui.health  # Sync initial health
        
        # Give environment a reference to the player for targeting
        if hasattr(self, 'environment'):
            self.environment.player = self.player
        
        # Spawn initial enemies
        self.spawn_enemies(7)  # Start with 7 enemies (including 2 seekers)
        self.spawn_powerup()
        
        # Initialize camera after player is created
        self.camera_controller = setup_camera(self.player)
        self.started = True

    def spawn_enemies(self, count=1, force_seeker=False):
        """Spawn specified number of enemies, with optional forced seeker type"""
        for _ in range(count):
            # Find a safe position away from buildings and player
            safe_position = self.find_safe_spawn_position()
            
            if force_seeker:
                enemy_type = 'seeker'
            else:
                # 30% chance for seeker, 70% for other types by default
                enemy_type = None  # Let the Enemy class decide based on its weighted distribution
                
            # Create the enemy
            enemy = Enemy(position=safe_position, enemy_type=enemy_type)
            print(f"Spawned {enemy.enemy_type} enemy at position {safe_position}")
            self.enemies.append(enemy)

    def find_safe_spawn_position(self):
        """Find a position that's away from buildings and the player"""
        min_player_distance = 10  # Minimum distance from player
        
        for _ in range(15):  # Try 15 times to find a good spot
            pos_x = random.uniform(-20, 20)
            pos_z = random.uniform(-20, 20)
            position = Vec3(pos_x, 1, pos_z)
            
            # Check player distance
            if self.player:
                player_distance = (position - self.player.position).length()
                if player_distance < min_player_distance:
                    continue  # Too close to player
            
            # Check if position is clear of buildings using raycast
            hit_info = raycast(
                origin=Vec3(pos_x, 10, pos_z),  # Cast from above
                direction=Vec3(0, -1, 0),  # Cast downward
                distance=20,
                ignore=[self.player] + (self.player.segments if self.player else [])
            )
            
            # If no building at position, it's safe to spawn
            if not hit_info.hit or not hasattr(hit_info.entity, 'name') or 'building' not in hit_info.entity.name:
                return position
        
        # If we couldn't find a spot after 15 tries, use a fallback position
        return Vec3(random.uniform(-5, 5), 1, random.uniform(-5, 5))

    def setup_environment(self):
        # Initialize the game environment
        self.environment = Environment()

    def update(self):
        if not self.started:
            return

        if not self.game_over:
            try:
                # Update enemy spawning
                self.enemy_spawn_timer += time.dt
                if self.enemy_spawn_timer >= self.enemy_spawn_interval and len(self.enemies) < self.max_enemies:
                    self.spawn_enemies(1)  # Spawn one new enemy
                    self.enemy_spawn_timer = 0
                
                # Update player
                if self.player and self.player.enabled:
                    self.player.update()
                
                # Update enemies
                for enemy in list(self.enemies):
                    # Skip enemies that may have been removed
                    if not enemy or not enemy.enabled:
                        continue
                    enemy.update()
                
                # Update environment
                if self.environment:
                    self.environment.update()
                    
                self.check_collisions()
                self.update_powerups()
                
                # Update UI score from game state
                if self.ui:
                    self.ui.set_score(self.score)
                
                # Check for game over condition
                if self.player and self.player.health <= 0:
                    self.game_over_sequence()
            except Exception as e:
                print(f"Error in game update loop: {e}")
                import traceback
                traceback.print_exc()

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
        # Use the safe position finder
        position = self.find_safe_spawn_position()
        
        # Create power-up at position
        powerup = PowerUp(position=position)
        self.powerups.append(powerup)
        print(f"Spawned {powerup.powerup_type} power-up at ({position.x:.1f}, {position.y:.1f}, {position.z:.1f})")

    def check_collisions(self):
        # Check enemy collisions with player's head
        for enemy in list(self.enemies):
            if not enemy or not self.player:
                continue
                
            try:
                # Check collision with player's head
                hit_info = self.player.intersects(enemy)
                
                # Special handling for seekers - they damage the player but die in the process
                if enemy.enemy_type == 'seeker':
                    if hit_info.hit:
                        # Seeker hit the player - deal damage
                        self.player.take_damage_from_enemy(enemy)
                        
                        # Seeker dies after hitting player
                        enemy.disable()
                        self.enemies.remove(enemy)
                        
                        # Spawn a replacement seeker
                        if random.random() < 0.5:  # 50% chance to spawn a new seeker
                            self.spawn_enemies(1, force_seeker=True)
                else:
                    # Regular enemies can be eaten by the player's head
                    if hit_info.hit:
                        print(f"Player hit {enemy.enemy_type} enemy! Distance: {hit_info.distance}")
                        # Increase score based on enemy points value
                        enemy_points = getattr(enemy, 'points', 1)
                        self.score += enemy_points
                        print(f"Score: {self.score}, added {enemy_points} points")
                        
                        # Remove the enemy
                        enemy.disable()
                        self.enemies.remove(enemy)
                        
                        # Grow the snake
                        self.player.grow()
                        
                        # Add to combo
                        self.player.add_combo()
                        
                        # 15% chance to spawn a seeker in place of a regular enemy
                        # to maintain challenge as player grows
                        if random.random() < 0.15:
                            self.spawn_enemies(1, force_seeker=True)
                        else:
                            # Spawn a replacement enemy of random type
                            self.spawn_enemies(1)
                
                # Check collisions with player's body segments (except for seekers, already handled)
                if enemy.enemy_type != 'seeker' and self.player.segments and not self.player.is_invisible:
                    for segment in self.player.segments:
                        segment_hit = segment.intersects(enemy)
                        if segment_hit.hit:
                            # Player takes damage from enemy
                            self.player.take_damage_from_enemy(enemy)
                            break
                            
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
                    # Update UI if needed
                    if self.ui and hasattr(self.ui, 'update_powerup_display'):
                        self.ui.update_powerup_display(powerup.powerup_type, powerup.duration)
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
        
        # Toggle camera view with 1/2
        elif self.camera_controller:
            if key == '1' and hasattr(self.camera_controller, 'set_mode'):
                self.camera_controller.set_mode('first_person')
            elif key == '2' and hasattr(self.camera_controller, 'set_mode'):
                self.camera_controller.set_mode('third_person')
    
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
        self.enemy_spawn_timer = 0
        
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
        self.spawn_enemies(7)  # Restart with 7 enemies
        self.spawn_powerup()  # Initial power-up

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