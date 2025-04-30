from ursina import *
import sys
import os

# Add the parent directory to sys.path to make imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)

# Set up error handling to show where issues occur
try:
    from game import Game
    from camera import setup_camera
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running the game from the correct directory")
    sys.exit(1)

# Temporarily comment out WebExporter to focus on getting the game running
"""
try:
    from panda3d.web import WebExporter
    
    # Define paths
    output_dir = os.path.join(parent_dir, "web_build")
    
    # Initialize exporter
    exporter = WebExporter()
    
    # Add your Ursina game files
    exporter.add_python_file(os.path.join(current_dir, "main.py"))
    exporter.add_python_file(os.path.join(current_dir, "game.py"))
    exporter.add_python_file(os.path.join(current_dir, "camera.py"))
    exporter.add_python_file(os.path.join(current_dir, "player.py"))
    exporter.add_python_file(os.path.join(current_dir, "enemy.py"))
    exporter.add_python_file(os.path.join(current_dir, "environment.py"))
    
    # Add assets directory
    asset_dir = os.path.join(parent_dir, "assets")
    if os.path.exists(asset_dir):
        exporter.add_directory(asset_dir, "assets")
    
    # Export the game
    exporter.export(output_dir)
    print(f"Game exported to {output_dir}")
except ImportError:
    print("WebExporter not available - skipping web export")
"""

def main():
    try:
        # Initialize the Ursina engine with proper path to icon
        icon_path = os.path.join(parent_dir, "assets", "models", "snake.ico")
        if os.path.exists(icon_path):
            app = Ursina(icon=icon_path, title="snakeX3000")
        else:
            # Fallback if icon not found
            print(f"Warning: Icon not found at {icon_path}")
            app = Ursina(title="snakeX3000")
            
        # Create the game instance
        game = Game()
        game.setup()
        
        # Set up camera after player is created
        try:
            camera_controller = setup_camera(game.player)
        except Exception as e:
            print(f"Camera init error: {e}")

        # Run the game
        app.run()
    except Exception as e:
        # Print detailed error information
        import traceback
        print(f"Error starting game: {e}")
        traceback.print_exc()
        
if __name__ == "__main__":
    main()