from ursina import *
import math

class CameraController(Entity):
    def __init__(self, target=None):
        super().__init__()
        self.camera_mode = 'first_person'
        self.distance = 10
        self.rotation_speed = 5
        self.target = target
        self.smoothing = 8  # Add smoothing factor
        self.target_position = Vec3(0,0,0)
        
        # Lock mouse cursor
        mouse.locked = True
        mouse.visible = False

    def update(self):
        if not self.target:
            return

        # Toggle camera modes
        if held_keys['1']:
            self.camera_mode = 'third_person'
        elif held_keys['2']:
            self.camera_mode = 'first_person'

        # Smoothly update target position to reduce flickering
        self.target_position = lerp(
            self.target_position, 
            self.target.position, 
            time.dt * self.smoothing
        )

        if self.camera_mode == 'third_person':
            # Fixed third-person camera - calculate position behind player
            # Use player's forward direction instead of rotation_y
            angle_in_radians = math.radians(self.target.rotation_y)
            offset_x = -math.sin(angle_in_radians) * self.distance
            offset_z = -math.cos(angle_in_radians) * self.distance
            
            target_camera_pos = Vec3(
                self.target_position.x + offset_x,
                self.target_position.y + 3,  # Camera height
                self.target_position.z + offset_z
            )
            
            # Apply smoothing to camera position
            camera.position = lerp(
                camera.position, 
                target_camera_pos, 
                time.dt * self.smoothing
            )
            
            # Look at player position plus a small offset in their look direction
            # This makes the camera look slightly ahead of the player
            forward_offset = self.target.forward * 2
            look_at_pos = Vec3(
                self.target_position.x + forward_offset.x,
                self.target_position.y + 1,  # Look at head level
                self.target_position.z + forward_offset.z
            )
            
            camera.look_at(look_at_pos)
        
        elif self.camera_mode == 'first_person':
            # Keep first-person view the same
            camera.position = Vec3(
                self.target.x, 
                self.target.y + 1.5, 
                self.target.z
            )
            camera.rotation = self.target.rotation

def setup_camera(target=None):
    camera_controller = CameraController(target)
    return camera_controller