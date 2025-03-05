class Game:
    def __init__(self):
        self.is_running = False

    def start(self):
        self.is_running = True
        self.update()

    def update(self):
        if self.is_running:
            # Update game state here
            pass

    def end(self):
        self.is_running = False
        # Handle end of game logic here