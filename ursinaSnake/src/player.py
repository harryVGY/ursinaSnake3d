from ursina import *
from collections import deque
import math
import random
import time as py_time

class Bullet(Entity):
    def __init__(self, position, direction, **kwargs):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=0.3,
            position=position,
            collider='sphere',
            **kwargs
        )
        self.direction = direction
        self.speed = 30  # Fast bullet speed
        self.max_lifetime = 2.0  # Seconds before bullet despawns
        self.lifetime = 0
        self.damage = 1
        self.hit_enemies = []  # Track hit enemies to avoid multiple hits
        
        # Add trail effect
        self.trail = Entity(
            parent=self,
            model='quad',
            color=color.orange,
            scale=(0.1, 0.5),
            billboard=True
        )
        
        # Add glow effect
        self.glow = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(1, 0.8, 0, 0.3),
            scale=1.5
        )
        
    def update(self):
        # Update position based on direction and speed
        self.position += self.direction * self.speed * time.dt
        
        # Update lifetime and destroy if expired
        self.lifetime += time.dt
        if self.lifetime >= self.max_lifetime:
            self.disable()
            destroy(self, delay=0.1)
            return
            
        # Check collision with enemies
        self.check_enemy_collisions()
        
        # Check collision with buildings
        hit_info = raycast(
            origin=self.position,
            direction=self.direction,
            distance=0.5,
            ignore=[self]
        )
        
        if hit_info.hit:
            # Create impact effect
            self.create_impact_effect(hit_info.point, hit_info.normal)
            # Destroy bullet on impact
            self.disable()
            destroy(self, delay=0.1)
    
    def check_enemy_collisions(self):
        """Check for collisions with enemies"""
        # Find all enemies
        for entity in scene.entities:
            if hasattr(entity, 'enemy_type') and entity not in self.hit_enemies:
                # Simple distance-based collision
                distance = (entity.position - self.position).length()
                if distance < 1.2:  # Slightly bigger than combined scale
                    self.hit_enemy(entity)
                    self.hit_enemies.append(entity)
                    
                    # Don't destroy the bullet yet if it's piercing
                    if len(self.hit_enemies) >= 3:  # Max 3 enemies per bullet
                        self.disable()
                        destroy(self, delay=0.1)
                        break
    
    def hit_enemy(self, enemy):
        """Handle enemy hit by bullet"""
        # Create hit effect
        self.create_impact_effect(enemy.position, Vec3(0, 1, 0))
        
        # Find game instance
        game_instance = None
        for entity in scene.entities:
            if hasattr(entity, 'ui') and hasattr(entity, 'player'):
                game_instance = entity
                break
        
        if game_instance:
            # Remove enemy
            if enemy in game_instance.enemies:
                # Add score based on enemy type
                score_value = enemy.points * 2  # Double points for shooting
                game_instance.score += score_value
                
                # Update UI
                if game_instance.ui:
                    game_instance.ui.set_score(game_instance.score)
                
                # Disable and remove enemy
                enemy.disable()
                game_instance.enemies.remove(enemy)
                
                # Spawn replacement enemy
                if enemy.enemy_type == 'seeker':
                    if random.random() < 0.3:  # Reduced chance for seeker replacement
                        game_instance.spawn_enemies(1, force_seeker=True)
                else:
                    game_instance.spawn_enemies(1)
    
    def create_impact_effect(self, position, normal):
        """Create visual impact effect"""
        # Create impact particles
        for _ in range(8):
            # Create particle spreading from impact point
            particle = Entity(
                model='sphere',
                color=color.yellow,
                position=position,
                scale=0.2
            )
            
            # Random direction in hemisphere facing the normal
            random_dir = Vec3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ).normalized()
            
            # Make sure it's in the hemisphere of the normal
            if random_dir.dot(normal) < 0:
                random_dir = -random_dir
                
            # Animate particle movement
            particle.animate_position(
                position + random_dir * random.uniform(1, 2),
                duration=0.3
            )
            
            # Fade out and shrink
            particle.animate_color(color.rgba(1, 0.8, 0, 0), duration=0.3)
            particle.animate_scale(0, duration=0.3)
            
            # Clean up
            destroy(particle, delay=0.3)

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'
        self.texture = 'brick'
        self.color = color.green
        self.scale = (1, 1, 1)
        self.position = (0, 1, 0)
        self.base_speed = 8  # Base speed value
        self.speed = self.base_speed
        self.growth_rate = 0.1
        self.length = 1
        self.segments = []
        self.segment_spacing = 10  # frames between segments
        self.position_history = deque(maxlen=1000)
        self.collider = 'box'
        self.mouse_sensitivity = 0  # disable mouse look
        self.turn_speed = 100        # degrees per second for turning
        self.crazy_mode = False      # toggle crazy mode (rotate on A/D)
        
        # Health system
        self.max_health = 3
        self.health = self.max_health
        self.damage_cooldown = 0  # Cooldown timer for damage
        self.damage_cooldown_duration = 1.0  # 1 second cooldown between damage
        
        # Visual damage feedback
        self.original_color = self.color
        
        # Movement control flag
        self.disable_movement = False
        
        # Power-up system
        self.active_powerups = {}  # {powerup_name: timer}
        self.is_invisible = False
        self.can_jump_obstacles = False
        self.jump_cooldown = 0
        self.jump_cooldown_max = 3.0
        
        # Combo system
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 5.0  # Seconds before combo resets
        
        print("Player initialized - press WASD to move, mouse to look, 1/2 to switch views")

    def update(self):
        if self.disable_movement:
            return
            
        self.handle_movement()
        self.update_segments()
        self.check_collisions()
        self.update_powerups()
        self.update_combo()
        
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= time.dt
            
        # Update jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= time.dt

    def input(self, key):
        # Toggle crazy mode
        if key == 'c':
            self.crazy_mode = not self.crazy_mode
            print(f"Crazy mode {'ON' if self.crazy_mode else 'OFF'}")
            return
        
        # Shoot gun with left click
        if key == 'left mouse down' or key == 'left mouse down':
            print("Shooting attempt detected")
            self.shoot_gun()

    def shoot_gun(self):
        """Shoot a bullet in the direction you're aiming with the mouse"""
        print("Shooting gun")
        # Get the mouse position in 3D space
        mouse_world_position = mouse.world_point
        
        # Fallback if mouse.world_point is None
        if mouse_world_position is None:
            # Shoot in the direction the player is facing
            shoot_direction = self.forward
            print("Using fallback shooting direction (forward)")
        else:
            # Calculate shooting direction - from player head toward mouse position
            shoot_direction = (mouse_world_position - self.position).normalized()
            print(f"Shooting at mouse position: {mouse_world_position}")
        
        # Ensure the direction is level (not shooting up/down too much)
        shoot_direction.y = min(max(shoot_direction.y, -0.3), 0.3)  # Limit vertical angle
        shoot_direction = shoot_direction.normalized()  # Re-normalize
        
        # Create bullet slightly in front of player to avoid self-collision
        bullet_pos = self.position + shoot_direction * 1.5 + Vec3(0, 0.5, 0)
        
        # Create the bullet
        bullet = Bullet(position=bullet_pos, direction=shoot_direction)
        
        # Add muzzle flash effect
        self.create_muzzle_flash(bullet_pos, shoot_direction)
        
        # Add recoil effect - slight push back
        self.position -= shoot_direction * 0.3

    def create_muzzle_flash(self, position, direction):
        """Create a muzzle flash effect when firing"""
        # Create flash
        flash = Entity(
            model='sphere',
            color=color.yellow,
            position=position,
            scale=0.5
        )
        
        # Quick expanding and fading animation
        flash.animate_scale(2, duration=0.1)
        flash.animate_color(color.clear, duration=0.1)
        
        # Clean up
        destroy(flash, delay=0.1)
        
        # Add some smoke particles
        for _ in range(5):
            smoke = Entity(
                model='sphere',
                color=color.rgba(0.7, 0.7, 0.7, 0.5),
                position=position,
                scale=0.3
            )
            
            # Random direction slightly forward
            random_dir = direction + Vec3(
                random.uniform(-0.3, 0.3),
                random.uniform(-0.3, 0.3),
                random.uniform(-0.3, 0.3)
            )
            
            # Animate
            smoke.animate_position(
                position + random_dir * random.uniform(1, 2),
                duration=0.5
            )
            smoke.animate_scale(0, duration=0.5)
            smoke.animate_color(color.rgba(0.7, 0.7, 0.7, 0), duration=0.5)
            
            # Clean up
            destroy(smoke, delay=0.5)

    def handle_movement(self):
        # Crazy mode: turn on A/D; Normal: no turn
        if self.crazy_mode:
            if held_keys['a']:
                self.rotation_y += self.turn_speed * time.dt
            if held_keys['d']:
                self.rotation_y -= self.turn_speed * time.dt
        
        # Build movement direction
        move_direction = Vec3(0, 0, 0)
        if held_keys['w']:
            move_direction += self.forward
        if held_keys['s']:
            move_direction -= self.forward
        # Normal mode: strafe left/right
        if not self.crazy_mode:
            if held_keys['a']:
                move_direction -= self.right
            if held_keys['d']:
                move_direction += self.right
            
        # Speed boost/reduction with Shift and Control
        if held_keys['shift']:
            current_speed = self.speed * 1.5
        elif held_keys['control']:
            current_speed = self.speed * 0.6
        else:
            current_speed = self.speed
        
        # Jump over obstacles with space if we have the power-up
        if held_keys['space'] and self.can_jump_obstacles and self.jump_cooldown <= 0:
            self.perform_jump()
            
        # Apply movement
        if move_direction.length() > 0:
            new_position = self.position + move_direction * current_speed * time.dt
            
            # Collision check
            hit_info = raycast(
                origin=self.position + Vec3(0, 0.5, 0),
                direction=move_direction,
                distance=1.0,
                ignore=[self] + self.segments
            )
            
            if hit_info.hit:
                entity = hit_info.entity
                # Check if we hit a building
                if hasattr(entity, 'name') and 'building' in entity.name:
                    # Don't collide if player is invisible
                    if not self.is_invisible:
                        self.handle_building_collision()
                    else:
                        # Pass through if invisible
                        self.position = new_position
                else:
                    # Not a building, can move
                    self.position = new_position
            else:
                self.position = new_position
        
        # Keep player at constant height
        self.y = 1

    def handle_building_collision(self):
        """Handle collision with buildings - reduce health and provide visual feedback"""
        # Only take damage if not in cooldown
        if self.damage_cooldown <= 0:
            # Apply damage
            self.health -= 1
            self.damage_cooldown = self.damage_cooldown_duration
            
            # Visual feedback - flash red
            self.color = color.red
            invoke(self.reset_color, delay=0.2)
            
            # Update UI if we can find the game instance
            game_instance = None
            for entity in scene.entities:
                if hasattr(entity, 'ui') and hasattr(entity, 'player'):
                    game_instance = entity
                    break
            
            if game_instance and game_instance.ui:
                game_instance.ui.set_health(self.health)
            
            # Sound effect would go here
            
            # Print debug info
            print(f"Player hit a building! Health: {self.health}")
            
            # Apply knockback
            knockback_direction = -self.forward
            self.position += knockback_direction * 2  # Knock back 2 units
    
    def reset_color(self):
        """Reset player color after collision flash"""
        self.color = self.original_color
        
    def update_segments(self):
        # Record current head position each frame
        self.position_history.append(self.position)
        # Update segment positions based on history
        for i, segment in enumerate(self.segments):
            idx = -((i+1) * self.segment_spacing)
            if abs(idx) <= len(self.position_history):
                segment.position = self.position_history[idx]

    def grow(self):
        # Create a new segment matching player appearance
        new_segment = Entity(
            model='cube', 
            color=color.green,
            texture='brick',
            scale=(0.9, 0.9, 0.9)
        )
        
        # Position it behind the player or the last segment
        if len(self.segments) == 0:
            new_segment.position = self.position - (self.forward * 1.2)
        else:
            new_segment.position = self.segments[-1].position
            
        self.segments.append(new_segment)
        self.length += self.growth_rate

    def check_collisions(self):
        # Additional collision checks can be added here
        pass

    def reset(self):
        """Reset player state for new game"""
        self.position = (0, 1, 0)
        self.rotation_y = 0
        self.health = self.max_health
        self.damage_cooldown = 0
        
        # Clear segments
        for segment in self.segments:
            destroy(segment)
        self.segments = []
        
        # Reset color
        self.color = self.original_color
        
        # Reset movement
        self.disable_movement = False

    def update_powerups(self):
        """Update all active power-ups and their timers"""
        # Process each active power-up
        powerups_to_remove = []
        for powerup, timer in self.active_powerups.items():
            # Decrease timer
            self.active_powerups[powerup] -= time.dt
            
            # Check if power-up expired
            if self.active_powerups[powerup] <= 0:
                powerups_to_remove.append(powerup)
                
        # Remove expired power-ups
        for powerup in powerups_to_remove:
            self.deactivate_powerup(powerup)
    
    def update_combo(self):
        """Update combo timer and reset when expired"""
        if self.combo_count > 0:
            self.combo_timer -= time.dt
            if self.combo_timer <= 0:
                self.reset_combo()
    
    def apply_powerup(self, powerup_type, duration):
        """Apply a power-up effect to the player"""
        # Add the power-up to active list with its duration
        self.active_powerups[powerup_type] = duration
        
        # Apply power-up effects
        if powerup_type == 'speed':
            self.speed = self.base_speed * 1.5
            print("Speed power-up activated! +50% speed")
            
        elif powerup_type == 'invisibility':
            self.is_invisible = True
            # Visual effect - make player semi-transparent
            self.alpha = 0.5
            for segment in self.segments:
                segment.alpha = 0.5
            print("Invisibility power-up activated! You can pass through buildings")
            
        elif powerup_type == 'jump':
            self.can_jump_obstacles = True
            print("Jump power-up activated! Press SPACE to jump over obstacles")
            
        elif powerup_type == 'health':
            self.health = min(self.health + 1, self.max_health)
            # Find game instance and update UI
            game_instance = None
            for entity in scene.entities:
                if hasattr(entity, 'ui') and hasattr(entity, 'player'):
                    game_instance = entity
                    break
            if game_instance and game_instance.ui:
                game_instance.ui.set_health(self.health)
            print(f"Health power-up activated! Health restored to {self.health}")
    
    def deactivate_powerup(self, powerup_type):
        """Remove a power-up effect when it expires"""
        if powerup_type in self.active_powerups:
            del self.active_powerups[powerup_type]
            
            # Remove power-up effects
            if powerup_type == 'speed':
                self.speed = self.base_speed
                print("Speed power-up expired")
                
            elif powerup_type == 'invisibility':
                self.is_invisible = False
                # Restore original appearance
                self.alpha = 1
                for segment in self.segments:
                    segment.alpha = 1
                print("Invisibility power-up expired")
                
            elif powerup_type == 'jump':
                self.can_jump_obstacles = False
                print("Jump power-up expired")
    
    def perform_jump(self):
        """Jump over obstacles"""
        if self.can_jump_obstacles and self.jump_cooldown <= 0:
            # Visual effect - leap animation
            self.animate_position(
                self.position + (self.forward * 3) + Vec3(0, 2, 0), 
                duration=0.3,
                curve=curve.out_back
            )
            # Set cooldown
            self.jump_cooldown = self.jump_cooldown_max
            print("Jump!")
    
    def add_combo(self):
        """Increment combo counter when eating enemies in succession"""
        self.combo_count += 1
        self.combo_timer = self.combo_timeout
        
        # Apply combo bonuses
        bonus_score = self.combo_count * 10  # More points for higher combos
        
        # Find game instance to update score
        game_instance = None
        for entity in scene.entities:
            if hasattr(entity, 'ui') and hasattr(entity, 'score'):
                game_instance = entity
                break
        
        if game_instance:
            game_instance.score += bonus_score
            if game_instance.ui:
                game_instance.ui.set_score(game_instance.score)
        
        # Visual feedback
        print(f"Combo x{self.combo_count}! +{bonus_score} points")
        
        # Apply special effects for higher combos
        if self.combo_count == 3:
            self.speed += 1  # Small speed increase
            print("Combo bonus: Speed increased!")
        elif self.combo_count == 5:
            self.apply_powerup('invisibility', 3.0)  # Brief invisibility
        elif self.combo_count >= 10:
            # Powerful combo bonus
            self.apply_powerup('speed', 5.0)
            print("MEGA COMBO BONUS!")
    
    def reset_combo(self):
        """Reset combo counter when timeout expires"""
        if self.combo_count > 0:
            print(f"Combo x{self.combo_count} expired")
            self.combo_count = 0

    def take_damage_from_enemy(self, enemy):
        """Handle taking damage from an enemy"""
        # Only take damage if not in cooldown
        if self.damage_cooldown <= 0:
            # Apply damage
            self.health -= 1
            self.damage_cooldown = self.damage_cooldown_duration
            
            # Visual feedback - flash red
            self.color = color.red
            invoke(self.reset_color, delay=0.2)
            
            # Create damage effect
            self.create_damage_effect(enemy.color)
            
            # Update UI if we can find the game instance
            game_instance = None
            for entity in scene.entities:
                if hasattr(entity, 'ui') and hasattr(entity, 'player'):
                    game_instance = entity
                    break
            
            if game_instance and game_instance.ui:
                game_instance.ui.set_health(self.health)
            
            # Apply knockback
            knockback_direction = (self.position - enemy.position).normalized()
            self.position += knockback_direction * 2  # Knock back 2 units
            
            print(f"Player took damage from {enemy.enemy_type} enemy! Health: {self.health}")
            
            # Play damage sound if available
            if hasattr(self, 'damage_sound'):
                self.damage_sound.play()

    def create_damage_effect(self, color=color.red):
        """Create particle effect when player takes damage"""
        # Create damage particles
        for _ in range(10):
            particle = Entity(
                model='sphere',
                color=color,
                position=self.position + Vec3(
                    random.uniform(-1, 1),
                    random.uniform(0, 1),
                    random.uniform(-1, 1)
                ),
                scale=random.uniform(0.2, 0.5)
            )
            
            # Animate the particles
            particle.animate_scale(0, duration=0.5)
            particle.animate_color(color.rgba(1, 0, 0, 0), duration=0.5)
            particle.animate_position(
                particle.position + Vec3(
                    random.uniform(-2, 2),
                    random.uniform(1, 3),
                    random.uniform(-2, 2)
                ),
                duration=0.5
            )
            
            # Clean up
            destroy(particle, delay=0.5)