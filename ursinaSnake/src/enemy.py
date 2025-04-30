from ursina import *
import random
import math

class Enemy(Entity):
    # Define different enemy types
    TYPES = {
        'crawler': {
            'color': color.red,
            'scale': 1,
            'speed': 3,
            'points': 1,
            'model': 'cube',
            'behavior': 'patrol'
        },
        'runner': {
            'color': color.orange,
            'scale': 0.8,
            'speed': 6,
            'points': 2,
            'model': 'cube',
            'behavior': 'chase'
        },
        'guardian': {
            'color': color.magenta,
            'scale': 1.2,
            'speed': 2,
            'points': 3,
            'model': 'cube',
            'behavior': 'guard'
        },
        'floater': {
            'color': color.cyan,
            'scale': 0.9,
            'speed': 4,
            'points': 4,
            'model': 'sphere',
            'behavior': 'wander'
        }
    }

    def __init__(self, position=(0, 0, 0), enemy_type=None):
        # If no specific type provided, choose random type
        if not enemy_type:
            enemy_type = random.choice(list(Enemy.TYPES.keys()))
        
        self.enemy_type = enemy_type
        self.config = Enemy.TYPES[enemy_type]
        
        # Initialize entity
        super().__init__()
        self.model = self.config['model']
        self.color = self.config['color']
        self.texture = 'brick'  # Better texture
        self.scale = self.config['scale']
        
        # Ensure all enemies are at the same height as player for collisions
        self.position = Vec3(position[0], 1, position[2])
        self.speed = self.config['speed'] * random.uniform(0.8, 1.2)  # Add some variation
        self.points = self.config['points']
        
        # Set behavior
        self.behavior = self.config['behavior']
        self.direction = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1])).normalized()
        
        # Make sure collider is properly set
        self.collider = 'box'
        
        # Additional properties based on type
        self.patrol_waypoints = []
        self.current_waypoint = 0
        self.guard_position = None
        self.guard_radius = random.uniform(5, 10)
        self.target = None
        self.detection_range = 15
        self.time_alive = 0
        
        # Initialize next_direction_change for all enemies
        self.next_direction_change = random.uniform(1, 3)
        
        # Initialize behavior specific properties
        self.setup_behavior()
        
        # Visual enhancements
        self.setup_visual_effects()

    def setup_behavior(self):
        """Setup behavior-specific properties"""
        if self.behavior == 'patrol':
            # Create waypoints in a loop
            self.create_patrol_route()
        
        elif self.behavior == 'guard':
            # Set guarding position
            self.guard_position = Vec3(self.position.x, 1, self.position.z)
        
        elif self.behavior == 'chase':
            # Will find player at runtime
            pass
        
        elif self.behavior == 'wander':
            # Will randomly change direction
            self.next_direction_change = random.uniform(1, 3)

    def create_patrol_route(self):
        """Create a patrol route for this enemy"""
        center_x = self.position.x
        center_z = self.position.z
        points = random.randint(3, 6)  # Number of patrol points
        
        for i in range(points):
            # Create points in a rough circle
            angle = math.radians(i * (360 / points))
            radius = random.uniform(5, 10)
            x = center_x + radius * math.cos(angle)
            z = center_z + radius * math.sin(angle)
            
            self.patrol_waypoints.append(Vec3(x, 1, z))

    def setup_visual_effects(self):
        """Add visual enhancements based on enemy type"""
        # Different visual effects based on enemy type
        if self.enemy_type == 'floater':
            # Floater enemy hovers and has a pulsing effect
            self.y = 1.5  # Make it float higher
            
            # Bobbing animation - fixed to use supported parameters
            self.animate_y(
                self.y + 0.5,
                duration=1.5,
                curve=curve.in_out_sine,
                loop=True
            )
            
            # Pulsing scale animation
            self.animate_scale(
                Vec3(1.2, 1.2, 1.2),
                duration=1,
                curve=curve.in_out_sine,
                loop=True
            )
            
        elif self.enemy_type == 'runner':
            # Runner enemy leaves particles when moving
            # Create a simple particle effect without using repeat parameter
            self.particle_timer = 0
            
        elif self.enemy_type == 'guardian':
            # Guardian has a shield-like outline
            self.shield = Entity(
                parent=self,
                model='sphere',
                scale=1.5,
                color=color.rgba(1, 1, 1, 0.2),
                double_sided=True
            )
            
            # Pulse the shield - fixed to use supported parameters
            self.shield.animate_scale(
                Vec3(1.7, 1.7, 1.7),
                duration=1.5,
                curve=curve.in_out_sine,
                loop=True
            )
            
    def create_movement_particle(self):
        """Create a particle at the runner's position to simulate trail effect"""
        if self.enemy_type == 'runner':
            particle = Entity(
                model='sphere',
                color=self.color.tint(-.2),
                position=self.position + Vec3(0, 0.1, 0),
                scale=0.3
            )
            particle.animate_scale(0, duration=0.5)
            particle.animate_color(color.clear, duration=0.5)
            destroy(particle, delay=0.5)

    def update(self):
        self.time_alive += time.dt
        
        if self.behavior == 'patrol':
            self.patrol_behavior()
        elif self.behavior == 'guard':
            self.guard_behavior()
        elif self.behavior == 'chase':
            self.chase_behavior()
        elif self.behavior == 'wander':
            self.wander_behavior()
            
        # Add a subtle hover/bob to all enemies
        self.y = 1 + math.sin(self.time_alive * 2) * 0.1
        
        # Handle particle creation for runner type
        if self.enemy_type == 'runner':
            self.particle_timer -= time.dt
            if self.particle_timer <= 0:
                self.create_movement_particle()
                self.particle_timer = 0.1  # Create particle every 0.1 seconds
        
    def find_player(self):
        """Find player in the scene"""
        for entity in scene.entities:
            if hasattr(entity, 'name') and entity.name == 'player':
                return entity
        return None

    def patrol_behavior(self):
        """Move between patrol waypoints"""
        if not self.patrol_waypoints:
            return
            
        # Get current target waypoint
        target = self.patrol_waypoints[self.current_waypoint]
        
        # Move towards waypoint
        direction = (target - self.position).normalized()
        direction.y = 0  # Keep y movement zero
        self.position += direction * self.speed * time.dt
        
        # Look towards movement direction
        self.look_at_2d(target)
        
        # Check if reached waypoint
        distance = (target - self.position).length()
        if distance < 1:
            # Move to next waypoint
            self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_waypoints)

    def guard_behavior(self):
        """Guard an area and chase if player comes close"""
        player = self.find_player()
        if not player:
            return
            
        # Check if player is within guarding radius
        player_distance = (player.position - self.guard_position).length()
        
        if player_distance < self.guard_radius:
            # Player is in guarded area, chase them!
            direction = (player.position - self.position).normalized()
            direction.y = 0
            self.position += direction * self.speed * time.dt
            self.look_at_2d(player.position)
        else:
            # Return to guard position
            direction = (self.guard_position - self.position).normalized()
            direction.y = 0
            
            # Only move if not already at guard position
            if (self.position - self.guard_position).length() > 0.5:
                self.position += direction * self.speed * time.dt
                self.look_at_2d(self.guard_position)

    def chase_behavior(self):
        """Actively chase the player"""
        player = self.find_player()
        if not player:
            # If no player found, wander
            self.wander_behavior()
            return
            
        # Check if player is within detection range
        player_distance = (player.position - self.position).length()
        
        if player_distance < self.detection_range:
            # Chase player
            direction = (player.position - self.position).normalized()
            direction.y = 0
            self.position += direction * self.speed * time.dt
            self.look_at_2d(player.position)
        else:
            # Wander if player is too far
            self.wander_behavior()

    def wander_behavior(self):
        """Move randomly, occasionally changing direction"""
        # Check if it's time to change direction
        self.next_direction_change -= time.dt
        if self.next_direction_change <= 0:
            # Choose new random direction
            self.direction = Vec3(
                random.uniform(-1, 1),
                0,
                random.uniform(-1, 1)
            ).normalized()
            self.next_direction_change = random.uniform(1, 3)
            
        # Apply movement
        self.position += self.direction * self.speed * time.dt
        self.look_at_2d(self.position + self.direction)
        
        # Boundary check - reverse direction if hitting boundaries
        if abs(self.x) > 24 or abs(self.z) > 24:
            self.direction = -self.direction
            self.look_at_2d(self.position + self.direction)

    def look_at_2d(self, target_pos):
        """Look at target but only in the y-axis rotation"""
        direction = target_pos - self.position
        self.rotation_y = math.degrees(math.atan2(direction.z, direction.x)) + 90
        
    def on_disable(self):
        """Called when the enemy is disabled (eaten by snake)"""
        # Create particle effect when eaten
        for _ in range(10):
            particle = Entity(
                model='sphere',
                color=self.color,
                position=self.position,
                scale=0.2,
                lifetime=1
            )
            # Random direction particle burst
            particle.animate_position(
                self.position + Vec3(
                    random.uniform(-2, 2),
                    random.uniform(0, 2),
                    random.uniform(-2, 2)
                ),
                duration=0.5
            )
            particle.animate_scale(0, duration=0.5)
            destroy(particle, delay=0.5)