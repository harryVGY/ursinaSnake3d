from ursina import *

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
        self.collider = 'box'
        self.mouse_sensitivity = 150  # Increased from 100
        
        # New player attributes for game mechanics
        self.can_jump = False
        self.jumping = False
        self.jump_height = 3
        self.gravity = 9.8
        self.vertical_velocity = 0
        self.has_shield = False
        self.shield_entity = None
        self.is_boosting = False
        
        # Collision cooldown to prevent multiple collisions
        self.collision_cooldown = 0
        
        # Tail segment management
        self.segment_spacing = 1.0
        self.segment_update_interval = 0.05
        self.segment_update_timer = 0
        self.previous_positions = []
        
        # Player health (lives)
        self.health = 3
        
        print("Player initialized - press WASD to move, mouse to look, 1/2 to switch views")

    def update(self):
        self.handle_movement()
        self.update_segments()
        self.handle_power_ups()
        
        # Decrease collision cooldown
        if self.collision_cooldown > 0:
            self.collision_cooldown -= time.dt

    def handle_movement(self):
        # Mouse look
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity * time.dt
        
        # Speed control using Shift key
        current_speed = self.speed
        if held_keys['shift']:
            if not self.is_boosting:
                self.speed = min(self.speed * 1.5, self.base_speed * 2)
                self.is_boosting = True
        else:
            if self.is_boosting:
                self.speed = self.base_speed
                self.is_boosting = False
        
        # Movement with WASD
        move_direction = Vec3(0, 0, 0)
        
        if held_keys['w']:
            move_direction += self.forward
        if held_keys['s']:
            move_direction -= self.forward
        if held_keys['a']:
            move_direction -= self.right
        if held_keys['d']:
            move_direction += self.right
            
        # Normalize and apply movement
        if move_direction.length() > 0:
            move_direction = move_direction.normalized()
            
            # Calculate the new position
            new_position = self.position + move_direction * self.speed * time.dt
            
            # Check for collisions before moving
            hit_info = raycast(
                origin=self.position + Vec3(0, 0.5, 0),  # Cast from slightly above current position
                direction=move_direction,
                distance=1.0,  # Check a bit ahead of the player
                ignore=[self] + self.segments
            )
            
            if hit_info.hit and not self.has_shield:
                # Different collision handling based on entity type
                entity = hit_info.entity
                
                # Ignore collisions with entities that aren't buildings
                if hasattr(entity, 'name') and ('building' in entity.name or 'obstacle' in entity.name):
                    if self.collision_cooldown <= 0:
                        self.collision_cooldown = 0.5  # Set cooldown to prevent multiple rapid collisions
                        print(f"Collision with {entity.name}")
                        self.handle_building_collision()
                else:
                    # Allow movement if not colliding with a building
                    self.position = new_position
            else:
                self.position = new_position
        
        # Handle jumping with spacebar
        if self.can_jump:
            if held_keys['space'] and not self.jumping:
                self.jumping = True
                self.vertical_velocity = 5  # Initial upward velocity
            
            if self.jumping:
                # Apply gravity
                self.vertical_velocity -= self.gravity * time.dt
                
                # Update position
                self.y += self.vertical_velocity * time.dt
                
                # Check if we've landed
                if self.y <= 1:  # Ground level
                    self.y = 1
                    self.jumping = False
                    self.vertical_velocity = 0
        else:
            # Keep player at a constant height when not jumping
            self.y = 1

    def handle_building_collision(self):
        """Handle collision with buildings"""
        # Flash the player red
        self.original_color = self.color
        self.color = color.red
        invoke(self.reset_color, delay=0.2)
        
        # Reduce health
        self.health -= 1
        
        # Find the colliding building and highlight it
        hit_info = None
        for entity in scene.entities:
            if hasattr(entity, 'name') and ('building' in entity.name or 'obstacle' in entity.name):
                if self.intersects(entity).hit:
                    hit_info = self.intersects(entity)
                    # Highlight the colliding building
                    original_color = entity.color
                    entity.color = color.red
                    invoke(lambda e=entity, c=original_color: setattr(e, 'color', c), delay=1)
                    
                    # Print detailed collision info
                    print(f"Player hit building: {entity.name} at position {entity.position}")
                    print(f"Building model: {getattr(entity, 'model', 'unknown')}")
                    print(f"Building scale: {entity.scale}")
                    break
        
        if not hit_info:
            print(f"Building collision detected but couldn't find the specific building!")
        
        print(f"Player hit a building! Health: {self.health}")

        # --- Update UI --- 
        # Find the game instance to access the UI
        game_instance = None
        for entity in scene.entities:
            # Check if the entity is the main Game controller
            # Use a more specific check if possible (e.g., isinstance(entity, Game) if Game is imported)
            if hasattr(entity, 'ui') and hasattr(entity, 'player'): 
                game_instance = entity
                break
        
        if game_instance and game_instance.ui:
            game_instance.ui.set_health(self.health)
        # --- End UI Update ---
        
        # Check for game over
        if self.health <= 0:
            print("Game over - player health is zero")
            # Game over will be handled by the main game class
            # Look for the parent game object
            if game_instance:
                game_instance.game_over_sequence()
        
        # Apply knockback
        knockback_direction = -self.forward
        self.position += knockback_direction * 2  # Knock back 2 units

    def reset_color(self):
        """Reset player color after collision flash"""
        self.color = self.original_color

    def update_segments(self):
        # Record the player's position periodically
        self.segment_update_timer += time.dt
        if self.segment_update_timer >= self.segment_update_interval:
            self.segment_update_timer = 0
            # Use Vec3 constructor to create a copy instead of .copy() method
            self.previous_positions.append(Vec3(self.position.x, self.position.y, self.position.z))
            
            # Keep only the positions we need
            max_positions = len(self.segments) + 10
            while len(self.previous_positions) > max_positions:
                self.previous_positions.pop(0)
        
        # Update segment positions
        for i, segment in enumerate(self.segments):
            # Calculate the target position index
            position_index = len(self.previous_positions) - 1 - (i + 1) * 2
            
            # Make sure we don't go out of bounds
            if position_index >= 0:
                # Smooth movement
                segment.position = lerp(
                    segment.position, 
                    self.previous_positions[position_index], 
                    time.dt * 5
                )

    def grow(self):
        # Create a new segment matching player appearance
        new_segment = Entity(
            model='cube', 
            color=self.color,
            texture='brick',
            scale=(0.9, 0.9, 0.9),
            collider='box'
        )
        
        # Position it behind the last segment or the player
        if len(self.segments) == 0:
            new_segment.position = self.position - (self.forward * 1.2)
        else:
            new_segment.position = self.segments[-1].position - (self.forward * 0.8)
            
        self.segments.append(new_segment)
        self.length += self.growth_rate
        
        # Make snake slightly faster as it grows
        self.base_speed += 0.05
        self.speed = self.base_speed

    def handle_power_ups(self):
        """Handle active power-up effects"""
        # This is mostly handled by the Game class
        pass

    def reset(self):
        """Reset the player to initial state"""
        self.position = (0, 1, 0)
        self.rotation = (0, 0, 0) # Reset rotation as well
        self.length = 1
        
        # Clear all segments
        for segment in self.segments:
            destroy(segment)
        self.segments = []
        self.previous_positions = []
        
        # Reset attributes
        self.health = 3
        self.base_speed = 8
        self.speed = self.base_speed
        self.collision_cooldown = 0
        self.is_boosting = False # Reset boost state
        
        # Clear power-ups
        self.can_jump = False
        self.jumping = False
        self.vertical_velocity = 0 # Reset jump velocity
        self.has_shield = False
        if self.shield_entity:
            destroy(self.shield_entity)
            self.shield_entity = None
        
        # Reset color if it was changed during collision
        if hasattr(self, 'original_color'):
            self.color = self.original_color
        else:
            self.color = color.green # Default color
        
        # Reset alpha if invisible
        self.alpha = 1.0