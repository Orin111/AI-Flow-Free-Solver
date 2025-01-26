import tkinter as tk
import time

from flow_game.flow_free_problem import FlowFreeProblem
from problems.level_creator import create_level
from solvers import solver
from solvers.SAT import FlowFreeSAT
from solvers.q_learning_agent import QLearningAgent
from solvers.flow_free_env import FlowFreeEnvironment
from gui import FlowFreeGUI
import solvers.heuristics as heuristics
from solvers.approx_q_learning import ApproxQLearningAgent

SAT_NO_SOLUTION = "UNSAT"
NO_SOLUTION_MESSAGE = "No solution found."
SOLUTION_FOUND_MESSAGE = "Solution found."


def run_search_algorithm(search_algorithm_name, problem):
    """
    Run the search algorithm on the given problem.
    :param search_algorithm_name: name of the search algorithm to run
    :param problem: the problem to solve
    :return: a list of actions that reaches the goal state
    """
    if search_algorithm_name == "DFS":
        return solver.depth_first_search(problem)
    elif search_algorithm_name == "UCS":
        return solver.uniform_cost_search(problem)
    elif search_algorithm_name == "A*":
        return solver.a_star_search(problem, heuristics.combined_heuristic)
    elif search_algorithm_name == "BFS":
        return solver.breadth_first_search(problem)


def choose_rl_agent(agent_name):
    """
    Choose the reinforcement learning agent to use.
    :param agent_name: name of the agent to use
    :return: the chosen agent
    """
    if agent_name == "Q learning":
        return QLearningAgent(0.7, 0.9, 0.75)
    elif agent_name == "AQ learning":
        return ApproxQLearningAgent()


def start_search(problem, algorithm_name):
    """
    Start the search algorithm on the given problem.
    :param problem: the problem to solve
    :param algorithm_name: the name of the algorithm to use
    :return: a list of actions that reaches the goal state and the time taken
    """
    start_time = time.time()
    actions = run_search_algorithm(algorithm_name, problem)
    elapsed_time = time.time() - start_time
    print(f"result(time,expended nodes): {elapsed_time},{problem.expanded}")
    return actions, elapsed_time


def execute_actions_with_delay(gui, curr_state, actions, index=0):
    """
    Execute the actions with a delay to display the moves on the GUI.
    :param gui: gui object to display the moves
    :param curr_state: current state of the game
    :param actions: list of actions to execute
    :param index: index of the current action
    """
    if index < len(actions):
        action = actions[index]
        curr_state = curr_state.do_move(action)
        gui.update_board(curr_state.game_board)
        gui.root.after(500, lambda: execute_actions_with_delay(gui, curr_state,
                                                               actions,
                                                               index + 1))
    else:
        gui.display_win_message()  # Display "You Win" message when done


def solve_with_search(algorithm_name, problem, dots_list):
    """
    Solve the problem using the search algorithm and display the GUI.
    :param algorithm_name: name of the algorithm to use
    :param problem: the problem to solve
    :param dots_list: list of dots representing the board initial state
    """
    # Execute the solvers algorithm
    actions, elapsed_time = start_search(problem, algorithm_name)
    display_gui(problem, algorithm_name, actions, elapsed_time)


def solve_with_rl(algorithm_name, problem, dots_list):
    """
    Solve the problem using the reinforcement learning agent and display the GUI.
    :param algorithm_name: name of the agent to use
    :param problem: the problem to solve
    :param dots_list: list of dots representing the board initial state
    """
    environment = FlowFreeEnvironment(problem)
    # Execute the solvers algorithm
    agent = choose_rl_agent(algorithm_name)
    # Train the agent
    agent.train(episodes=10000, environment=environment)
    # Solve a specific level
    initial_state = environment.reset()
    start_time = time.time()
    actions = agent.solve(initial_state, environment)
    elapsed_time = time.time() - start_time
    display_gui(problem, algorithm_name, actions, elapsed_time)


def convert_dots_to_sat_problem(dots):
    """
    Convert the dots list to a SAT problem format.
    :param dots: list of Dot objects representing the board initial state
    :return: list of colors and a dictionary representing the board
    """
    dot_dict = {}
    colors = set()
    for dot in dots:
        colors.add(dot.get_color())
        pos = (dot.get_x(), dot.get_y())
        dot_dict[pos] = dot.get_color()
    return list(colors), dot_dict


def solve_with_sat(algorithm_name, problem, dots_list):
    """
    Solve the problem using the SAT solver and display the GUI.
    :param algorithm_name: name of the algorithm to use
    :param problem: the problem to solve
    :param dots_list: list of dots representing the board initial state
    :return:
    """
    board_size, dots_array = problem.get_problem_vars()
    colors, initial_board = convert_dots_to_sat_problem(dots_array)
    sat_solver = FlowFreeSAT(board_size, colors, initial_board)

    start_time = time.time()
    solution = sat_solver.solve(dots_list)
    elapsed_time = time.time() - start_time

    if solution == SAT_NO_SOLUTION:
        print(NO_SOLUTION_MESSAGE)
    else:
        print(SOLUTION_FOUND_MESSAGE)
        root = tk.Tk()
        flow_free_gui = FlowFreeGUI(root, board_size, board_size)
        flow_free_gui.display_solved_board(sat_solver.convert_sol_to_board(
            solution), algorithm_name, elapsed_time)
        # Start the Tkinter event loop
        root.mainloop()


def display_initial_board(problem):
    """
    A function to display the initial board state.
    :param problem: the problem to display
    """
    root = tk.Tk()
    board_size = problem.board.board_size
    gui = FlowFreeGUI(root, board_size, board_size)

    # Display the starting dots
    dots_list = problem.board.dots_list
    gui.display_starting_dots(dots_list)

    root.mainloop()


def display_gui(problem, algorithm_name, actions, elapsed_time):
    """
    Display the GUI with the given problem and actions.
    :param problem: the problem to display
    :param algorithm_name: name of the algorithm used to solve the problem
    :param actions: list of actions to execute
    :param elapsed_time: time taken to solve the problem
    """
    # Create Tkinter root and GUI only after the solvers algorithm is done
    root = tk.Tk()
    board_size = problem.board.board_size
    gui = FlowFreeGUI(root, board_size, board_size)

    # Set the solvers time, expanded nodes, and algorithm name in the GUI
    gui.set_search_time(elapsed_time)
    gui.set_expanded_nodes(problem.expanded)
    gui.set_algorithm_name(algorithm_name)

    if actions:
        # Display the initial state and start executing actions with a delay
        curr_state = problem.get_start_state()
        gui.update_board(curr_state.game_board)
        root.after(500, execute_actions_with_delay, gui, curr_state, actions)
    else:
        gui.display_lost_message()  # Display "You Lost" message if no actions

    root.mainloop()


# dictionary of solvers
solvers = {"A*": solve_with_search, "DFS": solve_with_search,
           "BFS": solve_with_search, "UCS": solve_with_search,
           "SAT": solve_with_sat, "Q learning": solve_with_rl,
           "AQ learning": solve_with_rl}


def solve_game(algorithm, grid_size, dots_list):
    """
    Solve the game using the given algorithm.
    :param algorithm: the algorithm to use
    :param grid_size: the size of the grid
    :param dots_list: list of dots representing the board initial state
    """
    problem = FlowFreeProblem(grid_size, dots_list)
    # display_initial_board(problem)
    solvers.get(algorithm)(algorithm, problem, dots_list)


def main():
    """
    Main function to solve a level with a specific algorithm.
    """
    algorithm = "SAT"
    grid_size = 5
    level = 5
    dots_list = create_level(grid_size, level)
    solve_game(algorithm, grid_size, dots_list)


if __name__ == "__main__":
    main()
