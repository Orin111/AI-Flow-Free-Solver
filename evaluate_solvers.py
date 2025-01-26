from flow_game.flow_free_problem import FlowFreeProblem
from main import run_search_algorithm
from main import convert_dots_to_sat_problem
from solvers.SAT import FlowFreeSAT
from problems.level_creator import create_level
import signal
import pandas as pd
import time

SAT_FAILED = "UNSAT"
LINE_FORMAT_ERROR = "Unexpected line format"
NUMBER_OF_LEVELS_PER_GRID_SIZE = 10
TIMEOUT = 180

sat_results = pd.DataFrame(columns=['grid size','level', 'time'])
search_results = pd.DataFrame(columns=['grid size', 'level', 'time', 'expended nodes', 'algorithm'])

class TimeoutException(Exception):
    """
    Class for a timeout exception.
    """
    pass

def timeout_handler(signum, frame):
    """
    Handle a timeout signal.
    :param signum: signal number
    :param frame: frame
    :return: None
    """
    raise TimeoutException()


# Set up the timeout handler
signal.signal(signal.SIGALRM, timeout_handler)


def run_with_timeout(timeout, function, *args, **kwargs):
    """
    Run a function with a timeout.
    :param timeout: timeout in seconds
    :param function: function to run
    :param args: arguments
    :param kwargs: keyword arguments
    :return: the result of the function or None if it times out
    """
    signal.alarm(timeout)  # Set the timeout in seconds
    try:
        result = function(*args, **kwargs)
    except TimeoutException:
        result = None
    finally:
        signal.alarm(0)  # Disable the alarm
    return result


def load_levels(grid_size):
    """
    Load the levels for the given grid size.
    :param grid_size: size of the grid
    :return: list of levels
    """
    # iterate over the files in problems directory,
    # use process_image to convert the image of the specific grid size to a
    # list of lists where each sublist represents a level
    loaded_levels = []
    for i in range(NUMBER_OF_LEVELS_PER_GRID_SIZE):
        level = create_level(grid_size, i+1)
        loaded_levels.append(level)

    return loaded_levels


def print_results(algorithm, problems_not_passed_lst,
                  num_of_passed_problems, total_levels):
    """
    Print the results of the algorithm.
    :param algorithm: name of the algorithm
    :param problems_not_passed_lst: list of problems not passed
    :param num_of_passed_problems: number of problems passed
    :param total_levels: number of levels that were tested
    :return:
    """
    print(f'{algorithm} passed {num_of_passed_problems}/{total_levels}')
    if problems_not_passed_lst:
        print(f'problems not passed: {problems_not_passed_lst}')
    print('---------------------------------------------------')



def evaluate_sat_solver(levels_list, grid_size):
    """
    Evaluate the SAT solver on the given levels.
    :param levels_list: list of levels
    :param grid_size: size of the grid
    """
    global sat_results
    num_of_passed_problems = 0
    problems_not_passed_lst = []

    for level_num, level in enumerate(levels_list):
        colors, initial_board = convert_dots_to_sat_problem(level)
        sat_solver = FlowFreeSAT(grid_size, colors, initial_board)
        # start timer
        start_time = time.time()
        solution = sat_solver.solve(level)
        elapsed_time = time.time() - start_time
        sat_results.loc[len(sat_results)] = [grid_size, level_num + 1, elapsed_time]
        if solution == SAT_FAILED:
            problems_not_passed_lst.append(level_num + 1)
            continue
        num_of_passed_problems += 1
    print_results("SAT", problems_not_passed_lst, num_of_passed_problems, len(levels_list))


def solve_search_problem(algo, problem_dots, grid_size):
    """
    Solve the search problem using the given algorithm.
    :param algo: algorithm to use
    :param problem_dots: list of dots representing the problem
    :param grid_size: size of the grid
    :return: the goal state of the problem
    """
    problem = FlowFreeProblem(grid_size, problem_dots)
    actions = run_with_timeout(TIMEOUT, run_search_algorithm, algo, problem)
    problem_state = problem.get_start_state()
    if actions is not None:
        for action in actions:
            problem_state = problem_state.do_move(action)
    return problem_state, problem.expanded


def evaluate_search_algorithm(levels_list, grid_size):
    """
    Evaluate the search algorithm on the given levels.
    :param levels_list: list of levels
    :param grid_size: size of the grid
    """
    search_algorithms = ["BFS", "DFS", "UCS", "A*"]
    passed_problems = {algo: 0 for algo in search_algorithms}
    global search_results
    for algo in search_algorithms:
        problems_not_passed_lst = []
        problems_passed_counter = 0
        for level_num, level in enumerate(levels_list):
            start_time = time.time()
            solution, expended = solve_search_problem(algo, level, grid_size)
            elapsed_time = time.time() - start_time
            if solution.is_goal_state():
                problems_passed_counter += 1
            else:
                problems_not_passed_lst.append(level_num + 1)
            search_results.loc[len(search_results)] = [grid_size, level_num + 1, elapsed_time, expended, algo]
        passed_problems[algo] = problems_passed_counter
        print_results(algo, problems_not_passed_lst,
                      problems_passed_counter, len(levels_list))

solvers = {"Search": evaluate_search_algorithm,
           "SAT": evaluate_sat_solver}


def evaluate_all(grid_size, levels_list):
    """
    Evaluate all algorithms on the given levels.
    :param grid_size: size of the grid
    :param levels_list: list of levels
    """
    for solver_type in solvers.keys():
            solvers.get(solver_type)(levels_list, grid_size)

def evaluate_algorithms_for_grid_size(algorithm_name, grid_size, levels_list):
    """
    Evaluate the algorithms for the given grid size.
    :param algorithm_name: type of algorithm to evaluate
    :param grid_size: size of the grid
    :param levels_list: list of levels
    """
    if algorithm_name == "All":
        evaluate_all(grid_size, levels_list)
    else:
        solvers.get(algorithm_name)(levels_list, grid_size)

def save_dataframe(algorithm_name):
    """
    Save the results to a csv file.
    :param algorithm_name: name of the algorithm
    """
    convert_pd_types()
    dataframes = []
    # save the dataframe to a csv file
    if algorithm_name == "SAT" or algorithm_name == "All":
        dataframes.append((sat_results, 'SAT'))
    if algorithm_name == "Search" or algorithm_name == "All":
        dataframes.append((search_results, 'Search'))
    for dataframe, algorithm_name in dataframes:
        dataframe.to_csv(f'results//{algorithm_name}_results.csv', index=False)


def convert_pd_types():
    """
    Convert the types of the dataframes.
    """
    global sat_results, search_results
    sat_results = sat_results.astype(
        {'grid size': 'int64', 'level': 'int64', 'time': 'float64'})
    search_results = search_results.astype({'grid size': 'int64', 'level': 'int64',
                                            'time': 'float32', 'expended nodes': 'int64',
                                            'algorithm': 'string'})


if __name__ == "__main__":
    algorithm_type = "Search"
    min_grid_size = 5
    max_grid_size = 5
    for size in range(min_grid_size, max_grid_size + 1):
        print("Simulating algorithms for grid size:", size)
        levels = load_levels(size)
        evaluate_algorithms_for_grid_size(algorithm_type, size, levels)
        print()
    save_dataframe(algorithm_type)



