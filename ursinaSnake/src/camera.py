from ursina import *
import math

class CameraController(Entity):
    def __init__(self, target=None):
        super().__init__()
        self.camera_mode = 'first_person'
        self.distance = 10
        self.rotation_speed = 5
        self.target = target

    def update(self):
        if not self.target:
            return

        if held_keys['1']:
            self.camera_mode = 'third_person'
        elif held_keys['2']:
            self.camera_mode = 'first_person'

        if self.camera_mode == 'third_person':
            camera.position = (
                self.target.x + self.distance * math.sin(math.radians(camera.rotation_y)),
                self.target.y + 5,
                self.target.z + self.distance * math.cos(math.radians(camera.rotation_y))
            )
            camera.look_at(self.target)
        elif self.camera_mode == 'first_person':
            camera.position = Vec3(self.target.x, self.target.y + 1.5, self.target.z)
            camera.rotation_y += held_keys['d'] * self.rotation_speed - held_keys['a'] * self.rotation_speed

def setup_camera(target=None):
    camera_controller = CameraController(target)
    return camera_controller