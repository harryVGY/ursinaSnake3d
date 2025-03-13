from ursina import *

class UI(Entity):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.health = 3

        # Score display
        self.score_text = Text(text=f'Score: {self.score}', position=(-0.9, 0.4), scale=2, color=color.white)

        # Health display
        self.health_text = Text(text=f'Health: {self.health}', position=(-0.9, 0.35), scale=2, color=color.white)

    def update(self):
        self.score_text.text = f'Score: {self.score}'
        self.health_text.text = f'Health: {self.health}'

    def set_score(self, score):
        self.score = score

    def set_health(self, health):
        self.health = health