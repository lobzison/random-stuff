"""
Loyd's Fifteen puzzle - solver and visualizer
Note that solved configuration has the blank (zero) tile in upper left
Use the arrows key to swap this tile with its neighbors
"""

# import poc_fifteen_gui


class Puzzle:
    """
    Class representation for the Fifteen puzzle
    """

    def __init__(self, puzzle_height, puzzle_width, initial_grid=None):
        """
        Initialize puzzle with default height and width
        Returns a Puzzle object
        """
        self._height = puzzle_height
        self._width = puzzle_width
        self._grid = [[col + puzzle_width * row
                       for col in range(self._width)]
                      for row in range(self._height)]

        if initial_grid is not None:
            for row in range(puzzle_height):
                for col in range(puzzle_width):
                    self._grid[row][col] = initial_grid[row][col]

        self._moves_dict = {"down": {"down": "u", "right": "ullddru",
                                     "left": "dru", "up": "lddru"},
                            "left": {"down": "lur", "right": "ulldr",
                                     "left": "r", "up": "ldr"},
                            "right": {"down": "luurrdl", "right": "l",
                                      "left": "urrdl", "up": "rdl"}}
        self._moves_dict_row0 = {"down": {"down": "u", "right": "dlu",
                                          "left": "dru", "up": "lddru"},
                                 "left": {"down": "lur", "right": "ulldr",
                                          "left": "r", "up": "ldr"},
                                 "right": {"down": "rul", "right": "l",
                                           "left": "drrul", "up": "rdl"}}

    def __str__(self):
        """
        Generate string representaion for puzzle
        Returns a string
        """
        ans = ""
        for row in range(self._height):
            ans += str(self._grid[row])
            ans += "\n"
        return ans

    #####################################
    # GUI methods

    def get_height(self):
        """
        Getter for puzzle height
        Returns an integer
        """
        return self._height

    def get_width(self):
        """
        Getter for puzzle width
        Returns an integer
        """
        return self._width

    def get_number(self, row, col):
        """
        Getter for the number at tile position pos
        Returns an integer
        """
        return self._grid[row][col]

    def set_number(self, row, col, value):
        """
        Setter for the number at tile position pos
        """
        self._grid[row][col] = value

    def clone(self):
        """
        Make a copy of the puzzle to update during solving
        Returns a Puzzle object
        """
        new_puzzle = Puzzle(self._height, self._width, self._grid)
        return new_puzzle

    ########################################################
    # Core puzzle methods

    def current_position(self, solved_row, solved_col):
        """
        Locate the current position of the tile that will be at
        position (solved_row, solved_col) when the puzzle is solved
        Returns a tuple of two integers
        """
        solved_value = (solved_col + self._width * solved_row)

        for row in range(self._height):
            for col in range(self._width):
                if self._grid[row][col] == solved_value:
                    return (row, col)
        assert False, "Value " + str(solved_value) + " not found"

    def update_puzzle(self, move_string):
        """
        Updates the puzzle state based on the provided move string
        """
        zero_row, zero_col = self.current_position(0, 0)
        for direction in move_string:
            if direction == "l":
                assert zero_col > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col - 1]
                self._grid[zero_row][zero_col - 1] = 0
                zero_col -= 1
            elif direction == "r":
                assert zero_col < self._width - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col + 1]
                self._grid[zero_row][zero_col + 1] = 0
                zero_col += 1
            elif direction == "u":
                assert zero_row > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row - 1][zero_col]
                self._grid[zero_row - 1][zero_col] = 0
                zero_row -= 1
            elif direction == "d":
                assert zero_row < self._height - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row + 1][zero_col]
                self._grid[zero_row + 1][zero_col] = 0
                zero_row += 1
            else:
                assert False, "invalid direction: " + direction

    ##################################################################
    # Phase one methods

    def lower_row_invariant(self, target_row, target_col, ignore_zero=False):
        """
        Check whether the puzzle satisfies the specified invariant
        at the given position in the bottom rows of the puzzle (target_row > 1)
        Returns a boolean
        """
        if not ignore_zero:
            zero_in_pos = self.get_number(target_row, target_col) == 0
        else:
            zero_in_pos = True
        lower_rows = True
        righter_cells = True
        if target_row != self.get_height() - 1:
            for rows in range(target_row + 1, self.get_height()):
                for cols in range(self.get_width()):
                    check = self.current_position(rows, cols) == (rows, cols)
                    lower_rows = lower_rows and check
        if target_col != self.get_width() - 1:
            for cols in range(target_col, self.get_width()):
                check = self.current_position(target_row, cols) == (target_row,
                                                                    cols)
                righter_cells = righter_cells and check
        return zero_in_pos and lower_rows

    def solve_interior_tile(self, target_row, target_col):
        """
        Place correct tile at target position
        Updates puzzle and returns a move string
        """
        assert self.lower_row_invariant(target_row, target_col), (
            "lower_row_invariant failed at %d %d" % (target_row, target_col))
        # find where the target tail is, move zero to that position
        target_pos = self.current_position(target_row, target_col)
        res = self.move_to_target_out((target_row, target_col), target_pos)
        current_pos, z_diff = self.update_data(target_row,
                                               target_col)
        while not (current_pos[0] == target_row and
                   current_pos[1] == target_col):
            # move to left first, set correct column, set correct row
            res += self.position_tile(current_pos, z_diff, target_row,
                                      target_col)
            current_pos, z_diff = self.update_data(target_row,
                                                   target_col)

        # move 0 to correct position
        if self.zero_to_target(z_diff) == "up":
            res += "ld"
            self.update_puzzle("ld")
        assert self.lower_row_invariant(target_row, target_col - 1), (
            "lower_row_invariant failed at %d %d" % (target_row,
                                                     target_col - 1))
        return res

    def move_to_target_out(self, zero_coord, target_coord):
        """
        Moves zero tile to target tile.
        Returns stirng with moves
        """
        res = ""
        ups = zero_coord[0] - target_coord[0]
        lefts = zero_coord[1] - target_coord[1]
        if target_coord[1] > zero_coord[1] and ups > 0:
            res += "u"
            ups -= 1
        if lefts > 0:
            res += "l" * lefts
        else:
            res += "r" * -lefts
        res += "u" * ups
        self.update_puzzle(res)
        return res

    def position_tile(self, current_pos, z_diff, target_row,
                      target_col, row0=False):
        """
        Do one step in direction of target
        """
        res = ""
        if row0:
            moves = self._moves_dict_row0
        else:
            moves = self._moves_dict
        if current_pos[1] == 0:
            res += moves["right"][self.zero_to_target(z_diff)]
        elif current_pos[1] != target_col:
            if current_pos[1] > target_col:
                # print "moving to left"
                print z_diff
                res += moves["left"][self.zero_to_target(z_diff)]
            else:
                # print "moving to right"
                res += moves["right"][self.zero_to_target(z_diff)]
        else:
            # print "moving down"
            res += moves["down"][self.zero_to_target(z_diff)]
        print self, res
        self.update_puzzle(res)
        return res

    def zero_to_target(self, z_diff):
        """
        Returns where zero tile is
        with respect to target tile
        """
        res = None
        if z_diff[0] == 0:
            if z_diff[1] == 1:
                res = "right"
            if z_diff[1] == -1:
                res = "left"
        elif z_diff[1] == 0:
            if z_diff[0] == -1:
                res = "up"
            if z_diff[0] == 1:
                res = "down"
        return res

    def update_data(self, target_row, target_col, current=None):
        """
        Updates data about tiles, and returns curren position and difference
        """
        if current is None:
            current_pos = self.current_position(target_row, target_col)
        else:
            current_pos = current
        zero_pos = self.current_position(0, 0)
        z_row_diff = zero_pos[0] - current_pos[0]
        z_col_diff = zero_pos[1] - current_pos[1]
        z_diff = [z_row_diff, z_col_diff]
        return current_pos, z_diff

    def solve_col0_tile(self, target_row):
        """
        Solve tile in column zero on specified row (> 1)
        Updates puzzle and returns a move string
        """
        assert self.lower_row_invariant(target_row, 0), (
            "lower_row_invariant failed at %d %d" % (target_row, 0))
        target_pos = self.current_position(target_row, 0)
        res = self.move_to_target_out((target_row, 0), target_pos)
        print self
        # sould check different way
        if not self.lower_row_invariant(target_row - 1,
                                        self.get_width() - 1, True):
            target_pos = self.current_position(target_row, 0)
            current_pos, z_diff = self.update_data(target_row, 0)
            while not (current_pos[0] == target_row - 1 and
                       current_pos[1] == 1):
                # move to left first, set correct column, set correct row
                res += self.position_tile(current_pos, z_diff,
                                          target_row - 1, 1)
                current_pos, z_diff = self.update_data(target_row, 0)
            if self.zero_to_target(z_diff) == "up":
                res += "ld"
                self.update_puzzle("ld")
            elif self.zero_to_target(z_diff) == "right":
                res += "ulld"
                self.update_puzzle("ulld")
            # res += self.position_tile(target_row - 1, 1)
            res += "ruldrdlurdluurddlur"
            self.update_puzzle("ruldrdlurdluurddlur")
        res += self.move_to_target_out(self.current_position(0, 0),
                                       (target_row - 1, self.get_width() - 1))
        assert self.lower_row_invariant(target_row - 1,
                                        self.get_width() - 1), (
            "lower_row_invariant failed at %d %d" % (target_row, 0))
        print self, res
        return res

    #############################################################
    # Phase two methods

    def row0_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row zero invariant
        at the given column (col > 1)
        Returns a boolean
        """
        zero_in_pos = self.get_number(0, target_col) == 0
        cell_check = self.current_position(1, target_col) == (1, target_col)
        check_rows = self.lower_row_invariant(1, target_col, True)
        return zero_in_pos and cell_check and check_rows

    def row1_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row one invariant
        at the given column (col > 1)
        Returns a boolean
        """
        return self.lower_row_invariant(1, target_col)

    def solve_row0_tile(self, target_col):
        """
        Solve the tile in row zero at the specified column
        Updates puzzle and returns a move string
        """
        assert self.row0_invariant(target_col), (
            "lower_row_invariant failed at %d %d" % (0, target_col))
        target_pos = self.current_position(0, target_col)
        res = self.move_to_target_out((0, target_col), target_pos)
        # sould check different way
        if not (0, target_col) == self.current_position(0, target_col):
            target_pos = self.current_position(0, target_col)
            current_pos, z_diff = self.update_data(0, target_col)
            while not (current_pos[0] == 1 and
                       current_pos[1] == target_col - 1):
                # move to left first, set correct column, set correct row
                print self
                if current_pos[0] == 0:
                    row0 = True
                else:
                    row0 = False
                res += self.position_tile(current_pos, z_diff,
                                          1, target_col - 1, row0)
                current_pos, z_diff = self.update_data(0, target_col)
            if self.zero_to_target(z_diff) == "up":
                res += "ld"
                self.update_puzzle("ld")
            # res += self.position_tile(target_row - 1, 1)
            res += "urdlurrdluldrruld"
            self.update_puzzle("urdlurrdluldrruld")
        else:
            res += 'd'
            self.update_puzzle("d")
        print self
        assert self.row1_invariant(target_col - 1), (
            "lower_row_invariant failed at %d %d" % (1, target_col - 1))
        return res

    def solve_row1_tile(self, target_col):
        """
        Solve the tile in row one at the specified column
        Updates puzzle and returns a move string
        """
        assert self.row1_invariant(target_col), (
            "lower_row_invariant failed at %d %d" % (1, target_col))
        target_pos = self.current_position(1, target_col)
        res = self.move_to_target_out((1, target_col), target_pos)
        current_pos, z_diff = self.update_data(1, target_col)
        if not (1, target_col) == self.current_position(1, target_col):
            target_pos = self.current_position(1, target_col)
            current_pos, z_diff = self.update_data(1, target_col)
            while not (current_pos[0] == 1 and
                       current_pos[1] == target_col):
                # move to left first, set correct column, set correct row
                res += self.position_tile(current_pos, z_diff,
                                          1, target_col)
                current_pos, z_diff = self.update_data(1, target_col)
        if self.zero_to_target(z_diff) != "up":
            if self.zero_to_target(z_diff) == "left":
                res += "ur"
            self.update_puzzle("ur")
        return res

    ###########################################################
    # Phase 3 methods

    def solve_2x2(self):
        """
        Solve the upper left 2x2 part of the puzzle
        Updates the puzzle and returns a move string
        """
        assert self.row1_invariant(1), (
            "row1_invariant failed at %d" % (1))
        res = "lu"
        self.update_puzzle("lu")
        print self, res
        while not ((0, 1) == self.current_position(0, 1) and
                   (1, 0) == self.current_position(1, 0) and
                   (1, 1) == self.current_position(1, 1)):
            res += 'rdlu'
            self.update_puzzle("rdlu")
        return res

    def solve_puzzle(self):
        """
        Generate a solution string for a puzzle
        Updates the puzzle and returns a move string
        """
        # solve all but top 2 rows
        res = ""
        zero_coord = self.current_position(0, 0)
        z_diff0 = (self.get_height() - 1) - zero_coord[0]
        z_diff1 = (self.get_width() - 1) - zero_coord[1]
        if z_diff0 > 0:
            res += "d" * z_diff0
        else:
            res += "u" * -z_diff0
        if z_diff1 > 0:
            res += "r" * z_diff1
        else:
            res += "l" * -z_diff1
        self.update_puzzle(res)
        for row in range(self.get_height() - 1, 1, -1):
            for col in range(self.get_width() - 1, -1, -1):
                if col != 0:
                    res += self.solve_interior_tile(row, col)
                else:
                    res += self.solve_col0_tile(row)
        for col in range(self.get_width() - 1, 1, -1):
            for row in range(1, -1, -1):
                if row != 0:
                    res += self.solve_row1_tile(col)
                else:
                    res += self.solve_row0_tile(col)
        res += self.solve_2x2()
        return res


# Start interactive simulation
# poc_fifteen_gui.FifteenGUI(Puzzle(4, 4))
