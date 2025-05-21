from ursina import *
import math
from math import radians, sin, cos

class CameraController(Entity):
    def __init__(self, target=None):
        super().__init__()
        self.target = target
        self.distance = 15    # behind distance
        self.height = 10      # above target
        self.smoothing = 8    # smooth follow speed
        # If in Normal mode, parent the camera directly for rigid follow
        if self.target and hasattr(self.target, 'crazy_mode') and not self.target.crazy_mode:
            from ursina import camera, Vec3
            camera.parent = self.target
            camera.position = Vec3(0, self.height, -self.distance)
            camera.rotation = Vec3(30, 0, 0)
            self.normal_fixed = True
            return
        else:
            self.normal_fixed = False
        # initialize camera position
        if self.target:
            self._update_position(initial=True)

    def update(self):
        if not self.target:
            return
        # Skip smoothing update in Normal mode (rigid follow)
        if getattr(self, 'normal_fixed', False):
            return
        # always third-person follow
        self._update_position()

    def _update_position(self, initial=False):
        from ursina import camera, Vec3, lerp, time
        # calculate ideal position based on game mode
        if hasattr(self.target, 'crazy_mode') and not self.target.crazy_mode:
            # normal mode: fixed behind along world -Z axis
            ideal = Vec3(
                self.target.x,
                self.target.y + self.height,
                self.target.z - self.distance
            )
        else:
            # crazy mode or no mode flag: rotate around snake orientation
            angle = radians(self.target.rotation_y)
            ideal = Vec3(
                self.target.x - sin(angle)*self.distance,
                self.target.y + self.height,
                self.target.z - cos(angle)*self.distance
            )
        if initial:
            camera.position = ideal
        else:
            camera.position = lerp(camera.position, ideal, time.dt * self.smoothing)
        camera.look_at(self.target.position + Vec3(0,2,0))


def setup_camera(target=None):
    return CameraController(target)