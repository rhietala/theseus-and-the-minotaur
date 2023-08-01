#!/usr/bin/env python3

from typing import List, Tuple, NamedTuple, Dict, Set
from getch import getch  # type: ignore
from enum import Enum
import sys
import random


class MazeTile(Enum):
    EMPTY = " "
    WALL = "#"
    WALKABLE = "."
    FINISH = "X"


PLAYER = "*"
MINOTAUR = "M"

Maze = List[List[MazeTile]]

Coord = Tuple[int, int]
Player = Coord
Minotaur = Coord


class Move(Enum):
    UP = "n"
    DOWN = "s"
    LEFT = "w"
    RIGHT = "e"
    SKIP = "d"
    QUIT = "q"
    UNDO = "u"
    AUTO = "a"


UncheckedMoves = Set[Move]


class Turn(NamedTuple):
    player: Player
    minotaur: Minotaur
    moves: List[Move]


class State(NamedTuple):
    maze: Maze
    finish: Coord
    initial: List[Move]
    turns: List[Turn]
    traversed: Dict[Tuple[Player, Minotaur], UncheckedMoves]
    solver: bool


def loadMaze(filename: str) -> State:
    """
    Loads a maze from a file.

    Replace player and minotaur with WALKABLE tiles.
    """
    maze: Maze = []
    player: Player = (0, 0)
    minotaur: Minotaur = (0, 0)
    finish: Coord = (0, 0)

    with open(filename) as f:
        for (y, line) in enumerate(f):
            maze.append([])
            for (x, char) in enumerate(line.strip()):
                if char == PLAYER:
                    player = (x, y)
                    tile = MazeTile.WALKABLE
                elif char == MINOTAUR:
                    minotaur = (x, y)
                    tile = MazeTile.WALKABLE
                elif char == MazeTile.FINISH.value:
                    finish = (x, y)
                    tile = MazeTile.EMPTY
                else:
                    # this will raise an error if the character is not valid
                    tile = MazeTile(char)

                maze[y].append(tile)

    moves: UncheckedMoves = validMoves(maze, player)
    subState = Turn(player, minotaur, [])
    traversed = {(player, minotaur): moves}

    return State(maze, finish, [], [subState], traversed, False)


def colorizeTile(tile: MazeTile) -> str:
    """
    Colorizes a tile for printing
    """
    if tile == MazeTile.WALKABLE:
        return f"\033[30;1m{tile.value}\033[0m"
    else:
        return tile.value


def printMaze(state: State) -> None:
    """
    Prints the maze with the player and minotaur
    """
    printedMaze = [[colorizeTile(x) for x in xs] for xs in state.maze]
    subState = state.turns[-1]
    player = subState.player
    minotaur = subState.minotaur
    printedMaze[player[1]][player[0]] = f"\033[97;1m{PLAYER}\033[0m"
    printedMaze[minotaur[1]][minotaur[0]] = f"\033[31;1m{MINOTAUR}\033[0m"

    for row in printedMaze:
        print("".join(row))

    print("Moves: " + ";".join(x.value for x in subState.moves))

    if subState.player == subState.minotaur:
        print("You lost!")
    elif subState.player == state.finish:
        print("You won!")
        sys.exit(0)


def isLocValid(maze: Maze, loc: Coord) -> bool:
    """
    Checks if a location is valid in the maze
    """
    x, y = loc
    if y < 0 or y >= len(maze) or x < 0 or x >= len(maze[y]):
        return False
    if maze[y][x] == MazeTile.WALL:
        return False

    return True


def validMoves(maze: Maze, coord: Coord) -> Set[Move]:
    """
    Returns the list of valid moves for a given coordinate
    """
    x, y = coord
    validMoves: Set[Move] = set([Move.SKIP])

    if isLocValid(maze, (x, y - 1)):
        validMoves.add(Move.UP)
    if isLocValid(maze, (x, y + 1)):
        validMoves.add(Move.DOWN)
    if isLocValid(maze, (x - 1, y)):
        validMoves.add(Move.LEFT)
    if isLocValid(maze, (x + 1, y)):
        validMoves.add(Move.RIGHT)

    return validMoves


def movePlayer(maze: Maze, player: Coord, move: Move) -> Tuple[Coord, bool]:
    """
    Player or minotaur moves in the maze

    Returns the new location and whether the move was valid.
    """
    x, y = player
    if move == Move.UP:
        newPlayer = (x, y - 2)
        validCheckLoc = (x, y - 1)
    elif move == Move.DOWN:
        newPlayer = (x, y + 2)
        validCheckLoc = (x, y + 1)
    elif move == Move.LEFT:
        newPlayer = (x - 2, y)
        validCheckLoc = (x - 1, y)
    elif move == Move.RIGHT:
        newPlayer = (x + 2, y)
        validCheckLoc = (x + 1, y)
    elif move == Move.SKIP:
        return (player, True)
    else:
        return (player, False)

    if isLocValid(maze, validCheckLoc):
        return (newPlayer, True)
    else:
        return (player, False)


def moveMinotaur(maze: Maze, player: Coord, minotaur: Coord) -> Coord:
    """
    Minotaur moves towards player

    It must move horizontally first and then vertically.
    """
    move = Move.SKIP

    # try to move horizontally

    if player[0] < minotaur[0]:
        move = Move.LEFT
    elif player[0] > minotaur[0]:
        move = Move.RIGHT

    (newMinotaur, _) = movePlayer(maze, minotaur, move)
    if newMinotaur != minotaur:
        return newMinotaur

    # try to move vertically

    if player[1] < minotaur[1]:
        move = Move.UP
    elif player[1] > minotaur[1]:
        move = Move.DOWN

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
    subState = state.turns[-1]

    if len(state.initial) > 0:
        move = state.initial.pop(0)
    elif state.solver:
        move = Move.AUTO
    else:
        try:
            move = Move(getch())
        except ValueError:  # invalid move
            return state

    if move == Move.QUIT:
        print("You quit!")
        sys.exit(1)

    if move == Move.AUTO:
        uncheckedMoves = state.traversed[(subState.player, subState.minotaur)]
        # pick a move at random from unchecked moves or undo
        if len(uncheckedMoves) == 0:
            move = Move.UNDO
        else:
            move = random.choice(list(uncheckedMoves))

    if move == Move.UNDO:
        if len(state.turns) > 1:
            state.turns.pop()
        return state

    if subState.player == subState.minotaur or subState.player == state.finish:
        # if the game is lost or won, allow only undo and quit
        return state

    # remove this move from the list of unchecked moves
    if move in state.traversed[(subState.player, subState.minotaur)]:
        state.traversed[(subState.player, subState.minotaur)].remove(move)

    (player, valid) = movePlayer(state.maze, subState.player, move)
    if not valid:
        return state

    # minotaur moves twice
    minotaur = moveMinotaur(state.maze, player, state.turns[-1].minotaur)
    minotaur = moveMinotaur(state.maze, player, minotaur)
    moves = subState.moves + [move]

    uncheckedMoves = validMoves(state.maze, player)
    # if there already is a substate with the same player and minotaur locations,
    # use that subState's uncheckedMoves
    if (player, minotaur) in state.traversed:
        uncheckedMoves = state.traversed[(player, minotaur)]
    # if game is lost, uncheckedMoves is empty
    if player == minotaur or player == state.finish:
        uncheckedMoves = set()

    state.traversed[(player, minotaur)] = uncheckedMoves

    state.turns.append(Turn(player=player, minotaur=minotaur, moves=moves))

    return state


def main() -> None:
    argv = sys.argv[1:]
    solver = False
    if len(argv) > 0 and argv[0] == "--solver":
        solver = True
        argv.pop(0)

    if len(argv) == 0 or len(argv) > 2:
        print(
            "Usage: python3 theseus-and-the-minotaur.py [--solver] "
            + "<maze filename> <optional starting position>"
        )
        sys.exit(1)

    filename = argv.pop(0)
    state = loadMaze(filename)
    state = state._replace(solver=solver)

    initial: List[Move] = []
    if len(argv) > 0:
        initial = [Move(x) for x in argv.pop().split(";")]
        state = state._replace(initial=initial)

    while True:
        state = mainLoop(state)


main()
