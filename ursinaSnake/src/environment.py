from ursina import *
from random import randint, uniform, choice
import random
import os
import shutil
import math

# Define the base path for KayKit assets relative to the project root
KAYKIT_ASSETS_RELATIVE_PATH = os.path.join("..", "..", "KayKit_City_Builder_Bits_1.0_FREE", "Assets")

class Environment(Entity):
    def __init__(self, map_size=25):
        """
        Initialize the environment with the specified map size.
        
        Args:
            map_size (int): The size of the map (half-width and half-length)
        """
        super().__init__()
        print("Initializing environment...")
        
        # Store map size for use in other methods
        self.map_size = map_size
        
        # Get the base directory of the script to build absolute paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.script_dir)
        self.assets_root = os.path.join(self.project_root, "assets")
        self.kaykit_base_path = os.path.abspath(os.path.join(self.script_dir, KAYKIT_ASSETS_RELATIVE_PATH))
        
        # Initialize storage for environment objects
        self.buildings = []      # Store buildings for reference
        self.dynamic_elements = []  # Elements that can change during gameplay
        self.borders = []        # Store border objects
        
        # Create modern environment components
        self.create_ground()
        
        # Load assets before creating city
        self.building_models, self.building_texture = self.load_building_assets()
        
        # Create the city and obstacles
        self.create_city_layout()
        
        # Fix any buildings that might be floating or outside map boundaries
        self.fix_building_positions()
        
        # Create obstacles and other elements
        self.create_obstacles()
        self.create_dynamic_elements()
        
        # Create the map border last (after buildings are placed)
        self.create_modern_map_border()
        
        # Player reference (will be set by game.py)
        self.player = None

    def create_ground(self):
        """
        Create a large textured ground plane with modern design.
        Adjusts size based on the map_size parameter.
        """
        # Create/check for ground texture
        ground_texture_path = os.path.join(self.assets_root, "textures", "ground_texture.png") 
        
        # Fallback texture if the specific one doesn't exist
        ground_texture = 'grass'  # Use a built-in texture or a known good one
        
        if os.path.exists(ground_texture_path):
            ground_texture = load_texture(ground_texture_path)
        else:
            print(f"Warning: Ground texture not found at {ground_texture_path}. Using fallback.")

        # Create ground entity with size matched to map_size
        self.ground = Entity(
            model='plane',
            scale=(self.map_size * 2, 1, self.map_size * 2),  # Double the map_size for full width/length
            texture=ground_texture, 
            texture_scale=(10, 10),
            color=color.rgba(0.8, 0.8, 0.9, 1.0),  # Light blue-gray tint for modern look
            collider='box',
            position=(0, 0, 0)  # Ensure ground is at y=0
        )
        
        # Add grid lines for a modern tech look - adjust spacing based on map size
        grid_spacing = max(5, self.map_size // 5)  # Ensure reasonable spacing
        
        # Create horizontal grid lines
        for x in range(-self.map_size, self.map_size + 1, grid_spacing):
            Entity(
                model='quad',
                scale=(0.1, self.map_size * 2, 1),
                rotation_x=90,
                position=(x, 0.01, 0),  # Slightly above ground to prevent z-fighting
                color=color.rgba(0.3, 0.6, 0.9, 0.3),
                texture='white_cube'
            )
        
        # Create vertical grid lines
        for z in range(-self.map_size, self.map_size + 1, grid_spacing):
            Entity(
                model='quad',
                scale=(self.map_size * 2, 0.1, 1),
                rotation_x=90,
                position=(0, 0.01, z),  # Slightly above ground to prevent z-fighting
                color=color.rgba(0.3, 0.6, 0.9, 0.3),
                texture='white_cube'
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

    def fix_building_positions(self):
        """
        Ensure all buildings are properly positioned:
        1. Not floating in the air
        2. Within map boundaries
        3. At appropriate height
        """
        for building in self.buildings:
            # Fix y position to ensure buildings aren't floating
            # The y position should be half the building's height
            building.y = building.scale_y / 2
            
            # Keep buildings within map boundaries
            max_pos = self.map_size / 2 - building.scale_x / 2  # Leave room for the border
            
            # Clamp x position
            if building.x > max_pos:
                building.x = max_pos
            elif building.x < -max_pos:
                building.x = -max_pos
                
            # Clamp z position
            if building.z > max_pos:
                building.z = max_pos
            elif building.z < -max_pos:
                building.z = -max_pos
                
        print(f"Fixed positions for {len(self.buildings)} buildings")

    def _fix_building_overlaps(self):
        """
        Check for and fix overlapping buildings.
        
        This method iterates through all buildings and checks for overlaps.
        If buildings are too close or overlapping, it adjusts their positions.
        """
        min_distance = 5.0  # Minimum distance between buildings
        
        # Check each pair of buildings
        for i, building1 in enumerate(self.buildings):
            for j, building2 in enumerate(self.buildings):
                if i != j:  # Don't compare a building with itself
                    # Calculate distance between buildings
                    distance = (building1.position - building2.position).length()
                    
                    # If buildings are too close
                    if distance < min_distance:
                        # Calculate direction vector between buildings
                        direction = building1.position - building2.position
                        if direction.length() > 0:  # Avoid division by zero
                            direction = direction.normalized()
                        else:
                            # If buildings are exactly at the same position, move in random direction
                            direction = Vec3(
                                random.uniform(-1, 1),
                                0,
                                random.uniform(-1, 1)
                            ).normalized()
                        
                        # Move buildings apart
                        adjustment = direction * (min_distance - distance) / 2
                        building1.position += adjustment
                        building2.position -= adjustment
                        
                        # Make sure buildings stay within map bounds
                        for building in (building1, building2):
                            # Clamp X and Z coordinates to stay within map boundaries
                            building.x = max(min(building.x, self.map_size - 2), -self.map_size + 2)
                            building.z = max(min(building.z, self.map_size - 2), -self.map_size + 2)
        
        print("Fixed building overlaps")

    def _create_cube_city(self):
        """Create a city with modern procedurally textured buildings"""
        # Modern building type definitions with procedural texture generation
        building_types = [
            {'height': randint(5, 10), 'base_color': color.rgba(0.8, 0.8, 0.9, 1.0)},  # Light blue-gray
            {'height': randint(4, 7), 'base_color': color.rgba(0.7, 0.8, 0.85, 1.0)},  # Cool blue-gray
            {'height': randint(6, 12), 'base_color': color.rgba(0.75, 0.75, 0.8, 1.0)},  # Steel gray
            {'height': randint(4, 8), 'base_color': color.rgba(0.85, 0.9, 0.95, 1.0)},  # Light steel blue
        ]
        
        # Create buildings in a grid pattern with much more randomness and space
        # Expanded map size from -20,20 to -30,30
        for x in range(-30, 31, 10):  # Increased map size 
            for z in range(-30, 31, 10):  # Increased map size
                # 50% chance to skip a building to create open spaces
                if random.random() < 0.5:
                    continue
                    
                pos_x = x + uniform(-1, 1)
                pos_z = z + uniform(-1, 1)
                self._create_modern_building(pos_x, pos_z, building_types)

    def _create_modern_building(self, pos_x, pos_z, building_types=None):
        """Create a building with modern design"""
        if not building_types:
            building_types = [
                {'height': randint(5, 10), 'base_color': color.rgba(0.8, 0.8, 0.9, 1.0)},
                {'height': randint(4, 7), 'base_color': color.rgba(0.7, 0.8, 0.85, 1.0)},
                {'height': randint(6, 12), 'base_color': color.rgba(0.75, 0.75, 0.8, 1.0)},
                {'height': randint(4, 8), 'base_color': color.rgba(0.85, 0.9, 0.95, 1.0)},
            ]
            
        # Select random building type
        building_type = random.choice(building_types)
        height = building_type['height']
        width = random.randint(2, 4)
        depth = random.randint(2, 4)
        
        # Randomly choose building shape - sometimes create interesting shapes
        shape_type = random.choice(['cube', 'L', 'tower'])
        
        building = Entity(
            model='cube',
            position=(pos_x, height/2, pos_z),
            scale=(width, height, depth),
            color=building_type['base_color'],
            name=f'building_cube_{len(self.buildings)}'
        )
        
        # Generate modern texture with large glass windows
        building_texture = self.generate_modern_building_texture(
            building_type['base_color'], 
            width=128, 
            height=128,
            window_color=color.rgba(0.7, 0.9, 1.0, 1.0)
        )
        
        building.texture = building_texture
        building.collider = 'box'
        
        # Add architectural details based on building shape
        if shape_type == 'L':
            # Create L-shaped building by adding a wing
            wing = Entity(
                parent=building,
                model='cube',
                position=(-(width/2), 0, depth/2),
                scale=(width/2, 0.9, depth/2),
                color=building_type['base_color'],
                texture=building_texture
            )
        elif shape_type == 'tower':
            # Create tower with narrower top section
            tower_top = Entity(
                parent=building,
                model='cube',
                position=(0, height/2, 0),
                scale=(width*0.6, height*0.3, depth*0.6),
                color=building_type['base_color'],
                texture=building_texture
            )
            
            # Add antenna or spire to some tall buildings
            if height > 8 and random.random() < 0.7:
                antenna = Entity(
                    parent=building,
                    model='cylinder',
                    position=(0, height, 0),
                    scale=(0.1, random.uniform(1, 2), 0.1),
                    color=color.light_gray
                )
        
        # Add a modern roof with potential for roof garden (green) or solar panels (blue tint)
        roof_type = random.choice(['garden', 'solar', 'plain'])
        roof_color = color.rgba(0.2, 0.6, 0.3, 1.0) if roof_type == 'garden' else \
                    color.rgba(0.2, 0.4, 0.7, 1.0) if roof_type == 'solar' else \
                    color.dark_gray
                    
        roof = Entity(
            parent=building,
            model='cube',
            position=(0, 0.5, 0),
            scale=(1, 0.05, 1),
            color=roof_color
        )
        
        # Add roof details
        if roof_type == 'garden':
            # Add some greenery spots
            for _ in range(3):
                spot = Entity(
                    parent=roof,
                    model='cube',
                    scale=(random.uniform(0.1, 0.3), 0.1, random.uniform(0.1, 0.3)),
                    position=(random.uniform(-0.4, 0.4), 0.1, random.uniform(-0.4, 0.4)),
                    color=color.rgba(0.1, 0.5, 0.1, 1.0)
                )
        elif roof_type == 'solar':
            # Add solar panel grid
            for x in range(-1, 2):
                for z in range(-1, 2):
                    panel = Entity(
                        parent=roof,
                        model='quad',
                        scale=(0.2, 0.2, 0.2),
                        position=(x*0.3, 0.1, z*0.3),
                        rotation_x=90,
                        color=color.rgba(0.1, 0.3, 0.8, 1.0)
                    )

        self.buildings.append(building)
        return building

    def generate_modern_building_texture(self, base_color, width=128, height=128, window_color=color.azure):
        """Generate a procedural texture for modern glass buildings"""
        from PIL import Image, ImageDraw
        import numpy as np
        
        # Create a blank image with the base color
        r, g, b = int(base_color.r * 255), int(base_color.g * 255), int(base_color.b * 255)
        img = Image.new('RGBA', (width, height), (r, g, b, 255))
        draw = ImageDraw.Draw(img)
        
        # Decide between different modern facade patterns
        pattern_type = random.choice(['grid', 'horizontal', 'vertical', 'asymmetric'])
        
        # Convert window color to RGB
        w_r, w_g, w_b = int(window_color.r * 255), int(window_color.g * 255), int(window_color.b * 255)
        
        if pattern_type == 'grid':
            # Modern grid pattern - common in glass skyscrapers
            grid_cols = random.randint(4, 8)
            grid_rows = random.randint(8, 16)
            
            cell_width = width // grid_cols
            cell_height = height // grid_rows
            
            for row in range(grid_rows):
                for col in range(grid_cols):
                    # Create glass panel
                    x1 = col * cell_width + 2  # Small gap between panels
                    y1 = row * cell_height + 2
                    x2 = (col + 1) * cell_width - 2
                    y2 = (row + 1) * cell_height - 2
                    
                    # Randomize reflection/lighting slightly
                    reflection = random.randint(-20, 20)
                    panel_color = (
                        min(255, max(0, w_r + reflection)),
                        min(255, max(0, w_g + reflection)),
                        min(255, max(0, w_b + reflection)),
                        255
                    )
                    
                    draw.rectangle([x1, y1, x2, y2], fill=panel_color)
                    
        elif pattern_type == 'horizontal':
            # Horizontal bands of glass and material
            bands = random.randint(6, 12)
            band_height = height // bands
            
            for i in range(bands):
                y1 = i * band_height
                y2 = (i + 1) * band_height - 2  # Gap between bands
                
                # Alternate between glass and material
                if i % 2 == 0:
                    draw.rectangle([0, y1, width, y2], fill=(w_r, w_g, w_b, 255))
                else:
                    # Structural band
                    draw.rectangle([0, y1, width, y2], fill=(r-30, g-30, b-30, 255))
                    
        elif pattern_type == 'vertical':
            # Vertical sections - common in modern architecture
            sections = random.randint(3, 6)
            section_width = width // sections
            
            for i in range(sections):
                x1 = i * section_width
                x2 = (i + 1) * section_width - 2
                
                # Alternate materials or use consistent glass
                material_type = random.choice(['glass', 'solid'])
                
                if material_type == 'glass' or i % 2 == 0:
                    draw.rectangle([x1, 0, x2, height], fill=(w_r, w_g, w_b, 255))
                else:
                    # Solid section
                    draw.rectangle([x1, 0, x2, height], fill=(r-20, g-20, b-20, 255))
                    
        else:  # asymmetric
            # Create an asymmetric modern pattern
            # Large glass sections with accent strips
            draw.rectangle([0, 0, width, height], fill=(w_r, w_g, w_b, 255))
            
            # Add random accent strips
            num_accents = random.randint(2, 5)
            for _ in range(num_accents):
                # Decide between horizontal or vertical accent
                if random.random() < 0.5:
                    # Horizontal accent
                    y_pos = random.randint(0, height)
                    height_acc = random.randint(10, 30)
                    draw.rectangle([0, y_pos, width, y_pos + height_acc], 
                                  fill=(r-30, g-30, b-30, 255))
                else:
                    # Vertical accent
                    x_pos = random.randint(0, width)
                    width_acc = random.randint(10, 30)
                    draw.rectangle([x_pos, 0, x_pos + width_acc, height], 
                                  fill=(r-30, g-30, b-30, 255))
        
        # Add some subtle texture variation
        pixels = np.array(img)
        noise = (np.random.rand(height, width, 4) * 10 - 5).astype(np.int32)
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)
        
        # Convert to Ursina texture
        texture = Texture(img)
        return texture

    def create_city_layout(self):
        """
        Create a city with modern procedurally generated buildings.
        
        This method places buildings throughout the map while respecting the map
        boundaries defined by self.map_size. It uses the previously loaded building
        models or falls back to procedurally generated buildings if models aren't available.
        """
        print("Creating city with procedural buildings")
        
        # Define safe zone from map edge to prevent buildings from being placed too close to borders
        safe_margin = 2.0
        safe_area_limit = self.map_size - safe_margin
        
        # If we have models available, try to use them
        if self.building_models:
            print(f"Using {len(self.building_models)} building model types")
            num_buildings = 30  # Reasonable number of buildings for a small city
            
            # Generate buildings with proper spacing
            for i in range(num_buildings):
                # Choose random position within safe area
                pos_x = random.uniform(-safe_area_limit, safe_area_limit)
                pos_z = random.uniform(-safe_area_limit, safe_area_limit)
                
                # Choose random building type
                building_type = random.choice(list(self.building_models.keys()))
                model_path = self.building_models[building_type]
                
                # Random scale factor for variety
                scale_factor = random.uniform(2.0, 4.0)
                
                try:
                    # Create building with model
                    building = Entity(
                        model=model_path,
                        texture=self.building_texture,
                        position=(pos_x, 0, pos_z),  # Start at ground level
                        scale=scale_factor,
                        collider='box',
                        name=f'building_{building_type}_{i}'
                    )
                    
                    # Adjust Y position to align with ground
                    building.y = building.scale_y / 2
                    
                    # Store the building
                    self.buildings.append(building)
                    print(f"Created building {building_type} at ({pos_x}, {pos_z})")
                    
                except Exception as e:
                    print(f"Error creating building {building_type}: {e}")
                    # Fall back to cube building if model fails to load
                    self._create_modern_building(pos_x, pos_z)
        else:
            # Fall back to procedural cube buildings
            print("No building models available, creating procedural cube buildings")
            self._create_cube_city()
            
        # Check for overlapping buildings and fix their positions
        self._fix_building_overlaps()
        
        print(f"City layout created with {len(self.buildings)} buildings")

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
        """Create dynamic environment elements - only collapsible buildings now"""
        # Set some buildings as collapsible
        for building in self.buildings:
            # 15% chance for a building to be collapsible
            if random.random() < 0.15:
                building.collapsible = True
                building.collapsed = False
                self.dynamic_elements.append(building)
                print(f"Made building {building.name} collapsible")
                
                # Add a modern warning indicator on top
                warning = Entity(
                    parent=building,
                    model='sphere',  # More modern than cube
                    color=color.yellow,
                    scale=(0.4, 0.4, 0.4),
                    y=5,  # Place on top of building
                    billboard=True  # Always face camera
                )
                # Make it blink
                warning.animate_color(color.red, duration=0.5, loop=True)
    
    def update(self):
        """Update dynamic environment elements"""
        # Update elements like collapsing buildings only
        # Wrap in try-except to prevent crashes
        try:
            for element in self.dynamic_elements:
                # Skip if element has been destroyed
                if not element or not element.enabled:
                    continue
                    
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
        except Exception as e:
            print(f"Error in environment update: {e}")
            # This prevents crashes by catching any exceptions

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
    
    def create_modern_map_border(self):
        """
        Create a sleek, modern border around the map that prevents the player from
        leaving the map area but does not cause damage.
        """
        border_thickness = 0.5  # Thinner, more sleek
        border_height = 4
        
        # Use a gradient of colors for a more modern look
        border_colors = [
            color.rgba(0.2, 0.4, 0.8, 0.7),  # Blue with transparency
            color.rgba(0.1, 0.3, 0.7, 0.7),  # Darker blue with transparency
            color.rgba(0.3, 0.5, 0.9, 0.7),  # Lighter blue with transparency
            color.rgba(0.2, 0.4, 0.8, 0.7),  # Blue with transparency
        ]
        
        # Create corner pillars for a modern look
        corners = [
            Vec3(self.map_size, 0, self.map_size),      # Northeast
            Vec3(self.map_size, 0, -self.map_size),     # Southeast
            Vec3(-self.map_size, 0, -self.map_size),    # Southwest
            Vec3(-self.map_size, 0, self.map_size),     # Northwest
        ]
        
        # Create corner pillars
        pillars = []
        for i, corner in enumerate(corners):
            pillar = Entity(
                model='cylinder',
                position=corner + Vec3(0, border_height/2, 0),
                scale=(1.5, border_height, 1.5),
                color=border_colors[i],
                collider='cylinder',
                tag='border'  # Tag for identification
            )
            pillars.append(pillar)
            
            # Add a light on top of each corner
            light = Entity(
                parent=pillar,
                model='sphere',
                y=border_height/2 + 0.2,
                scale=0.5,
                color=color.yellow,
                billboard=False
            )
            
            # Make the light pulse
            light.animate_color(
                color.rgba(1.0, 0.9, 0.1, 1.0),
                duration=1.0,
                curve=curve.in_out_sine,
                loop=True
            )
        
        # Initialize border collection
        self.borders = []
        
        # Create north border
        north = Entity(
            model='cube',
            position=(0, border_height/2, self.map_size),
            scale=(self.map_size * 2, border_height, border_thickness),
            color=border_colors[0],
            collider='box',
            tag='border'  # Tag for identification
        )
        self.borders.append(north)
        
        # Add pattern to the borders
        self.add_border_pattern(north, False)
        
        # Create south border
        south = Entity(
            model='cube',
            position=(0, border_height/2, -self.map_size),
            scale=(self.map_size * 2, border_height, border_thickness),
            color=border_colors[1],
            collider='box',
            tag='border'  # Tag for identification
        )
        self.borders.append(south)
        
        self.add_border_pattern(south, False)

        # Create east border
        east = Entity(
            model='cube',
            position=(self.map_size, border_height/2, 0),
            scale=(border_thickness, border_height, self.map_size * 2),
            color=border_colors[2],
            collider='box',
            tag='border'  # Tag for identification
        )
        self.borders.append(east)
        
        self.add_border_pattern(east, True)

        # Create west border
        west = Entity(
            model='cube',
            position=(-self.map_size, border_height/2, 0),
            scale=(border_thickness, border_height, self.map_size * 2),
            color=border_colors[3],
            collider='box',
            tag='border'  # Tag for identification
        )
        self.borders.append(west)
        
        self.add_border_pattern(west, True)
        
        print(f"Created modern map border with {len(self.borders)} wall segments and {len(pillars)} corner pillars")
    
    def add_border_pattern(self, border, is_vertical):
        """Add a modern pattern to the border walls without creating purple lasers"""
        # Add subtle, non-distracting border patterns
        num_lines = 10
        
        if is_vertical:
            # Vertical border (east-west)
            for i in range(num_lines):
                z_pos = -25 + (i * 5)
                line = Entity(
                    parent=border,
                    model='quad',
                    color=color.rgba(0.8, 0.8, 0.9, 0.3),  # Very subtle light color
                    double_sided=True,
                    scale=(0.1, 0.5, 1),  # Much smaller lines
                    y=random.uniform(-1, 1),
                    z=z_pos - border.position.z
                )
        else:
            # Horizontal border (north-south)
            for i in range(num_lines):
                x_pos = -25 + (i * 5)
                line = Entity(
                    parent=border,
                    model='quad',
                    color=color.rgba(0.8, 0.8, 0.9, 0.3),  # Very subtle light color
                    double_sided=True,
                    scale=(1, 0.5, 0.1),  # Much smaller lines
                    y=random.uniform(-1, 1),
                    x_pos=x_pos - border.position.x
                )
                
        # No more pulsing animations that create the purple laser effect

    def create_obstacle(self, obstacle_type, position):
        """Create a modern version of obstacles"""
        if obstacle_type == 'hydrant':
            obstacle = Entity(
                model='cylinder',
                color=color.rgb(200, 0, 0),
                position=position,
                scale=(0.5, 1, 0.5),
                collider='cylinder',
                name=f'obstacle_hydrant'
            )
            # Add top cap
            cap = Entity(
                parent=obstacle,
                model='sphere',
                color=color.rgb(200, 0, 0),
                position=(0, 0.6, 0),
                scale=(0.6, 0.2, 0.6)
            )
            
        elif obstacle_type == 'bench':
            # More modern bench design
            obstacle = Entity(
                model='cube',
                color=color.rgb(100, 100, 110),  # Modern gray
                position=position,
                scale=(2, 0.15, 0.8),
                collider='box',
                name=f'obstacle_bench'
            )
            # Add bench legs - more modern design
            leg1 = Entity(
                parent=obstacle,
                model='cube',
                color=color.rgb(80, 80, 90),  # Darker gray
                position=(-0.7, -0.4, 0),
                scale=(0.1, 0.7, 0.8)
            )
            leg2 = Entity(
                parent=obstacle,
                model='cube',
                color=color.rgb(80, 80, 90),
                position=(0.7, -0.4, 0),
                scale=(0.1, 0.7, 0.8)
            )
            
        elif obstacle_type == 'trash':
            # Modern trash bin
            obstacle = Entity(
                model='cylinder',
                color=color.rgba(0.2, 0.6, 0.3, 1.0),  # Modern green
                position=position,
                scale=(0.7, 1.2, 0.7),
                collider='cylinder',
                name=f'obstacle_trash'
            )
            # Add lid
            lid = Entity(
                parent=obstacle,
                model='cylinder',
                color=color.rgba(0.15, 0.5, 0.25, 1.0),  # Darker green
                position=(0, 0.7, 0),
                scale=(0.8, 0.1, 0.8)
            )
            
            # Add recycling symbol
            symbol = Entity(
                parent=obstacle,
                model='quad',
                texture='white_cube',  # Ideally would be a recycling symbol texture
                color=color.white,
                scale=(0.5, 0.5, 0.5),
                position=(0, 0.3, -0.36),
                billboard=False
            )
            
        elif obstacle_type == 'barrier':
            # Modern safety barrier
            obstacle = Entity(
                model='cube',
                color=color.rgba(0.3, 0.3, 0.9, 1.0),  # Modern blue
                position=position,
                scale=(2, 1, 0.3),
                collider='box',
                name=f'obstacle_barrier'
            )
            # Add modern stripes
            for i in range(3):
                stripe = Entity(
                    parent=obstacle,
                    model='quad',
                    texture='white_cube',
                    color=color.white,
                    position=(0.5 - i, 0.3, 0.16),
                    scale=(0.2, 0.6)
                )
                
        else:
            # Default modern obstacle
            obstacle = Entity(
                model='sphere',  # More interesting than cube
                color=color.rgba(0.7, 0.7, 0.8, 1.0),  # Modern light gray
                position=position,
                scale=(1, 1, 1),
                collider='sphere',
                name=f'obstacle_generic'
            )
            
        return obstacle