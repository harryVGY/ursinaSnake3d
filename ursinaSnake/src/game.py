from ursina import *
import random
import time as py_time

try:
    from player import Player
    from enemy import Enemy
    from environment import Environment
    from ui import UI
except ImportError as e:
    print(f"Import error in game.py: {e}")
    raise

class PowerUp(Entity):
    def __init__(self, position=(0,0,0), power_type=None):
        super().__init__(
            model='sphere',
            position=position,
            scale=(0.7, 0.7, 0.7),
            collider='sphere'
        )
        
        self.power_type = power_type or random.choice(['speed', 'invisible', 'jump', 'shield'])
        
        # Set color based on power type
        if self.power_type == 'speed':
            self.color = color.yellow
        elif self.power_type == 'invisible':
            self.color = color.cyan
        elif self.power_type == 'jump':
            self.color = color.magenta
        elif self.power_type == 'shield':
            self.color = color.azure
        
        # Add hover animation
        self.y_offset = 0
        self.animate_y()
        
        # Add rotation animation
        self.animate('rotation_y', 360, duration=3, loop=True)
        
    def animate_y(self):
        new_y = self.y + 0.5
        self.animate('y', new_y, duration=1, curve=curve.in_out_sine)
        invoke(self.animate_y_reverse, delay=1)
    
    def animate_y_reverse(self):
        original_y = self.y - 0.5
        self.animate('y', original_y, duration=1, curve=curve.in_out_sine)
        invoke(self.animate_y, delay=1)

class Game(Entity):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = []
        self.power_ups = []
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.combo_timeout = 5.0  # Seconds before combo resets
        self.environment = None
        self.game_over = False
        self.ui = None
        self.collider = 'box'  # Add this in __init__ method
        
        # Track game time
        self.game_time = 0
        self.power_up_spawn_timer = 0
        self.power_up_interval = 15  # Spawn power-up every 15 seconds
        
        # Sound effects (placeholders)
        self.eat_sound = None
        self.power_up_sound = None
        self.combo_sound = None
        
        print("Game initialized")

    def setup(self):
        try:
            # Setup UI first so it's rendered on top
            self.ui = UI()
            
            # Create player
            self.player = Player()
            
            # Setup environment
            self.environment = Environment()
            
            # Spawn initial enemies
            self.spawn_enemies(count=5)
            
            # Try to load sounds
            try:
                self.eat_sound = Audio('eat_sound', autoplay=False, loop=False)
                self.power_up_sound = Audio('powerup_sound', autoplay=False, loop=False)
                self.combo_sound = Audio('combo_sound', autoplay=False, loop=False)
            except:
                print("Warning: Could not load sound effects")
            
            print("Game setup complete")
        except Exception as e:
            print(f"Error during game setup: {e}")
            import traceback
            traceback.print_exc()
            raise

    def spawn_enemies(self, count=1):
        for _ in range(count):
            # Generate a position that's not too close to the player
            while True:
                pos = (random.uniform(-20, 20), 1, random.uniform(-20, 20))
                # Check if position is far enough from player (at least 5 units)
                if self.player and distance(pos, self.player.position) > 5:
                    break
            
            # Create the enemy
            enemy = Enemy(position=pos)
            self.enemies.append(enemy)
            print(f"Spawned enemy at position {pos}")

    def spawn_power_up(self):
        # Find a position away from buildings and other objects
        while True:
            pos = (random.uniform(-20, 20), 1, random.uniform(-20, 20))
            # Check if position is not colliding with anything
            hit_info = raycast(pos + Vec3(0,1,0), Vec3(0,-1,0), distance=3)
            if not hit_info.hit or hit_info.entity == self.environment.ground:
                break
        
        # Create the power-up
        power_up = PowerUp(position=pos)
        self.power_ups.append(power_up)
        print(f"Spawned {power_up.power_type} power-up at {pos}")

    def setup_environment(self):
        # This is now handled in the setup method
        pass

    def update(self):
        if self.game_over:
            # Handle game over state
            return
            
        # Update game time
        self.game_time += time.dt
        
        # Update combo timer if we have an active combo
        if self.combo > 0:
            self.combo_timer -= time.dt
            if self.combo_timer <= 0:
                self.combo = 0
                # Update UI to show combo has ended
                if self.ui:
                    self.ui.set_combo(0)
        
        # Check if it's time to spawn a power-up
        self.power_up_spawn_timer += time.dt
        if self.power_up_spawn_timer >= self.power_up_interval:
            self.power_up_spawn_timer = 0
            self.spawn_power_up()
        
        if self.environment:
            self.environment.update()
            
        # Check for collisions
        self.check_collisions()
        
        # Update UI
        if self.ui:
            self.ui.set_score(self.score)
            # Health will be updated in collision handling if needed

    def check_collisions(self):
        if not self.player:
            return
            
        # Check enemy collisions
        for enemy in list(self.enemies):
            if not enemy:
                continue
                
            try:
                # Check for collision with player
                hit_info = self.player.intersects(enemy)
                if hit_info.hit:
                    self.handle_enemy_collision(enemy)
            except Exception as e:
                print(f"Error in enemy collision detection: {e}")
        
        # Check power-up collisions
        for power_up in list(self.power_ups):
            if not power_up:
                continue
                
            try:
                # Check for collision with player
                hit_info = self.player.intersects(power_up)
                if hit_info.hit:
                    self.handle_power_up_collision(power_up)
            except Exception as e:
                print(f"Error in power-up collision detection: {e}")
    
    def handle_enemy_collision(self, enemy):
        # Play eat sound
        if self.eat_sound:
            self.eat_sound.play()
            
        # Increase score
        base_points = 10
        
        # Apply combo multiplier
        self.combo += 1
        self.combo_timer = self.combo_timeout  # Reset combo timer
        
        # Calculate score with combo
        points = base_points * self.combo
        self.score += points
        
        print(f"Hit enemy! Combo: {self.combo}x, Points: +{points}, Total: {self.score}")
        
        # Update UI
        if self.ui:
            self.ui.set_score(self.score)
            self.ui.set_combo(self.combo)
        
        # Play combo sound for good combos
        if self.combo >= 3 and self.combo_sound:
            self.combo_sound.play()
        
        # Remove the enemy
        enemy.disable()
        self.enemies.remove(enemy)
        
        # Grow the snake
        self.player.grow()
        
        # Spawn a new enemy
        self.spawn_enemies(1)
    
    def handle_power_up_collision(self, power_up):
        # Play power-up sound
        if self.power_up_sound:
            self.power_up_sound.play()
            
        effect_duration = 10  # seconds
        
        # Apply power-up effect based on type
        if power_up.power_type == 'speed':
            self.player.speed *= 1.5
            invoke(self.end_speed_boost, delay=effect_duration)
            print("Speed boost activated!")
            
        elif power_up.power_type == 'invisible':
            # Make snake semi-transparent
            self.player.alpha = 0.3
            for segment in self.player.segments:
                segment.alpha = 0.3
            invoke(self.end_invisibility, delay=effect_duration)
            print("Invisibility activated!")
            
        elif power_up.power_type == 'jump':
            # Enable jump ability (implementation depends on your player class)
            self.player.can_jump = True
            invoke(self.end_jump_ability, delay=effect_duration)
            print("Jump ability activated!")
            
        elif power_up.power_type == 'shield':
            # Add shield effect
            self.player.has_shield = True
            shield = Entity(
                parent=self.player,
                model='sphere',
                scale=1.2,
                color=color.rgba(0, 0.6, 1, 0.2)
            )
            self.player.shield_entity = shield
            invoke(self.end_shield, delay=effect_duration)
            print("Shield activated!")
        
        # Remove the power-up
        power_up.disable()
        self.power_ups.remove(power_up)
        
        # Update UI to show active power-up
        if self.ui:
            self.ui.set_power_up(power_up.power_type, effect_duration)
    
    def end_speed_boost(self):
        if self.player:
            self.player.speed /= 1.5
            print("Speed boost ended")
    
    def end_invisibility(self):
        if self.player:
            self.player.alpha = 1.0
            for segment in self.player.segments:
                segment.alpha = 1.0
            print("Invisibility ended")
    
    def end_jump_ability(self):
        if self.player:
            self.player.can_jump = False
            print("Jump ability ended")
    
    def end_shield(self):
        if self.player:
            self.player.has_shield = False
            if hasattr(self.player, 'shield_entity') and self.player.shield_entity:
                self.player.shield_entity.disable()
            print("Shield ended")

    def game_over_sequence(self):
        if self.game_over: # Prevent running multiple times
            return
        self.game_over = True
        mouse.locked = False # Unlock mouse to show cursor
        print(f"Game Over! Final score: {self.score}")
        
        # Show game over text
        self.game_over_text = Text(text='GAME OVER', origin=(0,0), scale=3, color=color.red, y=0.1)
        self.final_score_text = Text(text=f'Final Score: {self.score}', origin=(0,0), scale=2, y=0)
        
        # Show restart button
        self.restart_button = Button(
            text='Restart (Click or Enter)', 
            color=color.azure, 
            scale=(0.3, 0.1),
            position=(0, -0.2)
        )
        self.restart_button.on_click = self.restart
    
    def restart(self):
        print("Restarting game...")
        # Cleanup existing entities
        for enemy in self.enemies:
            if enemy:
                destroy(enemy)
        self.enemies.clear()
        
        for power_up in self.power_ups:
            if power_up:
                destroy(power_up)
        self.power_ups.clear()
        
        if self.player:
            # Explicitly destroy segments first if needed
            if hasattr(self.player, 'segments'):
                for segment in self.player.segments:
                    if segment:
                        destroy(segment)
                self.player.segments.clear()
            destroy(self.player)
            self.player = None
            
        if self.environment:
            # Destroy buildings and other environment elements if necessary
            if hasattr(self.environment, 'buildings'):
                 for building in self.environment.buildings:
                      if building:
                           destroy(building)
                 self.environment.buildings.clear()
            if hasattr(self.environment, 'dynamic_elements'):
                 # Be careful destroying elements shared elsewhere (like obstacles)
                 # Only destroy elements fully owned by environment if needed
                 pass # Or selectively destroy
            destroy(self.environment)
            self.environment = None

        if self.ui:
             destroy(self.ui) # Destroy old UI
             self.ui = None
            
        # Remove game over UI elements if they exist
        if hasattr(self, 'game_over_text') and self.game_over_text:
            destroy(self.game_over_text)
            self.game_over_text = None
        if hasattr(self, 'final_score_text') and self.final_score_text:
             destroy(self.final_score_text)
             self.final_score_text = None
        if hasattr(self, 'restart_button') and self.restart_button:
            destroy(self.restart_button)
            self.restart_button = None
            
        # Reset game state
        self.game_over = False
        self.score = 0
        self.combo = 0
        self.game_time = 0
        self.power_up_spawn_timer = 0
        
        # Setup fresh game
        self.setup() # This creates new player, env, ui
        
        # Re-lock mouse for gameplay
        mouse.locked = True
        print("Game restarted.")

    def input(self, key):
        # Handle global inputs, like restarting on Enter when game is over
        if self.game_over and (key == 'enter' or key == 'enter hold'):
            self.restart()

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