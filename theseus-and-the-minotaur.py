#!/usr/bin/env python3

from typing import List, Tuple, NamedTuple
from copy import deepcopy
from getch import getch  # type: ignore
import sys

EMPTY = " "
WALL = "#"
WALKABLE = "."
FINISH = "X"

PLAYER = "*"
MINOTAUR = "M"

MOVE_UP = "n"
MOVE_DOWN = "s"
MOVE_LEFT = "w"
MOVE_RIGHT = "e"
MOVE_SKIP = "d"
MOVE_QUIT = "q"


Maze = List[List[str]]
Coord = Tuple[int, int]


class State(NamedTuple):
    maze: Maze
    player: Coord
    minotaur: Coord
    finish: Coord
    moves: List[str]
    initial: List[str]


def loadMaze(filename: str) -> State:
    """
    Loads a maze from a file
    """
    maze: Maze = []
    player: Coord = (0, 0)
    minotaur: Coord = (0, 0)
    finish: Coord = (0, 0)

    with open(filename) as f:
        for (y, line) in enumerate(f):
            maze.append([])
            for (x, char) in enumerate(line.strip()):
                if char == PLAYER:
                    player = (x, y)
                    char = WALKABLE
                elif char == MINOTAUR:
                    minotaur = (x, y)
                    char = WALKABLE
                elif char == FINISH:
                    finish = (x, y)
                    char = EMPTY

                maze[y].append(char)

    return State(maze, player, minotaur, finish, [], [])


def printMaze(state: State) -> None:
    """
    Prints the maze with the player and minotaur
    """
    maze, player, minotaur, _, moves, _ = state
    printedMaze: Maze = deepcopy(maze)
    printedMaze[player[1]][player[0]] = PLAYER
    printedMaze[minotaur[1]][minotaur[0]] = MINOTAUR

    print("\033c", end="")  # clear screen
    for row in printedMaze:
        print("".join(row))

    print("Moves: " + ";".join(moves))


def isLocValid(maze: Maze, loc: Coord) -> bool:
    """
    Checks if a location is valid in the maze
    """
    x, y = loc
    if y < 0 or y >= len(maze) or x < 0 or x >= len(maze[y]):
        return False
    if maze[y][x] == WALL:
        return False

    return True


def movePlayer(maze: Maze, player: Coord, move: str) -> Tuple[Coord, bool]:
    """
    Player or minotaur moves in the maze

    Returns the new location and whether the move was valid.
    """
    x, y = player
    if move == MOVE_UP:
        newPlayer = (x, y - 2)
        validCheckLoc = (x, y - 1)
    elif move == MOVE_DOWN:
        newPlayer = (x, y + 2)
        validCheckLoc = (x, y + 1)
    elif move == MOVE_LEFT:
        newPlayer = (x - 2, y)
        validCheckLoc = (x - 1, y)
    elif move == MOVE_RIGHT:
        newPlayer = (x + 2, y)
        validCheckLoc = (x + 1, y)
    elif move == MOVE_SKIP:
        return (player, True)
    else:
        return (player, False)

    if isLocValid(maze, validCheckLoc):
        return (newPlayer, True)
    else:
        return (player, False)


def moveMinotaur(state: State) -> Coord:
    """
    Minotaur moves towards player

    It must move horizontally first and then vertically.
    """
    maze, player, minotaur, _, _, _ = state
    move = MOVE_SKIP

    # try to move horizontally

    if player[0] < minotaur[0]:
        move = MOVE_LEFT
    elif player[0] > minotaur[0]:
        move = MOVE_RIGHT

    (newMinotaur, _) = movePlayer(maze, minotaur, move)
    if newMinotaur != minotaur:
        return newMinotaur

    # try to move vertically

    if player[1] < minotaur[1]:
        move = MOVE_UP
    elif player[1] > minotaur[1]:
        move = MOVE_DOWN

    (newMinotaur, _) = movePlayer(maze, minotaur, move)
    return newMinotaur


def mainLoop(state: State) -> State:
    """
    Main game loop

    - print initial maze
    - wait for input
    - check if move is valid
    - move player
    - move minotaur twice
    - check for winning and losing conditions

    Both state and initial are mutated in place.
    """
    printMaze(state)

    if len(state.initial) > 0:
        move = state.initial.pop(0)
    else:
        move = getch()

    if move == MOVE_QUIT:
        print("You quit!")
        sys.exit(1)

    (player, valid) = movePlayer(state.maze, state.player, move)
    if not valid:
        return state

    state = state._replace(player=player)
    state = state._replace(moves=state.moves + [move])

    # minotaur moves twice
    minotaur = moveMinotaur(state)
    state = state._replace(minotaur=minotaur)
    minotaur = moveMinotaur(state)
    state = state._replace(minotaur=minotaur)

    if player == state.minotaur:
        printMaze(state)
        print("You lose!")
        sys.exit(1)

    if player == state.finish:
        printMaze(state)
        print("You win!")
        sys.exit(0)

    return state


def main() -> None:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 theseus-and-the-minotaur.py <maze filename> <optional starting position>")
        sys.exit(1)

    filename = sys.argv[1]
    state = loadMaze(filename)

    initial: List[str] = []
    if len(sys.argv) == 3:
        initial = sys.argv[2].split(";")
        state = state._replace(initial=initial)

    while True:
        state = mainLoop(state)


main()
