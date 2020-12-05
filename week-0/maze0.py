import sys
import abc

class BaseFrontier(abc.ABC):
    """
        Dynamic list to store explored nodes and nodes to explore.
    """
    def __init__(self):
        self.nodes = list()
        self.explored_nodes = list()
    
    def add(self, node):
        """ Adds new node to the list of nodes to explore.

        Args:
            node ([Node]): node object to explore.
        """
        if node not in self.nodes and node not in self.explored_nodes:
            self.nodes.append(node)
        return

    def is_empty(self):
        """ Checks if the frontier has remaining nodes to explore or not.

        Returns:
            [Bool]
        """
        return len(self.nodes) == 0
    
    @abc.abstractclassmethod
    def remove(self):
        """
            Removes a node from the list in order to explore it. 
            This method is meant to be overriden by inheriting classes base on its data structure.
        """
        pass

class StackFrontier(BaseFrontier):
    """ Frontier based on Stack data structre.

    Args:
        BaseFrontier ([BaseFrontier])
    """
    def remove(self):
        """Removes last added node from frontier.

        Returns:
            [Node]: node to explore.
        """
        node = self.nodes[-1]
        self.nodes = self.nodes[:-1]
        self.explored_nodes.append(node)
        return node

class QueueFrontier(BaseFrontier):
    """ Frontier based on Queue data structre.

    Args:
        BaseFrontier ([BaseFrontier])
    """
    def remove(self):
        """Removes first added node from frontier.

        Returns:
            [Node]: node to explore.
        """
        node = self.nodes[0]
        self.nodes = self.nodes[1:]
        self.explored_nodes.append(node)
        return node

class Node:
    """
        Class for storing each cell data.
    """
    def __init__(self, state, x, y, action=None, parent=None):
        self.state = state
        self.parent = parent
        self.x = x
        self.y = y
        self.action = action

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class Maze:
    """
        Class for creating a maze, solving it and exporting the solution as either an image or a txt file.
    """
    START = 'A'
    TARGET = 'B'

    def __init__(self, filename):
        """ Creating new maze.

        Args:
            filename ([str]): File name of the maze.
        """
        self.filename = filename
        self.maze_arr = self._parse_maze_file()
        self.start_point, self.end_point = self._get_start_end_points()
        self._validate_maze_points()
        self.rows_count = len(self.maze_arr)
        self.cells_count = len(self.maze_arr[0])
        self.steps = 0

    def solve(self, frontier):
        """Solve maze to find the way from start to target point

        Args:
            frontier (BaseFrontier): Contains explored nodes and nodes to explore.

        Returns:
            Bool: Success status of solving maze. True if a path was found. False otherwise.
        """
        x, y = self.start_point[0], self.start_point[1]
        node = Node(self.maze_arr[x][y], x, y)
        frontier.add(node)
        while(not frontier.is_empty()):
            self.steps += 1
            node = frontier.remove()
            self.maze_arr[node.x][node.y] = '/' if self.maze_arr[node.x][node.y] == ' ' else self.maze_arr[node.x][node.y]
            if node.state == self.TARGET:
                self._apply_solution(node)
                return True
            new_nodes = self._get_neighbors(node)
            for new_node in new_nodes:
                frontier.add(new_node)
        return False

    def draw_image(self, filename):
        """ Draws maze as an image.

        Args:
            filename (str): Name of the generated image file.
        """
        from PIL import Image, ImageDraw
        CELL_WIDTH = 70
        COLORS = {
            '#': (40, 40, 40),
            self.START: (0, 0, 200),
            self.TARGET: (0, 171, 28),
            '*': (220, 235, 113),
            '/': (212, 97, 85),
            ' ': (237, 240, 252),
            }
        height = CELL_WIDTH * len(self.maze_arr)
        width = CELL_WIDTH * len(self.maze_arr[0])
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        for i, row in enumerate(self.maze_arr):
            for j, col in enumerate(row):
                color = COLORS.get(col)
                shape = [(j * CELL_WIDTH, i * CELL_WIDTH), ((j * CELL_WIDTH) + CELL_WIDTH , (i * CELL_WIDTH) + CELL_WIDTH)]
                draw.rectangle(shape, fill=color, outline='black')
        img.save(filename)

    def write_solved_maze_file(self):
        """ Generates text file for the solution of the maze.
        """
        filename = self.filename.split('.')
        filename = filename[0] + '_solved.' + filename[1]
        with open(filename, 'w') as file:
            for row in self.maze_arr:
                row.append('\n')
                file.writelines(''.join(row))
        return

    def _parse_maze_file(self):
        """ Converts Maze file to a two dimensional list.

        Returns:
            [List]: Maze data as list.
        """
        maze_arr = list()
        with open(self.filename, "r") as file:
            for line in file:
                maze_arr.append(list(line.rstrip('\n')))
        return maze_arr

    def _get_start_end_points(self):
        """ Looks for Start point and target point indecies.

        Returns:
            Tuple, Tuple : Two Tuples of x and y coordinates of start and target points.
        """
        starting_point = tuple()
        ending_point = tuple()
        for i, row in enumerate(self.maze_arr):
            for j, cell in enumerate(row):
                if cell == self.START:
                    starting_point = (i, j)
                elif cell == self.TARGET:
                    ending_point = (i, j)
        return starting_point, ending_point

    def _validate_maze_points(self):
        """ Validates inserted maze file.

        Raises:
            Exception: If maze file is either: 
                            - Empyt.
                            - Doesn't have consistent row width.
                            - Doesn't include start and target point.

        """
        if len(self.maze_arr) < 1:
            raise Exception("Maze is empty")
        if any(len(row) != len(self.maze_arr[0]) for row in self.maze_arr):
            raise Exception("Maze rows must have the same number of cells")
        if len(self.end_point) != 2 or len(self.start_point) != 2:
            raise Exception("Maze doesn't contain start and end points")
        return
    
    def _apply_solution(self, node):
        """ Inserts * on the descovered path.

        Args:
            node ([Node]): Node of the found target to traceback the followed path.
        """
        node = node.parent
        while node.state != self.START:
            self.maze_arr[node.x][node.y] = '*'
            node = node.parent
        
    def _get_state(self, x, y):
        """ Returns the state of a given coordindates.

        Args:
            x ([int]): Cell X coordinate
            y ([int]): Cell Y coordinate

        Returns:
            [type]: [description]
        """
        return self.maze_arr[x][y]
    
    def _get_neighbors(self, node):
        """ Creates nodes for potential paths to explore.

        Args:
            node ([Node]): node object to check its surrounding paths.

        Returns:
            [List]: List of all available surrounding nodes.
        """
        movements = ['UP', 'LEFT', 'DOWN', 'RIGHT']
        availabe_nodes = list()
        for movement in movements:
            coords = self._next_cell(node.x, node.y, movement)
            if coords:
                x, y = coords
                new_node = Node(self._get_state(x, y), x, y, movement, node)
                availabe_nodes.append(new_node)
        return availabe_nodes

    def _next_cell(self, x, y, movement):
        """ Validates nearby cells.

        Args:
            x ([int]): Node X coordinate
            y ([int]): Node Y coordinate
            movement ([str]): path direction.

        Returns:
            [Tuple]: Tuple of X, Y coordinates of the available cell if it's not a wall. None otherwise.
        """
        if movement == 'UP':
            x = x - 1
            if x < 0 or self.maze_arr[x][y] =='#':
                return None

        elif movement == 'DOWN':
            x = x + 1
            if x >= self.rows_count or self.maze_arr[x][y] =='#':
                return None

        elif movement == 'LEFT':
            y = y - 1
            if y < 0 or self.maze_arr[x][y] =='#':
                return None

        elif movement == 'RIGHT':
            y = y + 1
            if y >= self.cells_count or self.maze_arr[x][y] =='#':
                return None

        return (x, y)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Invalid Command Line arguments. Maze file location required.")
        sys.exit(1)

    filename = sys.argv[1]
    maze = Maze(filename)
    # frontier = StackFrontier()
    frontier = QueueFrontier()
    maze.solve(frontier)
    print(maze.steps)
    maze.draw_image(filename.split('.')[0] + '.png')
