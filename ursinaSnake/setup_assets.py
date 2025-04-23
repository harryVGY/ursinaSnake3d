import os
import shutil
import sys

def setup_assets():
    """Copy building models from downloads to the assets folder and verify"""
    print("Setting up game assets...")
    
    # Source paths - get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Source path using the correct location - directly in the project folder
    source_dir = os.path.join(
        project_root,  # The ursinaSnake folder is the project root
        "KayKit_City_Builder_Bits_1.0_FREE",
        "Assets",
        "obj"
    )
    
    print(f"Looking for KayKit assets in: {source_dir}")
    
    # Destination paths - where to copy the files in your game
    dest_dir = os.path.join(script_dir, "assets", "models", "buildings")
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Files to copy (all building models, obstacles, and texture)
    building_files = [
        f"building_{c}.obj" for c in "ABCDEFGH"
    ] + [
        f"building_{c}.mtl" for c in "ABCDEFGH"
    ]
    obstacle_files = [
        f"{name}.obj" for name in ["firehydrant", "trash_A", "trash_B", "dumpster", "bench"]
    ] + [
        f"{name}.mtl" for name in ["firehydrant", "trash_A", "trash_B", "dumpster", "bench"]
    ]
    files_to_copy = building_files + ["citybits_texture.png"]

    # Copy building files
    success = True
    try:
        for filename in files_to_copy:
            source_file = os.path.join(source_dir, filename)
            dest_file = os.path.join(dest_dir, filename)
            if os.path.exists(source_file):
                shutil.copy2(source_file, dest_file)
                print(f"Copied {filename} to {dest_dir}")
            else:
                print(f"ERROR: Source file not found: {source_file}")
                success = False

        # Copy obstacle files
        obstacles_dest_dir = os.path.join(script_dir, "assets", "models", "obstacles")
        os.makedirs(obstacles_dest_dir, exist_ok=True)
        for filename in obstacle_files:
            source_file = os.path.join(source_dir, filename)
            dest_file = os.path.join(obstacles_dest_dir, filename)
            if os.path.exists(source_file):
                shutil.copy2(source_file, dest_file)
                print(f"Copied {filename} to {obstacles_dest_dir}")
            else:
                print(f"ERROR: Source file not found: {source_file}")
                success = False

        if success:
            # Update the models info file
            with open(os.path.join(dest_dir, "models_info.txt"), "w") as f:
                for filename in files_to_copy:
                    f.write(f"{os.path.join(dest_dir, filename)}\n")
            
            print("\nAssets copied successfully!")
            print(f"\nBuilding models are now available in: {dest_dir}")
            print("\nYou can now run the game with: python src/main.py")
        else:
            print("\nWARNING: Some files could not be copied.")
            print("Please make sure the KayKit City Builder files are in your Downloads folder.")
    except Exception as e:
        print(f"Error copying files: {e}")

if __name__ == "__main__":
    setup_assets()
    input("\nPress Enter to continue...")
