from ursina import *
from game import Game
from camera import setup_camera

# Initialize the Ursina engine
app = Ursina()

# Create the game instance
game = Game()
game.setup()

# Set up camera after player is created
camera_controller = setup_camera(game.player)

# Run the game
app.run()