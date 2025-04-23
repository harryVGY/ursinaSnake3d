from ursina import *
from random import randint, uniform
import random
import os
import shutil

# Define the base path for KayKit assets relative to the project root
KAYKIT_ASSETS_RELATIVE_PATH = os.path.join("..", "..", "KayKit_City_Builder_Bits_1.0_FREE", "Assets")

class Environment(Entity):
    def __init__(self):
        super().__init__()
        print("Initializing environment...")
        # Get the base directory of the script to build absolute paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.script_dir)
        self.assets_root = os.path.join(self.project_root, "assets")
        self.kaykit_base_path = os.path.abspath(os.path.join(self.script_dir, KAYKIT_ASSETS_RELATIVE_PATH))
        
        self.create_ground()
        self.buildings = []  # Store buildings for reference
        self.dynamic_elements = []  # Initialize dynamic_elements list before using it
        self.building_models, self.building_texture = self.load_building_assets() # Load models and texture
        self.create_city_layout()
        self.create_obstacles()

    def create_ground(self):
        # Create a large textured ground plane
        ground_texture_path = os.path.join(self.assets_root, "textures", "ground_texture.png") # Example path, ensure this texture exists
        # Fallback texture if the specific one doesn't exist
        ground_texture = 'grass' # Use a built-in texture or a known good one
        if os.path.exists(ground_texture_path):
             ground_texture = load_texture(ground_texture_path)
        else:
             print(f"Warning: Ground texture not found at {ground_texture_path}. Using fallback.")
             # Attempt to copy from KayKit if it exists there under a different name maybe?
             # For now, just use a default Ursina texture.
             # You might need to manually place a ground texture in assets/textures/
             pass


        self.ground = Entity(
            model='plane',
            scale=(50, 1, 50),
            # color=color.light_gray, # Color is less important when textured
            texture=ground_texture, # Use the loaded texture or fallback
            texture_scale=(10, 10), # Adjust scale as needed
            collider='box'
        )
        # self.ground.texture = 'grid' # Remove this line, texture is set above

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
        dest_texture_path = os.path.join(dest_model_path, texture_filename) # Store texture with models
        source_texture_path = os.path.join(kaykit_obj_path, texture_filename)

        # Copy texture if it doesn't exist in dest and exists in source
        if not os.path.exists(dest_texture_path) and os.path.exists(source_texture_path):
            try:
                shutil.copy2(source_texture_path, dest_texture_path)
                print(f"Copied texture from {source_texture_path} to {dest_texture_path}")
            except Exception as e:
                print(f"Error copying texture: {e}")

        # Load the texture if it exists in the destination
        if os.path.exists(dest_texture_path):
            building_texture = load_texture(texture_filename, path=dest_model_path)
            if building_texture:
                 print(f"Successfully loaded building texture: {dest_texture_path}")
            else:
                 print(f"Warning: Failed to load texture from {dest_texture_path}")
        else:
            print(f"Warning: Building texture not found at {dest_texture_path} or {source_texture_path}")


        # --- Model Handling ---
        building_types = ["building_A", "building_B", "building_C", "building_D",
                         "building_E", "building_F", "building_G", "building_H"]

        # Even if we don't find any models, we'll add default colored structures
        # This ensures we always have some buildings to render
        if not building_texture:
            print("No building texture found. Using colored structures instead.")
        
        # Try to load real models first
        for building_type in building_types:
            model_filename = f"{building_type}.obj"
            mtl_filename = f"{building_type}.mtl"
            dest_model_file = os.path.join(dest_model_path, model_filename)
            dest_mtl_file = os.path.join(dest_model_path, mtl_filename)
            source_model_file = os.path.join(kaykit_obj_path, model_filename)
            source_mtl_file = os.path.join(kaykit_obj_path, mtl_filename)

            # Copy model and mtl if they don't exist in dest and exist in source
            copied_model = False
            if not os.path.exists(dest_model_file) and os.path.exists(source_model_file):
                try:
                    shutil.copy2(source_model_file, dest_model_file)
                    print(f"Copied model {model_filename} to {dest_model_path}")
                    copied_model = True
                except Exception as e:
                    print(f"Error copying model {model_filename}: {e}")

            if not os.path.exists(dest_mtl_file) and os.path.exists(source_mtl_file):
                 try:
                      shutil.copy2(source_mtl_file, dest_mtl_file)
                      print(f"Copied MTL {mtl_filename} to {dest_model_path}")
                 except Exception as e:
                      print(f"Error copying MTL {mtl_filename}: {e}")


            # Add to models dict if the OBJ file exists in the destination path
            if os.path.exists(dest_model_file):
                # Store the relative path for Ursina, assuming 'assets' is discoverable
                relative_model_path = os.path.join("assets", "models", "buildings", model_filename)
                building_models[building_type.lower()] = relative_model_path # Use relative path for loading
                print(f"Found {building_type} model at {dest_model_file}")
            elif copied_model: # If we just copied it, try adding it
                 relative_model_path = os.path.join("assets", "models", "buildings", model_filename)
                 building_models[building_type.lower()] = relative_model_path
                 print(f"Using newly copied {building_type} model")
            else:
                # Add a fallback colored structure indicator
                # We'll use 'cube' and a specific color per building type
                building_models[building_type.lower()] = 'cube'
                print(f"Using fallback cube for {building_type}")

        if not building_models:
            print(f"Warning: No building models found or copied to {dest_model_path}")
            # Ensure we have at least some building types as fallbacks
            for building_type in building_types:
                building_models[building_type.lower()] = 'cube'
                print(f"Added fallback cube for {building_type}")
        else:
            print(f"Successfully prepared {len(building_models)} building models.")

        return building_models, building_texture # Return both models dict and the texture


    def create_city_layout(self):
        # We'll always have building models now with our fallbacks, so just check for consistency
        if not self.building_models:
            print("Building models missing, creating basic cube buildings instead")
            self._create_cube_city()
            return

        # Create a more varied city layout with different building models
        building_scales = {
            'building_a': 2.5,  # Increased sizes for better visibility
            'building_b': 2.5,
            'building_c': 2.8,  # Medium buildings
            'building_d': 2.8,
            'building_e': 3.2,  # Taller buildings
            'building_f': 3.2,
            'building_g': 3.5,  # Large buildings
            'building_h': 3.5
        }
        
        # Building colors for fallback cubes
        building_colors = {
            'building_a': color.light_gray,
            'building_b': color.gray, 
            'building_c': color.dark_gray,
            'building_d': color.rgba(0.7, 0.7, 0.8, 1),
            'building_e': color.rgba(0.6, 0.6, 0.7, 1),
            'building_f': color.rgba(0.5, 0.5, 0.6, 1),
            'building_g': color.rgba(0.4, 0.4, 0.5, 1),
            'building_h': color.rgba(0.3, 0.3, 0.4, 1),
        }
        
        # Place buildings on a grid but with slight positional variation
        for x in range(-20, 21, 8):
            for z in range(-20, 21, 8):
                # Add variation to position
                pos_x = x + uniform(-1, 1)
                pos_z = z + uniform(-1, 1)
                
                # Choose a random building model
                building_keys = list(self.building_models.keys())
                building_type = random.choice(building_keys)
                model_path = self.building_models[building_type]
                scale_value = building_scales.get(building_type, 2.5) # Default to 2.5 for better visibility
                
                # Add some rotation variation
                rotation_y = random.choice([0, 90, 180, 270])

                # --- Debug Print --- 
                print(f"Attempting to create building: type={building_type}, model_path='{model_path}', texture='{self.building_texture}'")
                # --- End Debug Print ---
                
                try:
                    # Check if we're using a fallback cube or actual model
                    if model_path == 'cube':
                        # Create a fallback colored cube
                        height = randint(5, 10)  # Increased height for better visibility
                        building = Entity(
                            model='cube',
                            color=building_colors.get(building_type, color.light_gray),
                            position=(pos_x, height/2, pos_z),
                            scale=(2.5, height, 2.5),  # Wider buildings
                            name=f'building_fallback_{building_type}_{len(self.buildings)}',
                            collider='box'
                        )
                        
                        # Create an outline for better visibility
                        outline = Entity(
                            parent=building,
                            model='cube',
                            color=color.black,
                            scale=(1.02, 1.02, 1.02),
                            alpha=0.6
                        )
                        
                        # Add windows to make it look more like a building
                        window_color = color.azure
                        for floor in range(1, height):
                            for side in range(4):
                                rotation = side * 90
                                window = Entity(
                                    parent=building,
                                    model='cube',
                                    rotation_y=rotation,
                                    position=(0, floor - height/2 + 0.5, 1.3 - 0.1),  # More visible windows
                                    scale=(0.7, 0.7, 0.1),  # Larger windows
                                    color=window_color
                                )
                        
                        # Add a roof
                        roof = Entity(
                            parent=building,
                            model='cube',
                            position=(0, height/2 + 0.1, 0),
                            scale=(2.5, 0.3, 2.5),
                            color=color.dark_gray
                        )
                        
                        print(f"Created fallback building for {building_type} at ({pos_x:.2f}, 0, {pos_z:.2f})")
                    else:
                        # Create the building entity with the model and texture
                        building = Entity(
                            model=model_path,
                            texture=self.building_texture,
                            position=(pos_x, 0, pos_z),
                            rotation_y=rotation_y,
                            scale=scale_value,
                            name=f'building_{building_type}_{len(self.buildings)}',
                            collider='box'
                        )
                        
                        # Add outline for better visibility of model buildings
                        outline = Entity(
                            parent=building,
                            model=model_path,
                            color=color.black,
                            scale=1.02,  # Slightly larger than the building
                            alpha=0.5     # Semi-transparent
                        )
                        
                        print(f"Successfully created Entity for {building_type} at ({pos_x:.2f}, 0, {pos_z:.2f})")
                    
                    self.buildings.append(building)

                    # Add a small chance for this to be a "collapsible" building
                    if random.random() < 0.2:
                        building.collapsible = True
                        building.collapsed = False
                        self.dynamic_elements.append(building)
                        
                except Exception as e:
                    # Print more detailed error, including model path
                    model_path_used = self.building_models.get(building_type, "N/A")
                    print(f"!!! ERROR creating {building_type} building using model '{model_path_used}': {e}")
                    import traceback
                    traceback.print_exc()
                    # Fallback to cube if model loading fails
                    self._create_cube_building(pos_x, pos_z)

    def _create_cube_city(self):
        """Fallback method to create a city with basic cubes if models aren't available"""
        building_types = [
            {'scale': (2, randint(3, 8), 2), 'color': color.light_gray},
            {'scale': (3, randint(2, 5), 3), 'color': color.gray},
            {'scale': (2, randint(4, 10), 2), 'color': color.dark_gray},
            {'scale': (4, randint(3, 6), 4), 'color': color.rgba(0.6, 0.6, 0.7, 1)},
        ]
        
        for x in range(-20, 21, 8):
            for z in range(-20, 21, 8):
                if random.random() < 0.3:
                    continue
                    
                pos_x = x + uniform(-1, 1)
                pos_z = z + uniform(-1, 1)
                self._create_cube_building(pos_x, pos_z, building_types)
    
    def _create_cube_building(self, pos_x, pos_z, building_types=None):
        """Create a basic cube building (fallback method)"""
        if not building_types:
            building_types = [
                {'scale': (2, randint(3, 8), 2), 'color': color.light_gray},
                {'scale': (3, randint(2, 5), 3), 'color': color.gray},
                {'scale': (2, randint(4, 10), 2), 'color': color.dark_gray},
                {'scale': (4, randint(3, 6), 4), 'color': color.rgba(0.6, 0.6, 0.7, 1)},
            ]
            
        # Select random building type
        building_type = random.choice(building_types)
        
        # Create the main building structure
        building = Entity(
            model='cube',
            color=building_type['color'],
            position=(pos_x, building_type['scale'][1]/2, pos_z),  # Position at half height
            scale=building_type['scale'],
            name=f'building_cube_{len(self.buildings)}'
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
        return building

    def create_obstacles(self):
        # Create dynamic obstacles in the environment
        obstacles = []
        available_models = {} # Reset this dict

        # Source path for KayKit OBJ models
        kaykit_obj_path = os.path.join(self.kaykit_base_path, "obj")
        # Destination path for obstacle models (can reuse building texture)
        dest_obstacle_path = os.path.join(self.assets_root, "models", "obstacles")
        os.makedirs(dest_obstacle_path, exist_ok=True)

        # List of possible obstacle models
        obstacle_types = ["firehydrant", "trash_A", "trash_B", "dumpster", "bench"]

        # Check which models are available, copy if needed
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
                    print(f"Copied obstacle model {model_filename} to {dest_obstacle_path}")
                except Exception as e:
                    print(f"Error copying obstacle model {model_filename}: {e}")

            # Copy MTL if needed
            if not os.path.exists(dest_mtl_file) and os.path.exists(source_mtl_file):
                 try:
                      shutil.copy2(source_mtl_file, dest_mtl_file)
                      print(f"Copied obstacle MTL {mtl_filename} to {dest_obstacle_path}")
                 except Exception as e:
                      print(f"Error copying obstacle MTL {mtl_filename}: {e}")


            # Add to available models if the OBJ exists in destination
            if os.path.exists(dest_model_file):
                relative_model_path = os.path.join("assets", "models", "obstacles", model_filename)
                available_models[obs_type] = relative_model_path
                print(f"Found obstacle model {obs_type} at {dest_model_file}")


        # Create obstacles with available models
        for i in range(10): # Create more obstacles
            if available_models:
                # Use a random available model
                obs_type = random.choice(list(available_models.keys()))
                model_path = available_models[obs_type]

                try:
                    # Create obstacle with the model and building texture
                    obstacle = Entity(
                        model=model_path,
                        texture=self.building_texture, # Reuse building texture
                        position=(uniform(-24, 24), 0, uniform(-24, 24)), # Spread them out more
                        scale=1.5,
                        name=f'obstacle_{obs_type}_{i}',
                        collider='box'
                    )
                    print(f"Created obstacle {obs_type} using model {model_path}")
                    obstacles.append(obstacle)
                except Exception as e:
                     print(f"Error creating obstacle {obs_type} with model {model_path}: {e}")
                     # Fallback to cube if model loading fails
                     self._create_fallback_obstacle(i, obstacles)

            else:
                # Fallback to basic cube if no models loaded
                print("No obstacle models found, creating red cube fallback.")
                self._create_fallback_obstacle(i, obstacles)

        # Create a moveable bridge
        self.create_bridge() # Ensure bridge creation is called
        self.dynamic_elements.extend(obstacles) # Add obstacles to dynamic elements if they need updates later

        return obstacles # Return the list of created obstacles

    def _create_fallback_obstacle(self, index, obstacles_list):
        """Create a more interesting fallback obstacle when model loading fails"""
        # Choose a random type of obstacle to create as fallback
        obs_type = random.choice(['hydrant', 'trash', 'bench'])
        
        if obs_type == 'hydrant':
            # Create fire hydrant shape (red cylinder with cap)
            base = Entity(
                model='cylinder',
                color=color.red,
                position=(uniform(-24, 24), 0.5, uniform(-24, 24)),
                scale=(0.5, 1, 0.5),
                collider='box',
                name=f'obstacle_fallback_hydrant_{index}'
            )
            
            # Add a cap on top
            cap = Entity(
                parent=base,
                model='sphere',
                color=color.dark_red,
                position=(0, 0.6, 0),
                scale=(0.7, 0.3, 0.7)
            )
            
            # Add connectors on sides
            for side in [0, 180]:
                connector = Entity(
                    parent=base,
                    model='cube',
                    color=color.dark_red,
                    rotation_y=side,
                    position=(0.3, 0, 0),
                    scale=(0.4, 0.2, 0.2)
                )
            
            obstacles_list.append(base)
            
        elif obs_type == 'trash':
            # Create trash can (cylindrical shape with different color)
            trash = Entity(
                model='cylinder',
                color=color.gray,
                position=(uniform(-24, 24), 0.7, uniform(-24, 24)),
                scale=(0.7, 1.4, 0.7),
                collider='box',
                name=f'obstacle_fallback_trash_{index}'
            )
            
            # Add trash lid
            lid = Entity(
                parent=trash,
                model='cylinder',
                color=color.dark_gray,
                position=(0, 0.75, 0),
                scale=(0.8, 0.1, 0.8)
            )
            
            obstacles_list.append(trash)
            
        else:  # bench
            # Create bench (rectangular shape)
            pos = (uniform(-24, 24), 0.4, uniform(-24, 24))
            rotation_y = random.choice([0, 90, 180, 270])
            
            bench = Entity(
                model='cube',
                color=color.brown,
                position=pos,
                rotation_y=rotation_y,
                scale=(2, 0.2, 0.8),
                collider='box',
                name=f'obstacle_fallback_bench_{index}'
            )
            
            # Add bench legs
            for x in [-0.7, 0.7]:
                leg = Entity(
                    parent=bench,
                    model='cube', 
                    color=color.dark_brown,
                    position=(x, -0.4, 0),
                    scale=(0.2, 0.6, 0.6)
                )
                
            # Add bench back
            back = Entity(
                parent=bench,
                model='cube',
                color=color.brown,
                position=(0, 0.5, -0.3),
                scale=(1.8, 0.8, 0.2)
            )
            
            obstacles_list.append(bench)
            
        print(f"Created fallback {obs_type} obstacle")
        return

    def create_bridge(self):
        # Create a bridge that can open/close
            
            # Collapsing buildings
            if hasattr(element, 'collapsible') and not element.collapsed:
                # Random chance to collapse when player is nearby
                if random.random() < 0.0005:  # Very small chance each frame
                    element.collapsed = True
                    element.animate_scale((element.scale_x, 0.2, element.scale_z), duration=0.5)
                    element.animate_position((element.x, 0.1, element.z), duration=0.5)
                    print(f"Building {element.name} collapsed!")