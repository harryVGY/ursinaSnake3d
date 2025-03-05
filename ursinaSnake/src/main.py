from ursina import *

def update():
    # This function will be called every frame to update the game state
    pass

app = Ursina()

# Initialize the game window
app.window.title = 'Ursina Snake'
app.window.borderless = False
app.window.size = (800, 600)

# Start the game loop
app.run()