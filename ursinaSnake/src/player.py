from ursina import *

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'
        self.texture = 'brick'  # Better texture
        self.color = color.green
        self.scale = (1, 1, 1)
        self.position = (0, 1, 0)  # Start slightly above ground
        self.speed = 5
        self.growth_rate = 0.1
        self.length = 1
        self.segments = []
        self.collider = 'box'
        self.mouse_sensitivity = 40  # Mouse sensitivity

    def update(self):
        self.handle_movement()
        self.update_segments()
        self.check_collisions()

    def handle_movement(self):
        # Mouse look control
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity * time.dt
        
        # WASD movement relative to facing direction
        move_direction = Vec3(0, 0, 0)
        
        if held_keys['w']:
            move_direction += self.forward
        if held_keys['s']:
            move_direction -= self.forward
        if held_keys['a']:
            move_direction -= self.right
        if held_keys['d']:
            move_direction += self.right
            
        # Normalize to prevent diagonal movement being faster
        if move_direction.length() > 0:
            move_direction = move_direction.normalized()
            
        # Apply movement
        self.position += move_direction * self.speed * time.dt
        
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