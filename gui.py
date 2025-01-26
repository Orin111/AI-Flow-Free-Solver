import tkinter as tk


class FlowFreeGUI:
    """
    Class to represent the GUI of the Flow Free game.
    """

    def __init__(self, root, board_width, board_height):
        """
        Constructor for the FlowFreeGUI class.
        :param root: root Tkinter object
        :param board_width: width of the board
        :param board_height: height of the board
        """
        self.root = root

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Adjust cell size to fit within the screen, with some padding
        max_cell_size_width = screen_width // (board_width + 2)
        max_cell_size_height = screen_height // (
                    board_height + 4)  # Adding extra rows for labels
        self.cell_size = min(max_cell_size_width, max_cell_size_height)

        # Calculate the overall board size
        self.board_width = board_width
        self.board_height = board_height
        self.cells = [[None for _ in range(board_width)] for _ in
                      range(board_height)]
        self.expanded_nodes = 0
        self.search_time = 0.0  # To store the solver's algorithm time
        self.algorithm_name = ""  # To store the algorithm name

        self.setup_gui()
        self.center_window()

    def setup_gui(self):
        """
        Setup the GUI for the Flow Free game.
        """
        self.root.title("Flow Free")

        # Create a frame for the "You Win/Lost" message
        self.win_frame = tk.Frame(self.root)
        self.win_frame.grid(row=0, column=0, columnspan=self.board_width)

        self.win_label = tk.Label(self.win_frame, text="",
                                  font=("Helvetica", 20), fg="green")
        self.win_label.pack()

        # Create a frame for the labels
        label_frame = tk.Frame(self.root)
        label_frame.grid(row=1, column=0, columnspan=self.board_width)

        self.expanded_nodes_label = tk.Label(label_frame,
                                             text=f"expanded nodes: {self.expanded_nodes}",
                                             font=("Helvetica", 16),
                                             fg="orange")
        self.expanded_nodes_label.pack(side=tk.LEFT, padx=20)

        self.search_time_label = tk.Label(label_frame,
                                          text=f"time: {self.search_time:.2f} s",
                                          font=("Helvetica", 16), fg="orange")
        self.search_time_label.pack(side=tk.LEFT, padx=20)

        self.algorithm_name_label = tk.Label(label_frame,
                                             text=f"algorithm: {self.algorithm_name}",
                                             font=("Helvetica", 16),
                                             fg="white")
        self.algorithm_name_label.pack(side=tk.LEFT, padx=20)

        for i in range(self.board_height):
            for j in range(self.board_width):
                canvas = tk.Canvas(master=self.root, width=self.cell_size,
                                   height=self.cell_size, bg='black',
                                   highlightthickness=0.5,
                                   highlightbackground='#808080')
                canvas.grid(row=i + 2,
                            column=j)  # Adjusted row to make space for labels
                self.cells[i][j] = canvas

    def update_board(self, game_board):
        """
        Update the board with the given game board.
        :param game_board: 2D list representing the game board with color names
        """
        for i in range(self.board_height):
            for j in range(self.board_width):
                color = game_board[i][j]
                self.cells[i][j].delete("all")
                if color != 'black':
                    self.cells[i][j].create_oval(self.cell_size // 5,
                                                 self.cell_size // 5,
                                                 self.cell_size * 4 // 5,
                                                 self.cell_size * 4 // 5,
                                                 fill=color, outline="")
        self.connect_adjacent_cells(game_board)
        self.update_labels()

    def connect_adjacent_cells(self, game_board):
        """
        Connect the adjacent cells of the same color.
        :param game_board: the game board with color names
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for i in range(self.board_height):
            for j in range(self.board_width):
                color = game_board[i][j]
                if color != 'black':
                    for di, dj in directions:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.board_height and 0 <= nj < self.board_width:
                            if game_board[ni][nj] == color:
                                self.cells[i][j].lift("all")
                                self.cells[i][j].create_line(
                                    self.cell_size // 2, self.cell_size // 2,
                                    self.cell_size // 2 + self.cell_size * dj,
                                    self.cell_size // 2 + self.cell_size * di,
                                    fill=color, width=20)

    def update_labels(self):
        """
        Update the labels with the expanded nodes, search time, and algorithm name.
        """
        self.expanded_nodes_label.config(
            text=f"expanded nodes: {self.expanded_nodes}")
        self.search_time_label.config(text=f"time: {self.search_time:.4f} s")
        self.algorithm_name_label.config(
            text=f"algorithm: {self.algorithm_name}")

    def set_expanded_nodes(self, expanded_nodes):
        """
        Set the number of expanded nodes and update the labels.
        :param expanded_nodes: number of expanded nodes
        """
        self.expanded_nodes = expanded_nodes
        self.update_labels()

    def set_search_time(self, search_time):
        """
        Set the search time and update the labels.
        :param search_time: time taken by the algorithm to solve the board
        """
        self.search_time = search_time
        self.update_labels()

    def set_algorithm_name(self, algorithm_name):
        """
        Set the algorithm name and update the labels.
        :param algorithm_name: name of the algorithm used to solve the board
        """
        self.algorithm_name = algorithm_name
        self.update_labels()

    def display_win_message(self):
        """
        Display the "You Win!" message.
        """
        self.win_label.config(text="You Win!", fg="green")

    def display_lost_message(self):
        """
        Display the "You Lost!" message.
        """
        self.win_label.config(text="You Lost!", fg="red")

    def center_window(self):
        """
        Center the window on the screen.
        """
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)
        self.root.geometry(
            f'{window_width}x{window_height}+{position_right}+{position_down}')

    def display_starting_dots(self, dots_list):
        """
        Display the starting dots on the board.
        :param dots_list: list of Dot objects representing the starting dots
        """
        # Clear the board
        for i in range(self.board_height):
            for j in range(self.board_width):
                self.cells[i][j].delete("all")
                self.cells[i][j].create_rectangle(0, 0, self.cell_size,
                                                  self.cell_size, fill="black")

        # Draw the dots on the board
        for dot in dots_list:
            i = dot.get_x()
            j = dot.get_y()
            color = dot.get_color()
            self.cells[i][j].create_oval(self.cell_size // 5,
                                         self.cell_size // 5,
                                         self.cell_size * 4 // 5,
                                         self.cell_size * 4 // 5, fill=color,
                                         outline="")

    def display_solved_board(self, solved_board, algorithm_name=None,
                             search_time=None):
        """
        Displays the solved board and connects the cells of the same color.
        Updates the algorithm name and search time if provided.
        :param solved_board: 2D list representing the solved board with color names
        :param algorithm_name: (optional) The name of the algorithm used to solve the board
        :param search_time: (optional) The time taken by the algorithm to solve the board
        """
        # Update the algorithm name and search time if provided
        if algorithm_name is not None:
            self.algorithm_name = algorithm_name
        if search_time is not None:
            self.search_time = search_time
        self.update_board(solved_board)
