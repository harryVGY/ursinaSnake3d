from ursina import *

class UI(Entity):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.health = 3
        self.max_health = 3
        self.combo_count = 0
        self.active_powerups = {}

        # Score display - moved higher up on the screen
        self.score_text = Text(text=f'Score: {self.score}', position=(-0.85, 0.45), scale=2, color=color.white)

        # Health display text - moved higher up on the screen
        self.health_text = Text(text=f'Health: {self.health}', position=(-0.85, 0.4), scale=2, color=color.white)
        
        # Create health bar - moved lower to avoid overlapping with text
        self.health_bar_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.4, 0.05),
            position=(-0.7, 0.35),
            color=color.dark_gray
        )
        
        self.health_bar = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.4, 0.05),
            position=(-0.7, 0.35),
            color=color.red,
            origin=(-0.5, 0)  # Set origin to left side for proper scaling
        )
        
        # Combo counter
        self.combo_text = Text(
            text='',  # No combo at start
            position=(-0.85, 0.3),
            scale=1.8,
            color=color.rgba(1, 1, 0.6, 0),  # Start invisible
            origin=(0, 0)
        )
        
        # Power-up status area (top right)
        self.powerup_container = Entity(
            parent=camera.ui,
            position=(0.75, 0.4),
            scale=(0.2, 0.2),
            model='quad',
            color=color.clear,  # Invisible container
            z=-1
        )
        
        # Create empty power-up indicator slots
        self.powerup_indicators = {}
        
        # Game controls info (bottom of screen)
        self.controls_text = Text(
            text='WASD: Move | Mouse: Look | 1/2: Switch Camera | Space: Jump | Shift/Ctrl: Speed',
            position=(0, -0.45),
            origin=(0, 0),
            scale=1,
            color=color.light_gray
        )

    def update(self):
        # Update text displays
        self.score_text.text = f'Score: {self.score}'
        self.health_text.text = f'Health: {self.health}'
        
        # Update health bar width based on current health
        health_ratio = self.health / self.max_health
        self.health_bar.scale_x = max(0, 0.4 * health_ratio)  # Ensure bar doesn't go negative
        
        # Update combo display
        if self.combo_count > 1:
            self.combo_text.text = f'COMBO x{self.combo_count}'
            self.combo_text.color = color.rgba(1, 1, 0.6, 1)  # Make visible
            self.combo_text.scale = 1.8 + (self.combo_count * 0.05)  # Grow with combo size
        else:
            self.combo_text.color = color.rgba(1, 1, 0.6, 0)  # Hide when no combo

    def set_score(self, score):
        self.score = score

    def set_health(self, health):
        self.health = health
        # Flash the health bar red when damage is taken
        if health < self.health:
            self.health_bar.color = color.red
            self.health_bar.animate_color(color.color(1,0,0,1), duration=0.3)
    
    def set_combo(self, count, timeout=None):
        """Update the combo counter"""
        self.combo_count = count
        
        # Special effects for higher combos
        if count >= 5:
            # Create a quick flash effect
            flash = Entity(
                parent=camera.ui,
                model='quad',
                scale=(2, 2),
                color=color.rgba(1, 1, 0, 0.2),
                z=1
            )
            flash.animate_color(color.rgba(1, 1, 0, 0), duration=0.5)
            destroy(flash, delay=0.5)
            
            # Shake the combo text
            self.combo_text.animate_position(
                (-0.85 + random.uniform(-0.02, 0.02), 0.3 + random.uniform(-0.02, 0.02)),
                duration=0.1,
                curve=curve.linear
            )
            invoke(self.reset_combo_position, delay=0.1)
    
    def reset_combo_position(self):
        """Reset combo text position after shake effect"""
        self.combo_text.animate_position((-0.85, 0.3), duration=0.1)
    
    def update_powerup(self, powerup_type, active, duration=0):
        """Update a power-up indicator in the UI"""
        # Create power-up indicator if it doesn't exist
        if powerup_type not in self.powerup_indicators:
            y_pos = len(self.powerup_indicators) * -0.12  # Stack vertically
            
            # Get color based on power-up type
            if powerup_type == 'speed':
                color_value = color.yellow
                icon_text = "⚡"
            elif powerup_type == 'invisibility':
                color_value = color.azure
                icon_text = "👻"
            elif powerup_type == 'jump':
                color_value = color.lime
                icon_text = "⬆️"
            elif powerup_type == 'health':
                color_value = color.red
                icon_text = "❤️"
            else:
                color_value = color.white
                icon_text = "⭐"
            
            # Create the indicator elements
            indicator = Entity(
                parent=self.powerup_container,
                position=(0, y_pos),
                model='quad',
                texture='white_cube',
                scale=(1, 0.3),
                color=color.rgba(0.2, 0.2, 0.2, 0.8)
            )
            
            # Progress bar
            progress = Entity(
                parent=indicator,
                model='quad',
                scale=(1, 1),
                origin=(-0.5, 0),
                color=color_value.tint(-0.2),
                z=-0.01
            )
            
            # Icon and text
            icon = Text(
                parent=indicator,
                text=icon_text,
                position=(-0.4, 0),
                scale=2,
                origin=(0, 0)
            )
            
            label = Text(
                parent=indicator,
                text=powerup_type.capitalize(),
                position=(-0.1, 0),
                origin=(-0.5, 0),
                scale=1.5
            )
            
            # Store references
            self.powerup_indicators[powerup_type] = {
                'container': indicator,
                'progress': progress,
                'icon': icon,
                'label': label
            }
        
        # Update the indicator
        indicator_data = self.powerup_indicators[powerup_type]
        if active:
            # Show the indicator
            indicator_data['container'].enable()
            
            # Set the progress bar width based on remaining duration ratio
            if 'max_duration' not in indicator_data:
                indicator_data['max_duration'] = duration
                
            remaining_ratio = duration / indicator_data['max_duration']
            indicator_data['progress'].scale_x = max(0.05, remaining_ratio)
            
        else:
            # Hide the indicator
            indicator_data['container'].disable()
            # Reset max duration
            if 'max_duration' in indicator_data:
                del indicator_data['max_duration']
    
    def reset(self):
        """Reset UI elements for game restart"""
        self.score = 0
        self.health = self.max_health
        self.combo_count = 0
        self.set_score(0)
        self.set_health(self.max_health)
        # Reset health bar color and size
        self.health_bar.color = color.red
        self.health_bar.scale_x = 0.4
        
        # Reset combo display
        self.combo_text.color = color.rgba(1, 1, 0.6, 0)
        
        # Reset power-up indicators
        for powerup_type, indicator in self.powerup_indicators.items():
            indicator['container'].disable()