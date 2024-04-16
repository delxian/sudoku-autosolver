# Sudoku Autosolver
Backtracking implementation of an automatic Sudoku puzzle solver, implemented from scratch.

## Features
- Automatic resolution of "naked singles"
- Simple optimization to prioritize cells with fewer options
- Optional comparison to solution string

## Algorithm

This automatic Sudoku solver is fairly straightforward, making no use of any esoteric strategy. The standard procedure is as described below:

1. Resolve all "naked singles" - cells that only have one possible value. These will not be recorded as moves since they must be in the solution.
2. Randomly pick a cell from the cells with the fewest legal values.
    - If there are no legal values in any cells, check whether the puzzle is solved. Quit if solved, otherwise undo the last move and ban it at the current move.
3. Pick a value for the current cell at random and execute it, recording it as a move.
4. Attempt to resolve all naked singles at the current move, recording them as moves.
    - If conflicting naked singles are found, i.e. two or more naked singles share any groups, undo the last move and ban it at the current move.
5. Repeat steps 2-4 until the puzzle is solved.

Checks are in place to ensure the puzzle does not get stuck in an invalid state or an infinite loop.

## Performance

The aim of this project was not to create the fastest Sudoku solver, but rather a decent Sudoku solver from scratch with minimal research. That said, the algorithm can solve most puzzles almost instantly and harder puzzles in a few seconds at most.

## Note 

It is possible that a puzzle has multiple solutions, but the algorithm will only return the first solution it finds. Thus, comparison to a provided solution may return False.

## Requirements
- Python 3.11 or higher
## License
- [MIT](LICENSE)