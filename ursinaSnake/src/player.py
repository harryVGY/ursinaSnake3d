from ursina import *

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'
        self.texture = 'brick'
        self.color = color.green
        self.scale = (1, 1, 1)
        self.position = (0, 1, 0)
        self.speed = 8  # Increased from 5 for faster movement
        self.growth_rate = 0.1
        self.length = 1
        self.segments = []
        self.collider = 'box'
        self.mouse_sensitivity = 100  # Significantly increased for better responsiveness
        
        print("Player initialized - press WASD to move, mouse to look, 1/2 to switch views")

    def update(self):
        self.handle_movement()
        self.update_segments()
        self.check_collisions()

    def handle_movement(self):
        # Simple, direct mouse look with high sensitivity
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity * time.dt
        
        # Movement without complex collision detection for now
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
            
            if hit_info.hit:
                # Print collision information for debugging
                print(f"Collision detected with: {hit_info.entity.name if hasattr(hit_info.entity, 'name') else 'unknown'}")
            else:
                self.position = new_position
        
        # Keep player at a constant height
        self.y = 1

    def update_segments(self):
        if len(self.segments) > 0:
            # Update segment positions to follow the player
            prev_pos = self.position
            for segment in self.segments:
                curr_pos = segment.position
                segment.position = lerp(segment.position, prev_pos, time.dt * 5)
                prev_pos = curr_pos

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
        # Placeholder for collision detection logic
        pass

    def reset(self):
        self.position = (0, 0, 0)
        self.length = 1
        self.segments.clear()