class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn_food()

    def spawn_food(self):
        import random
        self.position = (random.randint(0, 19), random.randint(0, 19))

    def check_if_eaten(self, snake_position):
        return self.position == snake_position