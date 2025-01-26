# AIFinalProject

<img src="readme_img.png" alt="Description of image" width="450" height="250">


# Flow Free Solver Project

This project implements a solver for the game **Flow Free**, along with tools to evaluate the solver's performance and generate analytical plots. The solver can be run with a graphical user interface (GUI) to visualize the solutions, and the evaluation scripts provide insights into the efficiency and accuracy of different solvers.

## Project Structure

- **main.py**: The main script that sets up and runs the Flow Free solver using various algorithms such as A*, DFS, BFS, UCS, SAT, and Reinforcement Learning (QLearning and ApproxQLearning).
- **evaluate_solvers.py**: A script to evaluate the performance of different solvers on multiple levels and grid sizes, logging metrics such as time taken and nodes expanded.
- **plots.py**: A script for generating visual plots based on the results obtained from solver evaluations. It uses libraries such as Matplotlib, Seaborn, and Plotly for creating various types of charts.

## How to Run the Project

### 0. Prerequisites
Before running the main solver, you need to install the required libraries by running the following command:

```bash
pip install -r requirements.txt
```

**note that we worked on python version 3.1.2 on mac OS.**

### 1. Running the Main Solver
Now you can run the main solver. you can choose the algorithm, grid size and the level you want 
by changing the following variables in the main.py file:

```python
algorithm = "SAT" # "A*", "DFS", "BFS", "UCS", "SAT", "Q learning", "AQ learning"
grid_size = 5 # 5 - 14
level = 5 # 1 - 10
```

You can run the Flow Free solver with a GUI that displays the board and the solved board
by running the following command:

```bash
python main.py
```

### 2. Evaluating the Solvers
You can evaluate the performance of different solvers on multiple levels and grid sizes by running the evaluate_solvers.py script.
before running the evaluation script, you can choose the algorithms, grid sizes, and levels you want to evaluate by changing the following variables in the evaluate_solvers.py file:

```python
algorithm_type = "Search"  # "Search" or "SAT" or "All"
min_grid_size = 5 # 5 - 14
max_grid_size = 5 # 5 - 14
```

### 3. Generating Plots
You can generate visual plots based on the results obtained from solver evaluations by running the plots.py script.
before running the plots scripts, you must have the results csv with the correct name in the res folder.
all the results are in the report, this is just the code we used to generate the plots.

```bash
python plots.py
```


