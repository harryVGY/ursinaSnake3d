from ursina import *
import math

class CameraController(Entity):
    def __init__(self, target=None):
        super().__init__()
        self.camera_mode = 'first_person'
        self.distance = 10
        self.target = target
        
        # Lock mouse cursor
        mouse.locked = True
        mouse.visible = False
        
        # Set initial camera position and rotation
        if self.target:
            camera.position = self.target.position + Vec3(0, 1.7, 0)
            camera.rotation = self.target.rotation

    def update(self):
        if not self.target:
            return
            
        # Toggle camera modes with number keys
        if held_keys['1'] and self.camera_mode != 'third_person':
            self.camera_mode = 'third_person'
            print("Switched to third-person view")
            
        if held_keys['2'] and self.camera_mode != 'first_person':
            self.camera_mode = 'first_person'
            print("Switched to first-person view")

        # First-person view (camera attached to player)
        if self.camera_mode == 'first_person':
            camera.position = Vec3(
                self.target.x,
                self.target.y + 1.7,
                self.target.z
            )
            camera.rotation = self.target.rotation
            
        # Third-person view (camera follows behind player)
        elif self.camera_mode == 'third_person':
            # Fix the rotation issue by directly using player's rotation angle
            # Calculate exact position behind player based on rotation angle
            angle_in_radians = math.radians(self.target.rotation_y)
            
            # Position camera directly behind player based on their rotation
            camera_x = self.target.x - math.sin(angle_in_radians) * self.distance
            camera_z = self.target.z - math.cos(angle_in_radians) * self.distance
            
            # Set camera position with height above player
            camera.position = Vec3(camera_x, self.target.y + 5, camera_z)
            
            # Set camera rotation to match player's rotation for alignment
            # This ensures we're looking in the same direction
            target_rotation = Vec3(
                30,  # Looking down at a 30-degree angle 
                self.target.rotation_y,  # Match player's horizontal rotation
                0  # No roll
            )
            
            # Apply the rotation directly
            camera.rotation = target_rotation

def setup_camera(target=None):
    return CameraController(target)