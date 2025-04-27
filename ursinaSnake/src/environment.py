from ursina import *
from random import randint, uniform, choice
import random
import os
import shutil
import math

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
        """Create a city layout with improved building generation."""
        if not self.building_models:
            print("No building models found. Using fallback cube buildings.")
            self._create_cube_city()
            return

        # Define a wider variety of building scales and colors
        building_scales = {
            'building_a': (2, randint(5, 10), 2),
            'building_b': (3, randint(6, 12), 3),
            'building_c': (4, randint(8, 15), 4),
            'building_d': (5, randint(10, 20), 5),
            'building_e': (6, randint(8, 15), 6),
            'building_f': (3.5, randint(12, 18), 3.5),
            'building_g': (4.5, randint(5, 9), 4.5),
            'building_h': (7, randint(8, 12), 7),
        }

        building_colors = {
            'building_a': color.light_gray,
            'building_b': color.gray,
            'building_c': color.dark_gray,
            'building_d': color.rgba(0.5, 0.5, 0.6, 1),
            'building_e': color.rgba(0.6, 0.6, 0.5, 1),
            'building_f': color.rgba(0.7, 0.6, 0.6, 1),
            'building_g': color.rgba(0.5, 0.6, 0.7, 1),
            'building_h': color.rgba(0.6, 0.7, 0.65, 1),
        }

        # Create a building placement grid to avoid overlaps
        grid_size = 12
        occupied_positions = []
        
        # First pass: place main district buildings in a more organized pattern
        for x in range(-24, 25, grid_size):
            for z in range(-24, 25, grid_size):
                # Skip some positions for variety
                if random.random() < 0.2:
                    continue
                
                pos_x = x + uniform(-1, 1)  # Add slight randomness to position
                pos_z = z + uniform(-1, 1)
                
                # Check if this position might overlap with existing buildings (with buffer)
                position_ok = True
                for occupied in occupied_positions:
                    if math.sqrt((pos_x - occupied[0])**2 + (pos_z - occupied[1])**2) < 10:
                        position_ok = False
                        break
                
                if not position_ok:
                    continue
                    
                # Add to occupied positions
                occupied_positions.append((pos_x, pos_z))
                
                # Special buildings for city center - taller, more impressive buildings
                if abs(x) < 12 and abs(z) < 12:
                    allowed_types = ['building_d', 'building_e', 'building_f', 'building_h']
                    building_type = random.choice(allowed_types)
                else:
                    # Regular buildings for outskirts
                    allowed_types = ['building_a', 'building_b', 'building_c', 'building_g']
                    building_type = random.choice(allowed_types)
                
                # Get model info
                model_path = self.building_models.get(building_type, 'cube')
                scale = building_scales.get(building_type, (2, 5, 2))
                building_color = building_colors.get(building_type, color.light_gray)
                
                # Randomize height within type-specific range
                height_factor = random.uniform(0.8, 1.2)
                adjusted_scale = (scale[0], int(scale[1] * height_factor), scale[2])
                
                try:
                    # Create the building entity with improved details
                    building = Entity(
                        model=model_path if model_path != 'cube' else 'cube',
                        texture=self.building_texture if model_path != 'cube' else None,
                        position=(pos_x, adjusted_scale[1] / 2, pos_z),
                        scale=adjusted_scale,
                        color=building_color if model_path == 'cube' else None,
                        rotation_y=random.choice([0, 90, 180, 270]),
                        name=f'building_{building_type}_{len(self.buildings)}',
                        collider='box',
                    )
                    
                    # Add detail/decoration to buildings, more for cube fallbacks
                    if model_path == 'cube':
                        self._add_building_details(building, adjusted_scale)
                    
                    # Add a chance for collapsible (damaged) buildings
                    if random.random() < 0.05:  # 5% chance
                        building.collapsible = True
                        building.collapsed = False
                        # Add visual indicator like cracks or damage texture
                        if model_path == 'cube':
                            damage = Entity(
                                parent=building,
                                model='cube',
                                color=color.rgba(0.3, 0.3, 0.3, 1),
                                position=(0, 0, adjusted_scale[2]/2-0.05),
                                scale=(adjusted_scale[0]*0.8, adjusted_scale[1]*0.7, 0.05),
                            )
                    
                    self.buildings.append(building)
                
                except Exception as e:
                    print(f"Error creating building {building_type}: {e}")
                    self._create_cube_building(pos_x, pos_z)
        
        # Second pass: add smaller buildings and structures in between
        for _ in range(15):  # Add some smaller filler buildings
            for _ in range(10):  # Try up to 10 times to find an empty spot
                pos_x = random.uniform(-25, 25)
                pos_z = random.uniform(-25, 25)
                
                # Check if too close to existing buildings
                position_ok = True
                for occupied in occupied_positions:
                    if math.sqrt((pos_x - occupied[0])**2 + (pos_z - occupied[1])**2) < 8:
                        position_ok = False
                        break
                        
                if position_ok:
                    occupied_positions.append((pos_x, pos_z))
                    building_type = random.choice(['building_a', 'building_b'])
                    
                    # Create a smaller building or structure
                    try:
                        self._create_cube_building(pos_x, pos_z, [
                            {'scale': (2, randint(2, 4), 2), 'color': color.gray},
                            {'scale': (1.5, randint(1, 3), 1.5), 'color': color.light_gray},
                        ])
                    except Exception as e:
                        print(f"Error creating filler building: {e}")
                    
                    break  # Successfully placed a building
                    
        print(f"Created {len(self.buildings)} buildings in the city layout")

    def create_obstacles(self):
        """Create dynamic obstacles in the environment"""
        obstacles = []
        
        # Create various obstacle types throughout the map
        for i in range(10):
            # Choose obstacle type
            obstacle_type = random.choice(['hydrant', 'trash', 'bench', 'barrier'])
            
            # Find a position away from buildings
            for attempt in range(10):
                pos = (uniform(-24, 24), 0.5, uniform(-24, 24))
                
                # Check if position is clear (not colliding with any buildings)
                position_clear = True
                for building in self.buildings:
                    if math.dist((pos[0], pos[2]), (building.x, building.z)) < 5:
                        position_clear = False
                        break
                    
                if position_clear:
                    break
            
            # Create basic obstacle based on type
            if obstacle_type == 'hydrant':
                # Create fire hydrant - using rgb to define the colors explicitly
                hydrant_red = color.rgb(0.9, 0.1, 0.1)  # Main hydrant color
                cap_red = color.rgb(0.7, 0.1, 0.1)      # Darker cap color
                
                try:
                    # Create the base using cylinder if available, fallback to cube
                    base = Entity(
                        model='cylinder',
                        color=hydrant_red,
                        position=pos,
                        scale=(0.5, 1, 0.5),
                        collider='box',
                        name=f'obstacle_hydrant_{i}'
                    )
                except Exception as e:
                    # Fallback to cube if cylinder model is missing
                    print(f"Using cube fallback for hydrant: {e}")
                    base = Entity(
                        model='cube',
                        color=hydrant_red,
                        position=pos,
                        scale=(0.5, 1, 0.5),
                        collider='box',
                        name=f'obstacle_hydrant_{i}'
                    )
                
                # Add cap
                try:
                    cap = Entity(
                        parent=base,
                        model='sphere',
                        color=cap_red,
                        position=(0, 0.6, 0),
                        scale=(0.7, 0.3, 0.7)
                    )
                except Exception as e:
                    # Fallback to cube if sphere model is missing
                    print(f"Using cube fallback for hydrant cap: {e}")
                    cap = Entity(
                        parent=base,
                        model='cube',
                        color=cap_red,
                        position=(0, 0.6, 0),
                        scale=(0.7, 0.3, 0.7)
                    )
                
                obstacles.append(base)
                
            elif obstacle_type == 'trash':
                # Create trash can with explicit model handling
                try:
                    trash = Entity(
                        model='cylinder',
                        color=color.gray,
                        position=pos,
                        scale=(0.7, 1.4, 0.7),
                        collider='box',
                        name=f'obstacle_trash_{i}'
                    )
                    
                    # Add lid
                    lid = Entity(
                        parent=trash,
                        model='cylinder',
                        color=color.dark_gray,
                        position=(0, 0.75, 0),
                        scale=(0.8, 0.1, 0.8)
                    )
                except Exception as e:
                    # Fallback to cube if cylinder model is missing
                    print(f"Using cube fallback for trash can: {e}")
                    trash = Entity(
                        model='cube',
                        color=color.gray,
                        position=pos,
                        scale=(0.7, 1.4, 0.7),
                        collider='box',
                        name=f'obstacle_trash_{i}'
                    )
                    
                    # Add lid
                    lid = Entity(
                        parent=trash,
                        model='cube',
                        color=color.dark_gray,
                        position=(0, 0.75, 0),
                        scale=(0.8, 0.1, 0.8)
                    )
                
                obstacles.append(trash)
                
            elif obstacle_type == 'bench':
                # Create bench
                bench_pos = pos
                rotation_y = random.choice([0, 90, 180, 270])
                
                # Define a custom brown color for the bench since dark_brown doesn't exist
                bench_color = color.rgb(0.4, 0.25, 0.1)
                leg_color = color.rgb(0.3, 0.18, 0.08)
                
                bench = Entity(
                    model='cube',
                    color=bench_color,
                    position=bench_pos,
                    rotation_y=rotation_y,
                    scale=(2, 0.2, 0.8),
                    collider='box',
                    name=f'obstacle_bench_{i}'
                )
                
                # Add bench legs
                for x in [-0.7, 0.7]:
                    leg = Entity(
                        parent=bench,
                        model='cube',
                        color=leg_color,
                        position=(x, -0.4, 0),
                        scale=(0.2, 0.6, 0.6)
                    )
                    
                # Add bench back
                back = Entity(
                    parent=bench,
                    model='cube',
                    color=bench_color,
                    position=(0, 0.5, -0.3),
                    scale=(1.8, 0.8, 0.2)
                )
                
                obstacles.append(bench)
                
            else:  # barrier
                # Create road barrier
                barrier = Entity(
                    model='cube',
                    color=color.orange,
                    position=pos,
                    rotation_y=random.choice([0, 90]),
                    scale=(2, 1, 0.3),
                    collider='box',
                    name=f'obstacle_barrier_{i}'
                )
                
                # Add stripes
                for x in range(-1, 2):
                    stripe = Entity(
                        parent=barrier,
                        model='cube',
                        color=color.white,
                        position=(x*0.5, 0.15, 0),
                        scale=(0.2, 0.3, 0.32)
                    )
                    
                obstacles.append(barrier)
        
        # Add obstacles to dynamic elements list for updates
        self.dynamic_elements.extend(obstacles)
        
        # Create a bridge if needed
        self.create_bridge()
        
        return obstacles

    def create_bridge(self):
        """Create a decorative bridge that can animate open/closed"""
        # Create a bridge in the central area
        bridge_position = Vec3(0, 0.5, 0)
        
        # Create the bridge parts
        bridge_left = Entity(
            model='cube',
            color=color.dark_gray,
            position=(bridge_position.x - 2, bridge_position.y, bridge_position.z),
            scale=(4, 0.5, 3),
            collider='box',
            name='bridge_left'
        )
        
        bridge_right = Entity(
            model='cube',
            color=color.dark_gray,
            position=(bridge_position.x + 2, bridge_position.y, bridge_position.z),
            scale=(4, 0.5, 3),
            collider='box',
            name='bridge_right'
        )
        
        # Add bridge details
        # Guard rails
        for side in [-1, 1]:
            rail_left = Entity(
                parent=bridge_left,
                model='cube',
                color=color.light_gray,
                position=(0, 0.3, side * 1.4),
                scale=(4, 0.3, 0.1)
            )
            
            rail_right = Entity(
                parent=bridge_right,
                model='cube',
                color=color.light_gray,
                position=(0, 0.3, side * 1.4),
                scale=(4, 0.3, 0.1)
            )
        
        # Bridge markings
        for section in [bridge_left, bridge_right]:
            for i in range(3):
                marking = Entity(
                    parent=section,
                    model='cube',
                    color=color.yellow,
                    position=(-1 + i, 0.26, 0),
                    scale=(0.5, 0.01, 0.2)
                )
        
        # Add to dynamic elements for animation
        bridge_left.is_bridge = True
        bridge_right.is_bridge = True
        bridge_left.open = False
        bridge_right.open = False
        
        self.dynamic_elements.append(bridge_left)
        self.dynamic_elements.append(bridge_right)
        
        # Add bridge supports
        for x_pos in [-4, 4]:
            support = Entity(
                model='cube',
                color=color.rgba(0.3, 0.3, 0.35, 1),
                position=(x_pos, -0.5, 0),
                scale=(1, 1, 5)
            )
        
        print("Bridge created")

    def _add_building_details(self, building, scale):
        """Add detailed windows, doors, and roof features to fallback cube buildings."""
        # Add windows with random patterns
        window_patterns = [
            (0.5, 0.5, color.azure),            # Standard blue windows
            (0.4, 0.6, color.rgba(1,1,0.8,1)),  # Yellow/warm light windows
            (0.5, 0.5, color.rgba(0.7,1,1,1)),  # Cool light windows
            (0.7, 0.3, color.rgba(0.5,0.5,0.5,1))  # Dark/tinted windows
        ]
        
        # Choose a pattern for this building
        window_width, window_height, window_color = random.choice(window_patterns)
        
        # Add windows on each floor
        for floor in range(1, int(scale[1])):
            # Skip some floors randomly for visual interest
            if random.random() < 0.1:
                continue
                
            for side in range(4):
                rotation = side * 90
                # Add multiple windows per floor for wider buildings
                window_count = max(1, int(scale[0] * 1.5))
                
                for w in range(window_count):
                    # Calculate offset based on building width
                    if window_count > 1:
                        offset = (w / (window_count-1) - 0.5) * (scale[0]*0.8)
                    else:
                        offset = 0
                        
                    window = Entity(
                        parent=building,
                        model='cube',
                        rotation_y=rotation,
                        position=(offset, floor - scale[1] / 2 + 0.5, scale[2] / 2 - 0.05),
                        scale=(window_width, window_height, 0.1),
                        color=window_color
                    )
                    
                    # Add random lit windows at night (some windows yellowish)
                    if random.random() < 0.3:
                        window.color = color.rgba(1, 0.9, 0.6, 1)
        
        # Add a more detailed roof based on building size
        if scale[0] > 3:
            # Larger building with more detailed roof
            roof_base = Entity(
                parent=building,
                model='cube',
                position=(0, scale[1] / 2 + 0.1, 0),
                scale=(scale[0], 0.2, scale[2]),
                color=color.dark_gray
            )
            
            # Add roof structures for larger buildings
            if scale[0] > 4:
                roof_structure = Entity(
                    parent=building,
                    model='cube',
                    position=(0, scale[1] / 2 + 0.5, 0),
                    scale=(scale[0]*0.3, 0.8, scale[2]*0.3),
                    color=color.gray
                )
                
                # Add antenna or water tower to some buildings
                if random.random() < 0.4:
                    antenna = Entity(
                        parent=building,
                        model='cylinder',
                        position=(random.uniform(-0.5, 0.5), scale[1] / 2 + 1.5, random.uniform(-0.5, 0.5)),
                        scale=(0.1, 2.0, 0.1),
                        color=color.dark_gray
                    )
        else:
            # Simple roof for smaller buildings
            roof = Entity(
                parent=building,
                model='cube',
                position=(0, scale[1] / 2 + 0.1, 0),
                scale=(scale[0], 0.2, scale[2]),
                color=color.dark_gray
            )
            
        # Add entrance/door at ground level
        door = Entity(
            parent=building,
            model='cube',
            rotation_y=random.choice([0, 90, 180, 270]),
            position=(0, -scale[1]/2 + 0.6, scale[2]/2 - 0.05),
            scale=(0.8, 1.2, 0.1),
            color=color.rgba(0.4, 0.3, 0.3, 1)
        )
        
        # Add building sign or detail to some buildings
        if random.random() < 0.3:
            sign = Entity(
                parent=building,
                model='cube',
                rotation_y=random.choice([0, 90, 180, 270]),
                position=(0, scale[1]/2 - 1, scale[2]/2 + 0.1),
                scale=(scale[0]*0.6, 0.4, 0.1),
                color=random.choice([
                    color.rgba(1, 0.2, 0.2, 1),  # Red sign
                    color.rgba(0.2, 0.6, 1, 1),  # Blue sign
                    color.rgba(1, 0.6, 0.1, 1),  # Orange sign
                ])
            )

    def _create_cube_city(self):
        """Fallback method to create a city with better cube buildings if models aren't available"""
        print("Creating fallback cube city with enhanced buildings...")
        
        # Define a wider variety of building types
        building_types = [
            {'scale': (2, randint(3, 8), 2), 'color': color.light_gray, 'style': 'modern'},
            {'scale': (3, randint(5, 9), 3), 'color': color.gray, 'style': 'office'},
            {'scale': (4, randint(7, 15), 4), 'color': color.dark_gray, 'style': 'highrise'},
            {'scale': (5, randint(3, 6), 5), 'color': color.rgba(0.6, 0.6, 0.7, 1), 'style': 'wide'},
            {'scale': (2.5, randint(10, 18), 2.5), 'color': color.rgba(0.7, 0.7, 0.8, 1), 'style': 'tower'},
            {'scale': (6, randint(4, 7), 6), 'color': color.rgba(0.5, 0.5, 0.5, 1), 'style': 'mall'},
        ]
        
        # Create a building placement grid to avoid overlaps
        grid_size = 12
        occupied_positions = []
        
        # First pass: place buildings on a grid with better spacing
        for x in range(-24, 25, grid_size):
            for z in range(-24, 25, grid_size):
                # Skip some positions for variety
                if random.random() < 0.25:
                    continue
                    
                pos_x = x + uniform(-1.5, 1.5)  # Add randomness to position
                pos_z = z + uniform(-1.5, 1.5)
                
                # Check if this position would overlap with existing buildings
                position_ok = True
                for occupied in occupied_positions:
                    if math.sqrt((pos_x - occupied[0])**2 + (pos_z - occupied[1])**2) < 8:
                        position_ok = False
                        break
                
                if not position_ok:
                    continue
                
                occupied_positions.append((pos_x, pos_z))
                
                # Select building type based on location
                if abs(x) < 10 and abs(z) < 10:
                    # Downtown - taller buildings
                    candidates = [bt for bt in building_types if bt['scale'][1] > 7]
                    building_type = random.choice(candidates if candidates else building_types)
                    # Make downtown buildings even taller
                    building_type = building_type.copy()  # Create a copy to modify
                    building_type['scale'] = (
                        building_type['scale'][0], 
                        int(building_type['scale'][1] * random.uniform(1.2, 1.5)), 
                        building_type['scale'][2]
                    )
                else:
                    # Suburbs - shorter, varied buildings
                    building_type = random.choice(building_types)
                
                # Create the building with enhanced details
                self._create_enhanced_cube_building(pos_x, pos_z, building_type)
        
        # Second pass: add smaller buildings and structures between the main buildings
        for _ in range(20):  # Add a good number of filler buildings
            for _ in range(10):  # Try several times to find a good spot
                pos_x = random.uniform(-25, 25)
                pos_z = random.uniform(-25, 25)
                
                # Check for overlap
                position_ok = True
                for occupied in occupied_positions:
                    if math.sqrt((pos_x - occupied[0])**2 + (pos_z - occupied[1])**2) < 6:
                        position_ok = False
                        break
                
                if position_ok:
                    occupied_positions.append((pos_x, pos_z))
                    
                    # Create a smaller filler building
                    small_building = {
                        'scale': (
                            random.uniform(1, 2.5), 
                            random.uniform(1, 3),
                            random.uniform(1, 2.5)
                        ),
                        'color': random.choice([
                            color.light_gray, 
                            color.gray,
                            color.rgba(0.6, 0.6, 0.5, 1)
                        ]),
                        'style': random.choice(['house', 'shop', 'garage'])
                    }
                    self._create_enhanced_cube_building(pos_x, pos_z, small_building)
                    break

    def _create_enhanced_cube_building(self, pos_x, pos_z, building_type):
        """Create an enhanced cube building with more details and variety"""
        # Create the main building structure
        building = Entity(
            model='cube',
            color=building_type['color'],
            position=(pos_x, building_type['scale'][1]/2, pos_z),
            scale=building_type['scale'],
            name=f'building_cube_{len(self.buildings)}',
            collider='box'
        )
        
        style = building_type.get('style', 'modern')
        
        # Different window patterns based on style
        window_patterns = {
            'modern': {'size': (0.5, 0.5), 'spacing': 1.2, 'color': color.azure},
            'office': {'size': (0.4, 0.8), 'spacing': 1.0, 'color': color.rgba(0.7, 0.9, 1.0, 1)},
            'highrise': {'size': (0.3, 0.6), 'spacing': 0.8, 'color': color.rgba(0.2, 0.3, 0.4, 1)},
            'tower': {'size': (0.4, 0.4), 'spacing': 1.5, 'color': color.rgba(0.8, 1.0, 1.0, 1)},
            'wide': {'size': (0.6, 0.4), 'spacing': 1.0, 'color': color.rgba(0.6, 0.8, 1.0, 1)},
            'mall': {'size': (0.7, 0.5), 'spacing': 1.3, 'color': color.rgba(0.9, 0.9, 0.7, 1)},
            'house': {'size': (0.5, 0.6), 'spacing': 1.2, 'color': color.rgba(1.0, 0.9, 0.7, 1)},
            'shop': {'size': (0.7, 0.7), 'spacing': 2.0, 'color': color.rgba(0.8, 0.8, 1.0, 1)},
            'garage': {'size': (1.0, 0.5), 'spacing': 2.0, 'color': color.rgba(0.5, 0.5, 0.5, 1)}
        }
        
        pattern = window_patterns.get(style, window_patterns['modern'])
        
        # Add windows based on the selected pattern
        window_width, window_height = pattern['size']
        window_color = pattern['color']
        spacing = pattern['spacing']
        
        # Number of windows per side is proportional to building width
        windows_per_side = max(1, int(building_type['scale'][0] / spacing))
        
        # Add windows for each floor
        for floor in range(1, int(building_type['scale'][1])):
            # Skip some floors randomly for penthouses or mechanical floors
            if random.random() < 0.15 and floor > building_type['scale'][1] * 0.7:
                continue
                
            for side in range(4):
                rotation = side * 90
                
                for w in range(windows_per_side):
                    # Calculate position for evenly spaced windows
                    if windows_per_side > 1:
                        offset = (w / (windows_per_side-1) - 0.5) * (building_type['scale'][0] * 0.8)
                    else:
                        offset = 0
                    
                    # Randomize window appearance
                    window_variation = random.random()
                    final_color = window_color
                    
                    # Some windows are lit (yellowish) for visual interest
                    if window_variation < 0.3:
                        final_color = color.rgba(1.0, 0.9, 0.5, 1) # Lit window
                    elif window_variation < 0.4:
                        final_color = color.rgba(0.3, 0.3, 0.3, 1) # Dark window
                    
                    window = Entity(
                        parent=building,
                        model='cube',
                        rotation_y=rotation,
                        position=(
                            offset,
                            floor - building_type['scale'][1]/2 + 0.5,
                            building_type['scale'][2]/2 - 0.05
                        ),
                        scale=(window_width, window_height, 0.1),
                        color=final_color
                    )
        
        # Add special features based on building style
        if style == 'modern' or style == 'highrise':
            # Add glass penthouse or crown
            if building_type['scale'][1] > 6:
                penthouse = Entity(
                    parent=building,
                    model='cube',
                    position=(0, building_type['scale'][1]/2 + 0.7, 0),
                    scale=(building_type['scale'][0] * 0.7, 1.5, building_type['scale'][2] * 0.7),
                    color=color.rgba(0.6, 0.9, 1.0, 0.8)
                )
        
        elif style == 'tower':
            # Add antenna or spire
            antenna = Entity(
                parent=building,
                model='cylinder',
                position=(0, building_type['scale'][1]/2 + 2, 0),
                scale=(0.1, 4.0, 0.1),
                color=color.dark_gray
            )
        
        elif style == 'mall' or style == 'shop':
            # Add storefront awnings or signage
            for side in range(4):
                rotation = side * 90
                awning = Entity(
                    parent=building,
                    model='cube',
                    rotation_y=rotation,
                    position=(0, -building_type['scale'][1]/2 + 1.2, building_type['scale'][2]/2 + 0.3),
                    scale=(building_type['scale'][0] * 0.8, 0.1, 0.6),
                    color=random.choice([
                        color.red,
                        color.yellow,
                        color.blue,
                        color.cyan
                    ])
                )
        
        # Add roof details for all buildings
        roof_height = 0.3 if building_type['scale'][1] > 5 else 0.2
        roof = Entity(
            parent=building,
            model='cube',
            position=(0, building_type['scale'][1]/2 + roof_height/2, 0),
            scale=(building_type['scale'][0], roof_height, building_type['scale'][2]),
            color=color.dark_gray
        )
        
        # Add technical equipment on roof for larger buildings
        if building_type['scale'][0] > 3 and random.random() < 0.7:
            # Add HVAC units and other roof equipment
            for _ in range(random.randint(1, 3)):
                equipment = Entity(
                    parent=building,
                    model='cube',
                    position=(
                        random.uniform(-building_type['scale'][0]/3, building_type['scale'][0]/3),
                        building_type['scale'][1]/2 + roof_height + 0.2,
                        random.uniform(-building_type['scale'][2]/3, building_type['scale'][2]/3)
                    ),
                    scale=(0.8, 0.4, 0.8),
                    color=color.gray
                )
        
        # Add entrance
        door = Entity(
            parent=building,
            model='cube',
            rotation_y=random.choice([0, 90, 180, 270]),
            position=(0, -building_type['scale'][1]/2 + 0.6, building_type['scale'][2]/2 - 0.03),
            scale=(1.2 if style == 'mall' else 0.8, 1.5 if style == 'mall' else 1.2, 0.1),
            color=color.rgba(0.3, 0.2, 0.2, 1) if style != 'mall' else color.rgba(0.7, 0.8, 1.0, 0.9)
        )
        
        # Add random chance of damage or distinguishing features
        if random.random() < 0.2:
            # Make building "under construction" or damaged
            if random.random() < 0.5:
                # Damaged look
                damage = Entity(
                    parent=building,
                    model='cube',
                    position=(
                        random.uniform(-building_type['scale'][0]/3, building_type['scale'][0]/3),
                        random.uniform(-building_type['scale'][1]/3, building_type['scale'][1]/3),
                        building_type['scale'][2]/2 - 0.05
                    ),
                    scale=(building_type['scale'][0] * 0.4, building_type['scale'][1] * 0.4, 0.1),
                    color=color.dark_gray
                )
                building.collapsible = True
                building.collapsed = False
            else:
                # Under construction look - add scaffolding
                for h in range(0, int(building_type['scale'][1]), 2):
                    scaffold = Entity(
                        parent=building,
                        model='cube',
                        position=(building_type['scale'][0]/2 + 0.5, h - building_type['scale'][1]/2 + 1, 0),
                        scale=(0.1, 2.0, building_type['scale'][2] * 0.8),
                        color=color.rgba(0.4, 0.4, 0.4, 1)
                    )
        
        # Store custom properties and building
        building.scale_y_original = building_type['scale'][1]  # Store original height for animations
        building.building_type = building_type
        building.style = style
        self.buildings.append(building)
        return building

    def _create_cube_building(self, pos_x, pos_z, building_types=None):
        """Create a basic cube building with improved details (fallback method)"""
        if not building_types:
            building_types = [
                {'scale': (2, randint(3, 8), 2), 'color': color.light_gray, 'style': 'modern'},
                {'scale': (3, randint(2, 5), 3), 'color': color.gray, 'style': 'office'},
                {'scale': (2, randint(4, 10), 2), 'color': color.dark_gray, 'style': 'highrise'},
                {'scale': (4, randint(3, 6), 4), 'color': color.rgba(0.6, 0.6, 0.7, 1), 'style': 'wide'},
            ]
            
        # Select random building type
        building_type = random.choice(building_types)
        
        # Check if the building_type has the new style parameter
        if 'style' in building_type:
            # Use the enhanced building creator
            return self._create_enhanced_cube_building(pos_x, pos_z, building_type)
        
        # Otherwise, use the legacy method for backward compatibility
        building = Entity(
            model='cube',
            color=building_type['color'],
            position=(pos_x, building_type['scale'][1]/2, pos_z),
            scale=building_type['scale'],
            name=f'building_cube_{len(self.buildings)}',
            collider='box'
        )
        
        # Add windows
        if building_type['scale'][1] > 4:
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

    def update(self):
        """Update the environment elements that need animation or state changes"""
        # Check if we have any dynamic elements to update
        if not self.dynamic_elements:
            return
            
        # Update bridge animation
        for element in self.dynamic_elements:
            # Handle bridge opening/closing
            if hasattr(element, 'is_bridge'):
                # Small random chance to toggle bridge state
                if random.random() < 0.001:  # 0.1% chance each frame
                    if element.open:
                        # Close the bridge
                        if element.name == 'bridge_left':
                            element.animate_position((element.x + 1.5, element.y, element.z), 
                                                   duration=2, curve=curve.in_out_sine)
                        else:
                            element.animate_position((element.x - 1.5, element.y, element.z), 
                                                   duration=2, curve=curve.in_out_sine)
                        element.open = False
                        print(f"{element.name} closing")
                    else:
                        # Open the bridge
                        if element.name == 'bridge_left':
                            element.animate_position((element.x - 1.5, element.y, element.z), 
                                                   duration=2, curve=curve.in_out_sine)
                        else:
                            element.animate_position((element.x + 1.5, element.y, element.z), 
                                                   duration=2, curve=curve.in_out_sine)
                        element.open = True
                        print(f"{element.name} opening")
            
            # Handle collapsible buildings
            if hasattr(element, 'collapsible') and not getattr(element, 'collapsed', False):
                # Random chance to collapse when player is nearby
                if random.random() < 0.0005:  # Very small chance each frame
                    element.collapsed = True
                    original_height = getattr(element, 'scale_y_original', element.scale_y)
                    element.animate_scale((element.scale_x, 0.2, element.scale_z), duration=0.5)
                    element.animate_position((element.x, 0.1, element.z), duration=0.5)
                    print(f"Building {element.name} collapsed!")
                    
                    # Add dust particles for the collapse effect
                    if hasattr(self, 'player') and self.player:
                        # Only create particles if the player is close
                        if math.dist((element.x, element.z), (self.player.x, self.player.z)) < 25:
                            for _ in range(15):
                                dust = Entity(
                                    model='sphere',
                                    color=color.rgba(0.5, 0.5, 0.5, 0.7),
                                    position=(
                                        element.x + random.uniform(-element.scale_x/2, element.scale_x/2),
                                        random.uniform(0, original_height),
                                        element.z + random.uniform(-element.scale_z/2, element.scale_z/2)
                                    ),
                                    scale=random.uniform(0.3, 0.8)
                                )
                                dust.animate_scale(0, duration=random.uniform(0.5, 1.2))
                                dust.animate_color(color.rgba(0.5, 0.5, 0.5, 0), duration=random.uniform(0.5, 1.2))
                                destroy(dust, delay=1.5)