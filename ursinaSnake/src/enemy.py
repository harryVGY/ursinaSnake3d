from ursina import Entity, color, Vec3, time  # Added time import
import random

class Enemy(Entity):
    def __init__(self, position=(0, 0, 0), model='cube', texture='white_cube', scale=1):
        super().__init__()
        self.model = model
        self.texture = 'brick'  # Better texture
        self.color = color.red
        self.scale = scale
        # Ensure all enemies are at the same height as player for collisions
        self.position = Vec3(position[0], 1, position[2])
        self.speed = random.uniform(1, 3)
        self.direction = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1])).normalized()
        # Make sure collider is properly set
        self.collider = 'box'

    def update(self):
        self.position += self.direction * self.speed * time.dt
        
        # Change direction if hitting a wall (simple boundary check)
        if abs(self.x) > 10 or abs(self.z) > 10:
            self.direction = -self.direction  # Reverse direction

    @classmethod
    def spawn(cls, count):
        enemies = []
        for _ in range(count):
            position = (random.uniform(-10, 10), 0, random.uniform(-10, 10))
            enemy = cls(position=position)
            enemies.append(enemy)
        return enemies