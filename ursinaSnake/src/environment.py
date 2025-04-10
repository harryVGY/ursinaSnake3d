from ursina import *
from random import randint, uniform
import random
import os

class Environment(Entity):
    def __init__(self):
        super().__init__()
        print("Initializing environment...")
        self.create_ground()
        self.buildings = []  # Store buildings for reference
        self.building_models = self.load_building_models()
        self.create_city_layout()
        self.create_obstacles()

    def create_ground(self):
        # Create a large textured ground plane
        self.ground = Entity(
            model='plane',
            scale=(50, 1, 50),
            color=color.light_gray,
            texture='white_cube',
            texture_scale=(50, 50),
            collider='box'
        )
        self.ground.texture = 'grid'

    def load_building_models(self):
        """Load custom building models from assets folder"""
        building_models = {}
        
        # Get the path to the assets folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Primary location - models should be copied here by the script
        assets_model_path = os.path.join(
            parent_dir,
            "assets",
            "models", 
            "buildings",
            "building_H.obj"
        )
        
        # Fallback - try the downloads folder directly
        download_path = os.path.join(
            os.path.expanduser("~"), 
            "Downloads", 
            "KayKit_City_Builder_Bits_1.0_FREE",
            "KayKit_City_Builder_Bits_1.0_FREE",
            "Assets",
            "obj",
            "building_H.obj"
        )
        
        # Try the assets path first
        if os.path.exists(assets_model_path):
            building_models['building_h'] = assets_model_path
            print(f"Found building model in assets folder: {assets_model_path}")
        # Fallback to downloads path
        elif os.path.exists(download_path):
            building_models['building_h'] = download_path
            print(f"Found building model in downloads folder: {download_path}")
        else:
            print("Warning: No building models found!")
            print(f"Looked in: {assets_model_path}")
            print(f"And in: {download_path}")
        
        return building_models

    def create_city_layout(self):
        # Create a more varied city layout with different building types
        building_types = [
            {'scale': (2, randint(3, 8), 2), 'color': color.light_gray},
            {'scale': (3, randint(2, 5), 3), 'color': color.gray},
            {'scale': (2, randint(4, 10), 2), 'color': color.dark_gray},
            {'scale': (4, randint(3, 6), 4), 'color': color.rgba(0.6, 0.6, 0.7, 1)},
        ]
        
        # Place buildings on a grid but with slight positional variation
        for x in range(-20, 21, 8):
            for z in range(-20, 21, 8):
                # Skip some positions randomly for more natural layout
                if random.random() < 0.3:
                    continue
                    
                # Add variation to position
                pos_x = x + uniform(-1, 1)
                pos_z = z + uniform(-1, 1)
                
                # Decide whether to use a custom model or a cube
                use_custom_model = random.random() < 0.7 and 'building_h' in self.building_models
                
                if use_custom_model:
                    # Create building using the custom 3D model
                    try:
                        # Use the custom building model
                        model_path = self.building_models['building_h']
                        print(f"Creating building with model: {model_path}")
                        
                        # Create the building entity
                        building = Entity(
                            model=model_path,
                            position=(pos_x, 0, pos_z),  # Position at ground level
                            scale=2,  # Scale the model to appropriate size
                            name=f'building_{len(self.buildings)}',
                            color=color.white  # Use white to show texture properly
                        )
                        
                        # Add proper collision box
                        building.collider = 'box'
                        print(f"Created custom building at ({pos_x}, 0, {pos_z})")
                        
                        self.buildings.append(building)
                        
                    except Exception as e:
                        print(f"Error creating custom building: {e}")
                        # Fallback to cube if model loading fails
                        self._create_cube_building(pos_x, pos_z, building_types)
                else:
                    # Create a cube building as fallback
                    self._create_cube_building(pos_x, pos_z, building_types)
    
    def _create_cube_building(self, pos_x, pos_z, building_types):
        """Create a basic cube building (fallback method)"""
        # Select random building type
        building_type = random.choice(building_types)
        
        # Create the main building structure
        building = Entity(
            model='cube',
            color=building_type['color'],
            position=(pos_x, building_type['scale'][1]/2, pos_z),  # Position at half height
            scale=building_type['scale'],
            name=f'building_{len(self.buildings)}'
        )
        
        # Make sure it has a proper collider
        building.collider = 'box'
        
        # Add details to larger buildings
        if building_type['scale'][1] > 4:
            # Add windows
            window_color = color.azure
            
            for floor in range(1, int(building_type['scale'][1])):
                for side in range(4):
                    rotation = side * 90
                    window = Entity(
                        parent=building,
                        model='cube',
                        rotation_y=rotation,
                        position=(0, floor - building_type['scale'][1]/2 + 0.5, building_type['scale'][2]/2 - 0.1),
                        scale=(0.5, 0.5, 0.1),
                        color=window_color
                    )

            # Add roof details
            roof = Entity(
                parent=building,
                model='cube',
                position=(0, building_type['scale'][1]/2 + 0.1, 0),
                scale=(building_type['scale'][0], 0.2, building_type['scale'][2]),
                color=color.dark_gray
            )

        self.buildings.append(building)

    def create_obstacles(self):
        # Create dynamic obstacles in the environment
        for i in range(5):
            obstacle = Entity(
                model='cube',
                color=color.red, 
                position=(randint(-10, 10), 0.5, randint(-10, 10)),
                scale=(1, 1, 1),
                name=f'obstacle_{i}'  # Add unique name
            )
            # Ensure obstacles have proper colliders
            obstacle.collider = 'box'

    def update(self):
        # Update the environment dynamically if needed
        pass