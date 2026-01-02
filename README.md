# Basketball Rotations

A Basketball Rotation Algorithm that dynamically assigns players to the court in timed intervals to balance skill, size, and fairness while ensuring everyone meets minimum playing-time constraints.

This project was created to help a friend who coaches youth basketball. The algorithm uses **Streamlit** as an interface to make it user-friendly and accessible.

## Features

- **Dynamic Player Assignments**: Automatically defines which players should be on the court at specific time intervals.
- **Fairness Focused**: Makes sure every player meets their minimum playing-time requirements.
- **Balance Skills and Size**: Takes player attributes like skill levels and physical attributes into account when creating rotations.
- **Customizable**: Adaptable to various lineup strategies and game rules.

## Why Use This?

Balancing a team during a game while keeping track of time and rotation fairness is a challenging task for coaches. This algorithm simplifies and automates the process, ensuring every team member gets appropriate playing time without sacrificing performance.

## Language

This project is implemented in **Python** and leverages **Streamlit** for its user interface.

## Getting Started

To use this project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/dray19/Basketball_Rotations.git
   cd Basketball_Rotations
   ```

2. Install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## How It Works

### Inputs
- **Players Data**: Includes details like player names, skills, size, and other attributes.
- **Game Configuration**: Time intervals, court capacity, etc.

### Outputs
- **Rotation Schedule**: Which player(s) should start and substitute at each time interval.

The algorithm ensures:
- Each player meets their minimum playing time.
- Balanced lineup configurations based on input considerations (e.g., skill, size).

### Link to app
https://basketballrotations-f9ufyc8yawhgg9vukxe9ez.streamlit.app/