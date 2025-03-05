class Snake:
    def __init__(self):
        self.body = [(0, 0)]
        self.direction = (1, 0)  # Initially moving right
        self.grow = False

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        opposite_direction = (-self.direction[0], -self.direction[1])
        if new_direction != opposite_direction:
            self.direction = new_direction

    def grow_snake(self):
        self.grow = True

    def check_collision(self, position):
        return position in self.body[1:]  # Check if the head collides with the body

    def get_head_position(self):
        return self.body[0]