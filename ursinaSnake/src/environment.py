from ursina import *
from random import randint, uniform
import random
import os
import shutil
import math

# Define the base path for KayKit assets relative to the project root
KAYKIT_ASSETS_RELATIVE_PATH = os.path.join("KayKit_City_Builder_Bits_1.0_FREE", "Assets")

class Environment(Entity):
    def __init__(self):
        super().__init__()
        print("Initializing environment...")
        
        # Get the base directory of the script to build absolute paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.script_dir)
        self.assets_root = os.path.join(self.project_root, "assets")
        self.kaykit_base_path = os.path.abspath(os.path.join(self.project_root, KAYKIT_ASSETS_RELATIVE_PATH))
        
        self.create_ground()
        self.buildings = []  # Store buildings for reference
        self.dynamic_elements = []  # Initialize dynamic_elements list before using it
        self.building_models, self.building_texture = self.load_building_assets() # Load models and texture
        self.create_city_layout()
        # Lower buildings by 50% (shift vertically, not scale)
        for building in self.buildings:
            building.y *= 0.5
        self.create_obstacles()
        self.create_dynamic_elements()

    def create_ground(self):
        # Create a large textured ground plane
        ground_texture_path = os.path.join(self.assets_root, "textures", "ground_texture.png") 
        # Fallback texture if the specific one doesn't exist
        ground_texture = 'grass'  # Use a built-in texture or a known good one
        
        if os.path.exists(ground_texture_path):
            ground_texture = load_texture(ground_texture_path)
        else:
            print(f"Warning: Ground texture not found at {ground_texture_path}. Using fallback.")

        self.ground = Entity(
            model='plane',
            scale=(50, 1, 50),
            texture=ground_texture, 
            texture_scale=(10, 10),
            collider='box'
        )

    def load_building_assets(self):
        """Load custom building models and the shared texture from assets folder, copying if necessary."""
        building_models = {}
        building_texture = None

        # Destination path for models within the project's assets
        dest_model_path = os.path.join(self.assets_root, "models", "buildings")
        os.makedirs(dest_model_path, exist_ok=True)

        # Source path for KayKit OBJ models and texture
        kaykit_obj_path = os.path.join(self.kaykit_base_path, "obj")
        print(f"Looking for KayKit assets in: {kaykit_obj_path}")

        # --- Texture Handling ---
        texture_filename = "citybits_texture.png"
        dest_texture_path = os.path.join(dest_model_path, texture_filename)
        source_texture_path = os.path.join(kaykit_obj_path, texture_filename)

        # Check if texture exists, copy if needed
        if not os.path.exists(dest_texture_path):
            if os.path.exists(source_texture_path):
                try:
                    shutil.copy2(source_texture_path, dest_texture_path)
                    print(f"Copied texture from {source_texture_path} to {dest_texture_path}")
                except Exception as e:
                    print(f"Error copying texture: {e}")
            else:
                print(f"Warning: Texture not found at {source_texture_path}")

        # Try to load the texture
        if os.path.exists(dest_texture_path):
            try:
                # Try loading texture with absolute path first
                building_texture = load_texture(dest_texture_path)
                print(f"Successfully loaded building texture from: {dest_texture_path}")
            except Exception as e:
                print(f"Error loading texture with absolute path: {e}")
                # Try with relative path
                try:
                    # Use direct path from assets folder 
                    building_texture = load_texture('citybits_texture.png', path=os.path.join(self.assets_root, "models", "buildings"))
                    print(f"Successfully loaded texture with path parameter")
                except Exception as e:
                    print(f"Error loading texture with path parameter: {e}")
                    # Last attempt with built-in texture
                    building_texture = 'white_cube'  # Fallback to a built-in texture
                    print(f"Using fallback white_cube texture")
        else:
            print(f"Warning: Building texture not found at {dest_texture_path}")
            building_texture = 'white_cube'  # Fallback to a built-in texture

        # --- Model Handling ---
        building_types = ["building_A", "building_B", "building_C", "building_D",
                         "building_E", "building_F", "building_G", "building_H"]
        
        # Try to copy all building models and their MTL files
        for building_type in building_types:
            model_filename = f"{building_type}.obj"
            mtl_filename = f"{building_type}.mtl"
            
            dest_model_file = os.path.join(dest_model_path, model_filename)
            dest_mtl_file = os.path.join(dest_model_path, mtl_filename)
            
            source_model_file = os.path.join(kaykit_obj_path, model_filename)
            source_mtl_file = os.path.join(kaykit_obj_path, mtl_filename)
            
            # Copy model if needed
            if not os.path.exists(dest_model_file) and os.path.exists(source_model_file):
                try:
                    shutil.copy2(source_model_file, dest_model_file)
                    print(f"Copied model {model_filename} to {dest_model_path}")
                except Exception as e:
                    print(f"Error copying model {model_filename}: {e}")
            
            # Copy MTL if needed
            if not os.path.exists(dest_mtl_file) and os.path.exists(source_mtl_file):
                try:
                    shutil.copy2(source_mtl_file, dest_mtl_file)
                    print(f"Copied MTL {mtl_filename} to {dest_model_path}")
                except Exception as e:
                    print(f"Error copying MTL {mtl_filename}: {e}")
            
            # Add to models dict if the OBJ file exists in the destination
            if os.path.exists(dest_model_file):
                relative_model_path = os.path.join("assets", "models", "buildings", model_filename)
                building_models[building_type.lower()] = relative_model_path
                print(f"Found {building_type} model at {dest_model_file}")
        
        if not building_models:
            print("Warning: No building models found. Will use fallback cubes.")
        else:
            print(f"Successfully found {len(building_models)} building models.")
        
        return building_models, building_texture

    def _create_cube_city(self):
        """Create a city with procedurally textured cube buildings"""
        # Building type definitions with procedural texture generation
        building_types = [
            {'height': randint(5, 10), 'base_color': color.light_gray},
            {'height': randint(4, 7), 'base_color': color.gray},
            {'height': randint(6, 12), 'base_color': color.dark_gray},
            {'height': randint(4, 8), 'base_color': color.rgba(0.6, 0.6, 0.7, 1)},
        ]
        
        for x in range(-20, 21, 8):
            for z in range(-20, 21, 8):
                if random.random() < 0.3:
                    continue
                    
                pos_x = x + uniform(-1, 1)
                pos_z = z + uniform(-1, 1)
                self._create_procedural_building(pos_x, pos_z, building_types)

    def _create_procedural_building(self, pos_x, pos_z, building_types=None):
        """Create a building with procedurally generated texture"""
        if not building_types:
            building_types = [
                {'height': randint(5, 10), 'base_color': color.light_gray},
                {'height': randint(4, 7), 'base_color': color.gray},
                {'height': randint(6, 12), 'base_color': color.dark_gray},
                {'height': randint(4, 8), 'base_color': color.rgba(0.6, 0.6, 0.7, 1)},
            ]
            
        # Select random building type
        building_type = random.choice(building_types)
        height = building_type['height']
        width = random.randint(2, 4)
        depth = random.randint(2, 4)
        
        # Create the main building structure
        building = Entity(
            model='cube',
            position=(pos_x, height/2, pos_z),  # Position at half height
            scale=(width, height, depth),
            name=f'building_cube_{len(self.buildings)}'
        )
        
        # Generate a procedural texture for the building - no external files needed
        building_texture = self.generate_building_texture(
            building_type['base_color'], 
            width=128, 
            height=128,
            window_color=color.rgba(0.7, 0.9, 1.0, 1.0)
        )
        
        building.texture = building_texture
        
        # Make sure it has a proper collider
        building.collider = 'box'
        
        # Add a simple roof
        roof = Entity(
            parent=building,
            model='cube',
            position=(0, 0.5, 0),
            scale=(1, 0.1, 1),
            color=color.dark_gray
        )

        self.buildings.append(building)
        return building

    def generate_building_texture(self, base_color, width=128, height=128, window_color=color.azure):
        """Generate a procedural building texture with windows and details"""
        # Create a new texture using Ursina's Texture class
        from PIL import Image, ImageDraw
        import numpy as np
        
        # Create a blank image with the base color
        r, g, b = int(base_color.r * 255), int(base_color.g * 255), int(base_color.b * 255)
        img = Image.new('RGBA', (width, height), (r, g, b, 255))
        draw = ImageDraw.Draw(img)
        
        # Add windows
        num_floors = random.randint(4, 8)
        num_windows_x = random.randint(3, 6)
        
        window_width = width // (num_windows_x * 2)
        window_height = height // (num_floors * 2)
        window_spacing_x = width // num_windows_x
        window_spacing_y = height // num_floors
        
        # Convert window color to RGB
        w_r, w_g, w_b = int(window_color.r * 255), int(window_color.g * 255), int(window_color.b * 255)
        
        # Drawing pattern depends on time of day - some windows lit, some dark
        for floor in range(num_floors):
            for win_x in range(num_windows_x):
                # Randomize window lighting
                if random.random() < 0.7:  # 70% of windows are lit
                    window_fill = (w_r, w_g, w_b, 255)
                else:
                    # Dark window
                    window_fill = (30, 30, 40, 255)
                    
                # Draw the window
                x1 = win_x * window_spacing_x + (window_spacing_x - window_width) // 2
                y1 = floor * window_spacing_y + (window_spacing_y - window_height) // 2
                x2 = x1 + window_width
                y2 = y1 + window_height
                
                draw.rectangle([x1, y1, x2, y2], fill=window_fill)
        
        # Add some architectural details
        # Horizontal lines between floors
        for floor in range(num_floors + 1):
            y = floor * window_spacing_y
            draw.line([(0, y), (width, y)], fill=(r//2, g//2, b//2, 255), width=2)
        
        # Edge details
        edge_color = (min(r+30, 255), min(g+30, 255), min(b+30, 255), 255)
        draw.rectangle([0, 0, width-1, height-1], outline=edge_color, width=3)
        
        # Add some texture/noise for realism
        pixels = np.array(img)
        noise = (np.random.rand(height, width, 4) * 20 - 10).astype(np.int32)
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)
        
        # Convert to Ursina texture
        texture = Texture(img)
        return texture

    def create_city_layout(self):
        """Create a city with procedurally generated buildings"""
        print("Creating city with procedural buildings")
        self._create_cube_city()

    def create_obstacles(self):
        """Create various obstacles throughout the environment"""
        obstacles = []
        available_models = {}

        # Source path for KayKit OBJ models
        kaykit_obj_path = os.path.join(self.kaykit_base_path, "obj")
        
        # Destination path for obstacle models
        dest_obstacle_path = os.path.join(self.assets_root, "models", "obstacles")
        os.makedirs(dest_obstacle_path, exist_ok=True)

        # List of possible obstacle models
        obstacle_types = ["firehydrant", "trash_A", "trash_B", "dumpster", "bench"]

        # Copy and prepare obstacle models
        for obs_type in obstacle_types:
            model_filename = f"{obs_type}.obj"
            mtl_filename = f"{obs_type}.mtl"
            
            dest_model_file = os.path.join(dest_obstacle_path, model_filename)
            dest_mtl_file = os.path.join(dest_obstacle_path, mtl_filename)
            
            source_model_file = os.path.join(kaykit_obj_path, model_filename)
            source_mtl_file = os.path.join(kaykit_obj_path, mtl_filename)

            # Copy model if needed
            if not os.path.exists(dest_model_file) and os.path.exists(source_model_file):
                try:
                    shutil.copy2(source_model_file, dest_model_file)
                    print(f"Copied obstacle model {model_filename}")
                except Exception as e:
                    print(f"Error copying obstacle model {model_filename}: {e}")

            # Copy MTL if needed
            if not os.path.exists(dest_mtl_file) and os.path.exists(source_mtl_file):
                try:
                    shutil.copy2(source_mtl_file, dest_mtl_file)
                    print(f"Copied obstacle MTL {mtl_filename}")
                except Exception as e:
                    print(f"Error copying obstacle MTL {mtl_filename}: {e}")

            # Add to available models if file exists
            if os.path.exists(dest_model_file):
                relative_model_path = os.path.join("assets", "models", "obstacles", model_filename)
                available_models[obs_type] = relative_model_path
                print(f"Found obstacle model {obs_type}")
        
        # Create obstacles with available models
        for i in range(10):  # Create 10 obstacles
            if available_models:
                # Use a random available model
                obs_type = random.choice(list(available_models.keys()))
                model_path = available_models[obs_type]

                try:
                    # Create obstacle container entity
                    container = Entity(
                        position=(uniform(-24, 24), 0, uniform(-24, 24)),
                        name=f'obstacle_container_{obs_type}_{i}'
                    )
                    
                    # Create obstacle with the model and building texture
                    obstacle = Entity(
                        parent=container,
                        model=model_path,
                        texture=self.building_texture,
                        scale=3.0,  # Make obstacles bigger for better visibility
                        color=color.white,  # Use white color to properly show texture
                        name=f'obstacle_{obs_type}_{i}',
                        collider='box'
                    )
                    
                    # Add a colored marker on top to make obstacles more visible
                    marker = Entity(
                        parent=container,
                        model='sphere',
                        scale=0.5,
                        y=2,
                        color=color.red,
                        billboard=True,  # Always face the camera
                    )
                    
                    print(f"Created obstacle {obs_type}")
                    obstacles.append(container)
                    
                except Exception as e:
                    print(f"Error creating obstacle {obs_type}: {e}")
                    # Fallback to cube if model loading fails
                    self._create_fallback_obstacle(i, obstacles)
            else:
                # Fallback to basic cube if no models loaded
                print("No obstacle models found, creating fallback obstacles.")
                self._create_fallback_obstacle(i, obstacles)

        # Add obstacles to dynamic elements
        self.dynamic_elements.extend(obstacles)

    def _create_fallback_obstacle(self, index, obstacles_list):
        """Create a fallback obstacle when model loading fails"""
        # Create a simple colored cube as a fallback
        obstacle = Entity(
            model='cube',
            color=color.orange,
            position=(uniform(-24, 24), 0.5, uniform(-24, 24)),
            scale=(1, 1, 1),
            collider='box',
            name=f'obstacle_fallback_{index}'
        )
        obstacles_list.append(obstacle)

    def create_dynamic_elements(self):
        """Create dynamic environment elements like collapsible buildings and movable bridges"""
        # Set some buildings as collapsible
        for building in self.buildings:
            # 15% chance for a building to be collapsible
            if random.random() < 0.15:
                building.collapsible = True
                building.collapsed = False
                self.dynamic_elements.append(building)
                print(f"Made building {building.name} collapsible")
                
                # Add a warning sign on top
                warning = Entity(
                    parent=building,
                    model='cube',
                    color=color.yellow,
                    scale=(0.5, 0.5, 0.5),
                    y=5,  # Place on top of building
                    billboard=True  # Always face camera
                )
                # Make it blink
                warning.animate_color(color.red, duration=0.5, loop=True)
        
        # Create bridges between some buildings
        self.create_bridges()
        
        # Create traffic with moving vehicles
        self.create_traffic()
    
    def create_bridges(self):
        """Create movable bridges between buildings"""
        self.bridges = []
        
        # Find pairs of buildings that are close enough for bridges
        for i, building1 in enumerate(self.buildings):
            for j, building2 in enumerate(self.buildings[i+1:], i+1):
                # Calculate distance between buildings
                distance = (building1.position - building2.position).length()
                
                # If buildings are between 8-15 units apart, they're candidates for a bridge
                if 8 <= distance <= 15:
                    # 25% chance to create a bridge
                    if random.random() < 0.25:
                        # Calculate bridge position and rotation
                        bridge_pos = (building1.position + building2.position) / 2
                        direction = building2.position - building1.position
                        bridge_angle = math.degrees(math.atan2(direction.z, direction.x))
                        
                        # Create bridge entity
                        bridge = Entity(
                            model='cube',
                            color=color.dark_gray,
                            position=bridge_pos,
                            scale=(distance, 0.5, 2),
                            rotation_y=bridge_angle,
                            collider='box',
                            name=f'bridge_{len(self.bridges)}'
                        )
                        
                        # Add railings
                        left_railing = Entity(
                            parent=bridge,
                            model='cube',
                            color=color.light_gray,
                            position=(0, 0.5, -0.9),
                            scale=(1, 0.5, 0.1)
                        )
                        
                        right_railing = Entity(
                            parent=bridge,
                            model='cube',
                            color=color.light_gray,
                            position=(0, 0.5, 0.9),
                            scale=(1, 0.5, 0.1)
                        )
                        
                        # Store open/closed state
                        bridge.is_open = False
                        bridge.is_moving = False
                        bridge.connected_buildings = (building1, building2)
                        
                        # Add bridge to dynamic elements
                        self.bridges.append(bridge)
                        self.dynamic_elements.append(bridge)
                        
                        print(f"Created bridge between buildings at ({bridge_pos.x:.1f}, {bridge_pos.z:.1f})")
    
    def create_traffic(self):
        """Create moving vehicles that add dynamic obstacles"""
        self.vehicles = []
        
        # Create a few main roads
        for i in range(3):
            # Create east-west road
            z_pos = -15 + (i * 15)
            
            for j in range(3):  # 3 vehicles per road
                # Create vehicle
                vehicle = Entity(
                    model='cube',
                    color=color.random_color(),
                    position=(random.uniform(-20, 20), 0.5, z_pos),
                    scale=(2, 1, 1),
                    collider='box',
                    name=f'vehicle_ew_{i}_{j}'
                )
                
                # Set movement properties
                vehicle.direction = Vec3(1, 0, 0)  # Move east
                if random.random() < 0.5:
                    vehicle.direction = -vehicle.direction  # 50% chance to move west
                    vehicle.rotation_y = 180
                
                vehicle.speed = random.uniform(3, 8)
                vehicle.road_bounds = (-25, 25)  # X boundaries
                
                self.vehicles.append(vehicle)
                self.dynamic_elements.append(vehicle)
            
            # Create north-south road
            x_pos = -15 + (i * 15)
            
            for j in range(3):  # 3 vehicles per road
                # Create vehicle
                vehicle = Entity(
                    model='cube',
                    color=color.random_color(),
                    position=(x_pos, 0.5, random.uniform(-20, 20)),
                    scale=(1, 1, 2),
                    collider='box',
                    name=f'vehicle_ns_{i}_{j}'
                )
                
                # Set movement properties
                vehicle.direction = Vec3(0, 0, 1)  # Move north
                if random.random() < 0.5:
                    vehicle.direction = -vehicle.direction  # 50% chance to move south
                    vehicle.rotation_y = 180
                
                vehicle.speed = random.uniform(3, 8)
                vehicle.road_bounds = (-25, 25)  # Z boundaries
                
                self.vehicles.append(vehicle)
                self.dynamic_elements.append(vehicle)
    
    def update(self):
        """Update dynamic environment elements"""
        # Update elements like collapsing buildings, moving bridges and vehicles
        for element in self.dynamic_elements:
            # Handle collapsible buildings
            if hasattr(element, 'collapsible') and not getattr(element, 'collapsed', True):
                # Small random chance for buildings to collapse
                if random.random() < 0.0005:  # Very low chance per frame
                    element.collapsed = True
                    element.animate_scale((element.scale_x, 0.2, element.scale_z), duration=1.0)
                    element.animate_position((element.x, 0.1, element.z), duration=1.0)
                    print(f"Building {element.name} collapsed!")
                    
                    # Create dust cloud effect
                    self.create_collapse_effect(element.position)
            
            # Handle bridges opening/closing
            if element in self.bridges and not element.is_moving:
                # Random chance to change bridge state
                if random.random() < 0.0002:  # Very low chance per frame
                    self.toggle_bridge(element)
            
            # Handle moving vehicles
            if element in self.vehicles:
                # Move vehicle
                element.position += element.direction * element.speed * time.dt
                
                # Check if reached boundary
                if element.direction.x != 0:  # East-west movement
                    if element.x < element.road_bounds[0] or element.x > element.road_bounds[1]:
                        element.direction = -element.direction  # Reverse direction
                        element.rotation_y = 180 - element.rotation_y  # Turn around
                
                if element.direction.z != 0:  # North-south movement
                    if element.z < element.road_bounds[0] or element.z > element.road_bounds[1]:
                        element.direction = -element.direction  # Reverse direction
                        element.rotation_y = 180 - element.rotation_y  # Turn around
    
    def toggle_bridge(self, bridge):
        """Toggle a bridge between open and closed states"""
        if bridge.is_moving:
            return
            
        bridge.is_moving = True
        if bridge.is_open:
            # Close the bridge
            print(f"Closing bridge {bridge.name}")
            bridge.animate_position(
                (bridge.x, 1, bridge.z),  # Lower to normal position
                duration=2.0,
                curve=curve.in_out_sine
            )
            bridge.is_open = False
        else:
            # Open the bridge
            print(f"Opening bridge {bridge.name}")
            bridge.animate_position(
                (bridge.x, 5, bridge.z),  # Raise up
                duration=2.0,
                curve=curve.in_out_sine
            )
            bridge.is_open = True
            
        # Reset is_moving after animation completes
        invoke(setattr, bridge, 'is_moving', False, delay=2.1)
    
    def create_collapse_effect(self, position):
        """Create dust cloud effect when buildings collapse"""
        # Create multiple dust particles
        for _ in range(20):
            dust = Entity(
                model='sphere',
                color=color.light_gray,
                position=position + Vec3(
                    random.uniform(-2, 2),
                    random.uniform(0, 3),
                    random.uniform(-2, 2)
                ),
                scale=random.uniform(0.5, 1.5)
            )
            
            # Animate the dust particles
            dust.animate_scale(0, duration=random.uniform(1.0, 2.0))
            dust.animate_color(color.rgba(0.7, 0.7, 0.7, 0), duration=random.uniform(1.0, 2.0))
            dust.animate_position(
                dust.position + Vec3(
                    random.uniform(-3, 3),
                    random.uniform(1, 5),
                    random.uniform(-3, 3)
                ),
                duration=random.uniform(1.0, 2.0)
            )
            
            # Destroy after animation
            destroy(dust, delay=2.0)