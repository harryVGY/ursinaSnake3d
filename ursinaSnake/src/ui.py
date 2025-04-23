from ursina import *

class UI(Entity):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.health = 3
        self.combo = 0
        self.active_power_up = None
        self.power_up_timer = 0

        # Score display
        self.score_text = Text(text=f'Score: {self.score}', position=(-0.85, 0.45), scale=1.5, color=color.white)

        # Health display
        self.health_text = Text(text=f'Health: {self.health}', position=(-0.85, 0.4), scale=1.5, color=color.white)
        
        # Combo display (initially hidden)
        self.combo_text = Text(text='', position=(-0.85, 0.35), scale=1.5, color=color.yellow)
        
        # Power-up display (initially hidden)
        self.power_up_text = Text(text='', position=(-0.85, 0.3), scale=1.5, color=color.cyan)
        
        # Game controls help
        self.controls_text = Text(text='WASD: Move | Mouse: Look | 1/2: Camera | Space: Use Power', 
                              position=(0, -0.45), origin=(0,0), scale=1, color=color.light_gray)

    def update(self):
        # Update power-up timer if active
        if self.active_power_up:
            self.power_up_timer -= time.dt
            if self.power_up_timer <= 0:
                self.active_power_up = None
                self.power_up_text.text = ''
            else:
                self.power_up_text.text = f'{self.active_power_up}: {self.power_up_timer:.1f}s'

    def set_score(self, score):
        self.score = score
        self.score_text.text = f'Score: {self.score}'

    def set_health(self, health):
        self.health = health
        self.health_text.text = f'Health: {self.health}'
        
        # Change color based on health
        if self.health <= 1:
            self.health_text.color = color.red
        elif self.health == 2:
            self.health_text.color = color.yellow
        else:
            self.health_text.color = color.white
    
    def set_combo(self, combo):
        self.combo = combo
        
        # Only show combo text if combo is active
        if combo > 1:
            self.combo_text.text = f'Combo: x{self.combo}'
            # Make combo text pulse and change color based on combo level
            if combo >= 5:
                self.combo_text.color = color.rgb(255, 100, 0)  # Orange
                self.animate_combo_text(1.5)
            elif combo >= 3:
                self.combo_text.color = color.yellow
                self.animate_combo_text(1.3)
            else:
                self.combo_text.color = color.white
                self.combo_text.scale = 1.5
        else:
            self.combo_text.text = ''
    
    def animate_combo_text(self, target_scale):
        # Create pulsing animation for high combos
        self.combo_text.animate_scale(target_scale, duration=0.3, curve=curve.out_bounce)
        invoke(self.reset_combo_text_scale, delay=0.3)
    
    def reset_combo_text_scale(self):
        self.combo_text.animate_scale(1.5, duration=0.3)
    
    def set_power_up(self, power_type, duration):
        self.active_power_up = power_type.capitalize()
        self.power_up_timer = duration
        
        # Set color based on power-up type
        if power_type == 'speed':
            self.power_up_text.color = color.yellow
        elif power_type == 'invisible':
            self.power_up_text.color = color.cyan
        elif power_type == 'jump':
            self.power_up_text.color = color.magenta
        elif power_type == 'shield':
            self.power_up_text.color = color.azure