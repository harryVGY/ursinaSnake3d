def random_position(bounds):
    from random import uniform
    x = uniform(-bounds, bounds)
    y = uniform(-bounds, bounds)
    return (x, y)

def check_collision(entity1, entity2):
    return entity1.intersects(entity2).hit

def load_texture(texture_path):
    from ursina import load_texture
    return load_texture(texture_path)

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def distance_between(point1, point2):
    from math import sqrt
    return sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)