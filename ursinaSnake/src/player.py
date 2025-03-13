from ursina import *

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'  # Use built-in model instead of 'snake'
        self.texture = 'white_cube'  # Use built-in texture
        self.color = color.green
        self.scale = (1, 1, 1)
        self.position = (0, 0, 0)
        self.speed = 5
        self.growth_rate = 0.1
        self.length = 1
        self.segments = []
        self.collider = 'box'  # Add collider

    def update(self):
        self.move()
        self.check_collisions()

    def move(self):
        if held_keys['w']:
            self.position += self.forward * self.speed * time.dt
        if held_keys['s']:
            self.position -= self.forward * self.speed * time.dt
        if held_keys['a']:
            self.rotation_y -= 100 * time.dt
        if held_keys['d']:
            self.rotation_y += 100 * time.dt

    def grow(self):
        new_segment = Entity(model='cube', color=color.green, scale=(1, 1, 1))
        new_segment.position = self.position
        self.segments.append(new_segment)
        self.length += self.growth_rate

    def check_collisions(self):
        # Placeholder for collision detection logic
        pass

    def reset(self):
        self.position = (0, 0, 0)
        self.length = 1
        self.segments.clear()