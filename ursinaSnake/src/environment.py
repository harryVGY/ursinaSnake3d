from ursina import *
from random import randint

class Environment(Entity):
    def __init__(self):
        super().__init__()
        self.create_ground()  # Add this line
        self.create_city_layout()
        self.create_obstacles()

    def create_ground(self):
        # Create a large textured ground plane
        self.ground = Entity(
            model='plane',
            scale=(50, 1, 50),
            color=color.light_gray,
            texture='white_cube',
            texture_scale=(50, 50),
            collider='box'
        )
        
        # You can use a built-in texture or add your own
        # For a more interesting look:
        # self.ground.texture = 'grass'  # Use built-in grass texture
        # Or create a grid pattern:
        self.ground.texture = 'grid'

    def create_city_layout(self):
        # Create a simple city layout with buildings
        for x in range(-10, 11, 5):
            for z in range(-10, 11, 5):
                building = Entity(model='cube', color=color.gray, position=(x, 1.5, z), scale=(1, 3, 1))
                building.collider = 'box'

    def create_obstacles(self):
        # Create dynamic obstacles in the environment
        for _ in range(5):
            obstacle = Entity(model='cube', color=color.red, position=(randint(-10, 10), 0, randint(-10, 10)), scale=(1, 1, 1))
            obstacle.collider = 'box'

    def update(self):
        # Update the environment dynamically if needed
        pass

# This file is intentionally left blank.