from ursina import *
import math
from math import radians, sin, cos

class CameraController(Entity):
    def __init__(self, target=None):
        super().__init__()
        self.target = target
        self.distance = 15    # behind distance
        self.height = 8       # lowered from 10 to 8 for better visibility with shorter buildings
        self.smoothing = 8    # smooth follow speed
        self.view_mode = 'third_person'  # default view mode
        
        # View mode settings
        self.third_person_settings = {
            'distance': 15,
            'height': 8,
            'offset': Vec3(0, 2, 0)  # Where to look at (slightly above player)
        }
        
        self.first_person_settings = {
            'height': 0.5,    # Slightly above player center
            'offset': Vec3(0, 0, 0)  # Look straight ahead
        }
        
        # Initialize camera position
        if self.target:
            self._update_position(initial=True)

    def update(self):
        if not self.target:
            return
            
        # Update camera position based on current view mode
        self._update_position()
        
    def _update_position(self, initial=False):
        # Calculate ideal position based on view mode
        if self.view_mode == 'first_person':
            # First-person view
            ideal_pos = self.target.position + Vec3(0, self.first_person_settings['height'], 0)
            if initial:
                camera.position = ideal_pos
            else:
                camera.position = lerp(camera.position, ideal_pos, time.dt * self.smoothing)
                
            # Make camera follow player rotation
            camera.rotation = self.target.rotation
            
        else:  # Third-person view
            # Find the position behind the player
            if hasattr(self.target, 'crazy_mode') and not self.target.crazy_mode:
                # normal mode: fixed behind along world -Z axis
                ideal = Vec3(
                    self.target.x,
                    self.target.y + self.third_person_settings['height'],
                    self.target.z - self.third_person_settings['distance']
                )
            else:
                # crazy mode or no mode flag: rotate around snake orientation
                angle = radians(self.target.rotation_y)
                ideal = Vec3(
                    self.target.x - sin(angle) * self.third_person_settings['distance'],
                    self.target.y + self.third_person_settings['height'],
                    self.target.z - cos(angle) * self.third_person_settings['distance']
                )
                
            if initial:
                camera.position = ideal
            else:
                camera.position = lerp(camera.position, ideal, time.dt * self.smoothing)
                
            # Look at player's position plus an offset
            camera.look_at(self.target.position + self.third_person_settings['offset'])
    
    def toggle_view_mode(self):
        """Toggle between first and third person views"""
        if self.view_mode == 'third_person':
            self.view_mode = 'first_person'
            print("Switched to first-person view")
        else:
            self.view_mode = 'third_person'
            print("Switched to third-person view")
            
    def set_mode(self, mode):
        """Set a specific view mode"""
        if mode in ['first_person', 'third_person']:
            self.view_mode = mode
            print(f"Set view to {mode}")

def setup_camera(target=None):
    return CameraController(target)