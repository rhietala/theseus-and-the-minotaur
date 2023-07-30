# Theseus and the Minotaur

[Theseus and the minotaur](https://en.wikipedia.org/wiki/Theseus_and_the_Minotaur)
maze game in CLI. The idea is that you must escape a maze while minotaur is
chasing you.

Minotaur moves twice and it must move horizontally first if that is possible.

---

Requirements: python 3 and `getch` library.

```sh
$ pip install getch
```

Characters:

- `*` player
- `M` minotaur
- `#` wall

Controls:

- `n`: north
- `s`: south
- `e`: east
- `w`: west
- `d`: delay, skip your move

Starting the game:

```sh
$ python3 theseus-and-the-minotaur.py maze1.txt


#############################
#. . . . .#. . . .#. . . . .#
##### # # # ### ##### ##### #
#.#.#.#.#.#.#. . . . .#. . .
# # # ### # ### ########### #
#. . . . . . . . . . . . . .#
# # ### # # ### # # ##### # #
#.#.#. .#.#. . .#.#. . . .#.#
# # ### # # # # # ####### # #
#*#.#. .#.#.#.#.#. . . .#.#M#
# # # # # # # # # ##### # # #
#.#.#.#. .#.#. . . . . .#.#.#
# # # # # # # # # ##### # # #
#.#.#.#.#.#.#.#.#. . . .#.#.#
# # # # # # # # # ##### # # #
#.#.#.#.#.#.#.#.#. . . .#.#.#
# # # # # # # # # ##### # # #
#. . . . . . . . . . . . . .#
#############################
```
