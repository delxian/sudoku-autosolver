"""Backtracking implementation of a Sudoku solver."""
# pylint: disable=redefined-outer-name,invalid-name
from __future__ import annotations
from collections import defaultdict
from itertools import combinations
import random


class Board:
    """Implementation of a Sudoku board."""
    def __init__(self):
        self.cells: list[int | None] = [None]*81

    def __iter__(self):
        return iter(self.cells)

    def __str__(self) -> str:
        output = []
        for i in range(9):
            row = [str(item) if item is not None else '-' for item in self.get_row(i)]
            output.append(' '.join(row))
        return '\n\n'.join(output)

    def get_cell(self, column: int, row: int) -> int | None:
        """Get the value of a cell."""
        return self.cells[self.xy_to_i(column, row)]

    def set_cell(self, column: int, row: int, value: int | None):
        """Set the value of a cell."""
        self.cells[self.xy_to_i(column, row)] = value

    def get_row(self, row: int) -> list[int | None]:
        """Get all values in a row in the board."""
        return self.cells[row*9 : row*9+9]

    def get_column(self, column: int) -> list[int | None]:
        """Get all values in a column in the board."""
        return [self.get_cell(column, row) for row in range(9)]

    def get_box(self, column: int, row: int) -> list[int | None]:
        """Get all values in a box in the board via a cell's location."""
        values = []
        box_row, box_column = row // 3, column // 3
        for row_index in range((box_row)*3, (box_row)*3 + 3):
            for column_index in range((box_column)*3, (box_column)*3 + 3):
                values.append(self.get_cell(column_index, row_index))
        return values

    def is_valid_group(self, group: list[int | None]) -> bool:
        """Determine whether any group (row, column, box) has a valid configuration."""
        if len(group) != 9:
            return False
        if all(isinstance(item, int) for item in group):
            return set(group) == set(range(1, 10))
        numbers = [item for item in group if isinstance(item, int)]
        return len(set(numbers)) == len(numbers)

    def get_valid_options(self, column: int, row: int) -> set[int]:
        """Get all valid options for a given cell."""
        valid = set(range(1, 10))
        row_values = self.get_row(row)
        column_values = self.get_column(column)
        box_values = self.get_box(column, row)
        for group in (row_values, column_values, box_values):
            valid -= set(item for item in group if item is not None)
        return valid

    @property
    def is_valid(self) -> bool:
        """Whether or not the board is in a valid configuration."""
        for i in range(9):
            if not self.is_valid_group(self.get_row(i)):
                return False
            for j in range(9):
                if not self.is_valid_group(self.get_column(i)):
                    return False
                if not self.is_valid_group(self.get_box(j, i)):
                    return False
        return True

    @property
    def is_solved(self) -> bool:
        """Whether or not the board is solved."""
        if not all(item in set(range(1, 10)) for item in self.cells):
            return False
        return self.is_valid

    @staticmethod
    def i_to_xy(index: int) -> tuple[int, int]:
        """Convert cell index to location."""
        y, x = divmod(index, 9)
        return (x, y)

    @staticmethod
    def xy_to_i(column: int, row: int) -> int:
        """Convert cell location to index."""
        return row*9 + column

    @staticmethod
    def share_groups(first: tuple[int, int], second: tuple[int, int]) -> bool:
        """Check whether two cells share any groups."""
        if first[0] == second[0]:
            return True
        if first[1] == second[1]:
            return True
        if ((first[0] // 3 == second[0] // 3)
            and (first[1] // 3 == second[1] // 3)):
            return True
        return False


class HistoryMove:
    """Data for a move in a Sudoku game."""
    root: HistoryMove | None = None

    def __init__(self, location: tuple[int, int], value: int):
        self.location = location
        self.value = value
        self.last: HistoryMove | None = None
        self.next: HistoryMove | None = None
        self.banned_moves: dict[tuple[int, int], set[int]] = defaultdict(set)

    @classmethod
    def history(cls) -> list[str]:
        """Get a stripped-down list of all moves executed in order."""
        if cls.root is None:
            return []
        entries = []
        current: HistoryMove = cls.root
        while True:
            entries.append(f"{current.value} at {current.location}")
            if current.next is None:
                break
            current = current.next
        return entries

    def legal_next(self, location: tuple[int, int], value: int) -> bool:
        """Determine whether or not a move is legal (not banned)."""
        if location not in self.banned_moves:
            return True
        return value not in self.banned_moves[location]


class Solver:
    """Class for execution of automatic sudoku solving."""

    def __init__(self, board_string: str, solution_string: str = ''):
        self.board = Board()
        if len(board_string) != 81:
            raise InvalidBoardStringError("Starting board must have 81 characters")
        if not board_string.isnumeric():
            raise InvalidBoardStringError("All board values must be numeric (0 for empty cells)")
        self.board.cells = [int(value) if value != '0' else None for value in board_string]
        if not self.board.is_valid:
            raise InvalidBoardStringError("Starting board is an invalid configuration")
        self.solution = solution_string
        self.current_move: HistoryMove = HistoryMove((-1, -1), -1)
        HistoryMove.root = self.current_move
        self.loops = 0
        self.total_edits = 0

    def add_move(self, location: tuple[int, int], value: int):
        """Handle adding a new move to the game's history."""
        next_move = HistoryMove(location, value)
        next_move.last = self.current_move
        next_move.banned_moves[location].add(value)

        self.current_move.next = next_move
        self.current_move = self.current_move.next

    def backtrack(self):
        """Undo a move in the game's history, if possible."""
        if not self.current_move.last:
            assert self.current_move.value == -1
            # at root: pick a new first move
            location, values = self.pick_cell()
            value = random.choice(list(values))
            self.set_cell(*location, value, track=True)
            return
        # any move after root: backtrack to last move
        self.set_cell(*self.current_move.location, None)
        last_move = self.current_move.last
        last_move.banned_moves[self.current_move.location].add(self.current_move.value)
        last_move.next = None
        self.current_move = last_move

    def set_cell(self, column: int, row: int, value: int | None, track: bool = False):
        """Set the value of a cell, optionally tracking it as a move."""
        self.board.set_cell(column, row, value)
        self.total_edits += 1
        if track and value is not None:
            self.add_move((column, row), value)

    def get_all_options(self) -> dict[int, set[int]]:
        """Get all legal options across the entire board."""
        all_options = {}
        for i, value in enumerate(self.board):
            if value is None:
                valid_options = self.board.get_valid_options(*self.board.i_to_xy(i))
                # includes banned moves, so remove them
                banned_moves = set(
                    option for option in valid_options
                    if not self.current_move.legal_next(self.board.i_to_xy(i), option)
                    )
                valid_options -= banned_moves
                # unassigned cells theoretically MUST have options
                if not valid_options:
                    raise NoLocalOptionsError(
                        f"No options for {i} [{self.board.i_to_xy(i)}]")
                all_options[i] = valid_options
        return all_options

    def get_single_options(self) -> dict[int, int]:
        """Get all options across the entire board that can be immediately resolved."""
        try:
            all_options = self.get_all_options()
        except NoLocalOptionsError as exc:
            raise exc
        singles = {}
        for i, options in all_options.items():
            if len(options) == 1:
                singles[i] = options.pop()
        return singles

    def resolve_all_singles(self, track: bool = False):
        """Resolve all singles (cells with one possible option) exhaustively."""
        while True:
            try:
                if not (singles := self.get_single_options()):
                    break
            except NoLocalOptionsError as exc:
                raise exc
            # group singles by value
            groups = defaultdict(set)
            for i, value in singles.items():
                groups[value].add(self.board.i_to_xy(i))
            # check for conflicting singles (same value in same group)
            for value, locations in groups.items():
                for a, b in combinations(locations, r=2):
                    if self.board.share_groups(a, b):
                        raise ConflictingSinglesError(
                            f"Conflicting {value}s at {a} and {b}")
            # assign all singles to their cells
            for i, value in singles.items():
                self.set_cell(*self.board.i_to_xy(i), value, track=track)

    def pick_cell(self, show_options: bool = False) -> tuple[tuple[int, int], set[int]]:
        """Select a cell and a valid value for it. Prioritize those with fewer options."""
        try:
            all_options = list(self.get_all_options().items())
        except NoLocalOptionsError as exc:
            raise NoLocalOptionsError from exc
        if not all_options:
            raise NoGlobalOptionsError("No options")
        if show_options:
            print("Options:")
            for i, values in all_options:
                print(f"    {self.board.i_to_xy(i)} - {values}")
        all_options = sorted(all_options, key=lambda x: len(x[1]))
        fewest_options = len(all_options[0][1])
        options = [(i, values) for i, values in all_options if len(values) == fewest_options]
        i, values = random.choice(options)
        return (self.board.i_to_xy(i), values)

    def solve(self):
        """Solve the sudoku puzzle."""
        self.resolve_all_singles()
        while True:
            self.loops += 1
            try:
                location, values = self.pick_cell()
            except NoLocalOptionsError:
                self.backtrack()
                continue
            except NoGlobalOptionsError:
                if self.board.is_solved:
                    break
                self.backtrack()
                continue
            value = random.choice(list(values))
            self.set_cell(*location, value, track=True)
            if not self.board.is_valid:
                self.backtrack()
                continue
            try:
                self.resolve_all_singles(track=True)
            except (NoLocalOptionsError, ConflictingSinglesError):
                self.backtrack()
                continue
            if not self.board.is_valid:
                self.backtrack()
                continue

    @property
    def matches_solution(self) -> bool:
        """Whether the solved board matches a provided solution."""
        if not self.solution:
            return False
        FINAL_CELLS = ''.join(str(n) for n in self.board.cells)
        return FINAL_CELLS == self.solution


class NoGlobalOptionsError(Exception):
    """No unassigned cells have any legal moves."""

class NoLocalOptionsError(Exception):
    """Unassigned cell has no legal moves."""

class ConflictingSinglesError(Exception):
    """Two or more singles conflict with each other."""

class InvalidBoardStringError(Exception):
    """Values provided for starting board are invalid."""


puzzle = input("Enter puzzle string (81 digits, with 0 for empty cells): ")
solution = input("Enter solution string [optional]: ")
solver = Solver(puzzle, solution)
print("Initial board:")
print(solver.board)
solver.solve()
print("Solved board:")
print(solver.board)
print(f"Loops: {solver.loops}")
print(f"Total edits: {solver.total_edits}")
if solver.solution:
    print(f"Matches solution: {solver.matches_solution}")
