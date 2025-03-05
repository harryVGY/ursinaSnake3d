def random_position(grid_size):
    from random import randint
    return (randint(0, grid_size[0] - 1), randint(0, grid_size[1] - 1))

def check_collision(rect1, rect2):
    return (rect1.x < rect2.x + rect2.width and
            rect1.x + rect1.width > rect2.x and
            rect1.y < rect2.y + rect2.height and
            rect1.y + rect1.height > rect2.y)