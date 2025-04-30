from ursina import *
import random

class PowerUp(Entity):
    """Power-up items that can be collected by the player for special abilities"""
    
    TYPES = {
        'speed': {
            'color': color.yellow,
            'duration': 10.0,
            'description': 'Speed Boost: Move 50% faster!',
            'model': 'sphere'
        },
        'invisibility': {
            'color': color.azure,
            'duration': 5.0,
            'description': 'Invisibility: Pass through buildings!',
            'model': 'sphere'
        },
        'jump': {
            'color': color.lime,
            'duration': 15.0,
            'description': 'Jump: Press SPACE to leap over obstacles!',
            'model': 'sphere'
        },
        'health': {
            'color': color.red,
            'duration': 0,  # Instant effect
            'description': 'Health: Restore 1 health point!',
            'model': 'sphere'
        }
    }
    
    def __init__(self, position=(0,0,0), powerup_type=None):
        # If no specific type provided, choose random type
        if not powerup_type:
            powerup_type = random.choice(list(PowerUp.TYPES.keys()))
        
        self.powerup_type = powerup_type
        self.config = PowerUp.TYPES[powerup_type]
        
        super().__init__(
            model=self.config['model'],
            color=self.config['color'],
            scale=1,
            position=position,
            collider='sphere'
        )
        
        # Add floating animation
        self.y = 1  # Float at player height
        self.original_y = self.y
        
        # Add rotation animation
        self.animate_rotation_y(360, duration=4, loop=True)
        
        # Add bobbing animation - fixed to use supported parameters
        self.animate_y(
            self.y + 0.5,
            duration=1,
            curve=curve.in_out_sine,
            loop=True
        )
        
        # Text indicator showing power-up type
        self.indicator = Text(
            text=self.config['description'],
            parent=self,
            billboard=True,
            scale=10,
            y=1.5,
            color=self.config['color']
        )
        
    def update(self):
        # Make the power-up rotate to be more visible
        self.rotation_y += 100 * time.dt
        
    def on_collect(self, player):
        """Called when player collects this power-up"""
        # Apply power-up effect to player
        duration = self.config['duration']
        player.apply_powerup(self.powerup_type, duration)
        
        # Play collection animation
        self.disable()  # Hide the power-up
        
        # Create particle effect
        for _ in range(20):
            particle = Entity(
                model='sphere',
                color=self.config['color'],
                position=self.position,
                scale=0.1,
                lifetime=1
            )
            # Random direction particle burst
            direction = Vec3(
                random.uniform(-1, 1),
                random.uniform(0.5, 1),  # Upward bias
                random.uniform(-1, 1)
            ).normalized()
            particle.animate_position(
                self.position + (direction * random.uniform(2, 5)),
                duration=0.5,
                curve=curve.out_expo
            )
            particle.animate_scale(0, duration=0.5)
            destroy(particle, delay=0.5)
        
        # Schedule destruction after effects finish
        destroy(self, delay=1)