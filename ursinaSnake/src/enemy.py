from ursina import Entity, color, Vec3, time, distance  # Added distance import
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
        
        # Change direction if hitting a wall (use larger boundaries)
        boundary = 24  # Match closer to ground plane size
        if abs(self.x) > boundary or abs(self.z) > boundary:
            # Reverse direction and move slightly away from boundary
            self.position -= self.direction * self.speed * time.dt * 2  # Move back slightly
            self.direction = -self.direction
            # Optional: Add slight random change to direction to prevent getting stuck
            self.direction.x += random.uniform(-0.1, 0.1)
            self.direction.z += random.uniform(-0.1, 0.1)
            self.direction = self.direction.normalized()

    @classmethod
    def spawn(cls, count, player_pos=None):
        enemies = []
        for _ in range(count):
            # Ensure enemies spawn away from the player
            while True:
                position = (random.uniform(-20, 20), 1, random.uniform(-20, 20))
                if player_pos is None or distance(Vec3(*position), player_pos) > 5:
                    break
            enemy = cls(position=position)
            enemies.append(enemy)
        return enemies