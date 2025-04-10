import os
import shutil
import sys

def setup_assets():
    """Copy building models from downloads to the assets folder and verify"""
    print("Setting up game assets...")
    
    # Source paths - where to find the original model files
    source_dir = os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        "KayKit_City_Builder_Bits_1.0_FREE",
        "KayKit_City_Builder_Bits_1.0_FREE",
        "Assets",
        "obj"
    )
    
    # Destination paths - where to copy the files in your game
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, "assets", "models", "buildings")
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Files to copy
    files_to_copy = [
        "building_H.obj",
        "building_H.mtl"
    ]
    
    # Copy the files
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
