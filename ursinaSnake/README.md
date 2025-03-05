# Ursina Snake Game

## Overview
Ursina Snake is a simple yet engaging snake game built using the Ursina engine. The game allows players to control a snake, eat food, and grow in size while avoiding collisions with the walls and itself.

## Project Structure
```
ursinaSnake
├── src
│   ├── main.py        # Entry point of the game
│   ├── game.py        # Game management and state handling
│   ├── snake.py       # Snake class and its functionalities
│   ├── food.py        # Food class and spawning logic
│   └── utils.py       # Utility functions for the game
├── assets
│   ├── textures       # Directory for texture files (snake, food, etc.)
│   └── sounds         # Directory for sound files (background music, effects)
├── requirements.txt   # List of dependencies
└── README.md          # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ursinaSnake.git
   ```
2. Navigate to the project directory:
   ```
   cd ursinaSnake
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Game
To start the game, run the following command:
```
python src/main.py
```

## Controls
- Use the arrow keys to control the direction of the snake.
- Eat the food to grow the snake and increase your score.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.