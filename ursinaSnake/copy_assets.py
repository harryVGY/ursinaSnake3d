import os
import shutil

def copy_models_to_assets():
    """Copy building models from downloads to the assets folder"""
    # Source paths
    source_dir = os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        "KayKit_City_Builder_Bits_1.0_FREE",
        "KayKit_City_Builder_Bits_1.0_FREE",
        "Assets",
        "obj"
    )
    
    # Destination paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, "assets", "models", "buildings")
    
    # Check if the path exists and is a file (not a directory)
    if os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
        print(f"Found a file at {dest_dir}. Renaming it to {dest_dir}.bak")
        # Rename the existing file
        os.rename(dest_dir, f"{dest_dir}.bak")
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy the files
    try:
        # Building H
        building_h_obj = os.path.join(source_dir, "building_H.obj")
        building_h_mtl = os.path.join(source_dir, "building_H.mtl")
        
        if os.path.exists(building_h_obj) and os.path.exists(building_h_mtl):
            shutil.copy2(building_h_obj, dest_dir)
            shutil.copy2(building_h_mtl, dest_dir)
            print(f"Copied building_H files to {dest_dir}")
            
            # Update the models info file
            with open(os.path.join(dest_dir, "models_info.txt"), "w") as f:
                f.write(f"building_H.obj\nbuilding_H.mtl\n")
            
            print("Assets copied successfully!")
        else:
            print(f"Building H files not found at {source_dir}")
            print(f"Source directory: {source_dir}")
            print(f"Files in source directory: {os.listdir(source_dir) if os.path.exists(source_dir) else 'Directory not found'}")
    except Exception as e:
        print(f"Error copying files: {e}")

if __name__ == "__main__":
    copy_models_to_assets()
    print("Run this script to copy models from your Downloads folder to the assets folder.")
    print("Then run the main game to use the 3D building models.")
