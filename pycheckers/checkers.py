"""
checkers.py
Logan Cary

A single or two player checkers game, or a simulation of a checkers game

0: random simulation
1: player vs random AI
2: player vs player

"""
import enum
import random
import time
import typing

from graphics import Circle, GraphWin, Point, Polygon, Rectangle


TILE_SIZE = 80
"""Length of each square game tile in pixels."""
BOARD_SIZE = 8
"""Length of the board in tiles. Must be an even number >=4 or things will break."""
HALF_BOARD_SIZE = BOARD_SIZE // 2
CPU_DELAY = 0.5
"""Number of seconds to wait between double jumps and CPU-player moves."""


class PlayerColor(enum.StrEnum):
    BLACK = "black"
    RED = "red"


class Tile(Rectangle):

    def __init__(self, x: int | float, y: int | float):
        Rectangle.__init__(self, Point(x, y), Point(x + TILE_SIZE, y - TILE_SIZE))
        self.setFill("black")
        self._location = Point(x + TILE_SIZE / 2, y - TILE_SIZE / 2)  # center of tile
        self._isOccupied = False

    def select(self):
        self.setOutline("cyan")

    def deselect(self):
        self.setOutline("black")

    def isOccupied(self) -> bool:
        return self._isOccupied

    def setOccupied(self, tf=True):
        self._isOccupied = tf

    def getLocation(self) -> Point:
        return self._location


class Board:

    def __init__(self, players: typing.Literal[0, 1, 2] = 2, invert: bool = False):
        """
        :param players: 0 for simulated games, 1 for singleplayer, 2 for multiplayer.
        :param invert: Black player on top. If left as `False`, black player is at the bottom of the window.

        """
        self._window = GraphWin("Checkers", TILE_SIZE * BOARD_SIZE, TILE_SIZE * BOARD_SIZE)
        self._window.setBackground("red")
        if invert:
            self._window.setCoords(TILE_SIZE * BOARD_SIZE, 0, 0, TILE_SIZE * BOARD_SIZE)
        self._populate()
        self._drawTiles()

        match players:
            case 2:
                self._blackPlayer = Player(self, PlayerColor.BLACK)
                self._redPlayer = Player(self, PlayerColor.RED)
            case 1:
                self._blackPlayer = Player(self, PlayerColor.BLACK)
                self._redPlayer = CPUPlayer(self, PlayerColor.RED)
                winner = self._begin()
                print(winner.capitalize(), "player won.")
            case 0:
                sims = int(input("How many simulations? "))
                wins = {PlayerColor.BLACK: 0, PlayerColor.RED: 0}
                for _ in range(sims):
                    self._blackPlayer = CPUPlayer(self, PlayerColor.BLACK)
                    self._redPlayer = CPUPlayer(self, PlayerColor.RED)
                    winner = self._begin()
                    wins[winner] += 1
                    self._reset()
                print("Wins:", wins)
            case _:
                raise ValueError("Specify either 0, 1, or 2 players")

    def _populate(self):
        """
        Tile indices are arranged as so:
        |  |  |  |  |  |  |  |  |
        |--|--|--|--|--|--|--|--|
        |  |28|  |29|  |30|  |31|
        |24|  |25|  |26|  |27|  |
        |  |20|  |21|  |22|  |23|
        |16|  |17|  |18|  |19|  |
        |  |12|  |13|  |14|  |15|
        | 8|  | 9|  |10|  |11|  |
        |  | 4|  | 5|  | 6|  | 7|
        | 0|  | 1|  | 2|  | 3|  |
        """
        self._tiles: list[Tile] = []
        y = TILE_SIZE * BOARD_SIZE
        for row in range(HALF_BOARD_SIZE):
            x = 0
            for rep in range(2):  # two rows at a time
                for t in range(HALF_BOARD_SIZE):
                    self._tiles.append(Tile(x, y))
                    if (
                        len(self._tiles) <= HALF_BOARD_SIZE * (HALF_BOARD_SIZE - 1)
                        or len(self._tiles) > HALF_BOARD_SIZE * (HALF_BOARD_SIZE + 1)
                    ):
                        # tile starts with piece
                        self._tiles[-1].setOccupied()
                    x += TILE_SIZE * 2
                y -= TILE_SIZE
                x = TILE_SIZE

    def _drawTiles(self):
        for tile in self._tiles:
            tile.draw(self._window)

    def _begin(self) -> PlayerColor:
        """Return the winner."""
        turnColor = PlayerColor.BLACK
        status = ""
        while status != "loss":
            if turnColor == PlayerColor.BLACK:
                status = self._blackPlayer.takeTurn(self)
                turnColor = PlayerColor.RED
            else:
                status = self._redPlayer.takeTurn(self)
                turnColor = PlayerColor.BLACK
        return turnColor

    def _reset(self):
        self._populate()
        for piece in self._blackPlayer.getPieces():
            piece.undraw()
        for piece in self._redPlayer.getPieces():
            piece.undraw()

    def getWindow(self) -> GraphWin:
        return self._window

    def getTile(self, tilenum: int) -> Tile:
        return self._tiles[tilenum]

    def getOpponent(self, color: PlayerColor) -> 'Player | CPUPlayer':
        if color == PlayerColor.BLACK:
            return self._redPlayer
        return self._blackPlayer


class Piece(Circle):

    def __init__(self, board: Board, color: PlayerColor, tilenum: int):
        self._color = color
        self._tilenum = tilenum
        self._isKing = False
        self._location = board.getTile(tilenum).getLocation()
        Circle.__init__(self, self._location, TILE_SIZE / 5 * 2)
        self.setFill(color)
        self.setOutline("white")
        self.draw(board.getWindow())

    def _isEdgeTile(self, tilenum: int) -> bool:
        return not (
            tilenum > HALF_BOARD_SIZE - 1  # bottom row
            and tilenum < (BOARD_SIZE - 1) * HALF_BOARD_SIZE  # top row
            and tilenum % BOARD_SIZE != 0  # left column
            and tilenum % BOARD_SIZE != BOARD_SIZE - 1  # right column
        )

    def _genCrown(self, window: GraphWin):
        points = [
            Point(-TILE_SIZE / 8, TILE_SIZE / 10),
            Point(-TILE_SIZE / 5, -TILE_SIZE / 10),
            Point(-TILE_SIZE / 10, -TILE_SIZE / 20),
            Point(0, -TILE_SIZE / 5),
            Point(TILE_SIZE / 10, -TILE_SIZE / 20),
            Point(TILE_SIZE / 5, -TILE_SIZE / 10),
            Point(TILE_SIZE / 8, TILE_SIZE / 10),
        ]

        if window.trans:
            points = [Point(self._location.getX() + p.x, self._location.getY() + p.y * -1) for p in points]
        else:
            points = [Point(self._location.getX() + p.x, self._location.getY() + p.y) for p in points]

        self._crown = Polygon(points)
        self._crown.setFill("gold")
        self._crown.setOutline("gold")
        self._crown.draw(window)

    def undraw(self):
        if self._isKing:
            self._crown.undraw()
        Circle.undraw(self)

    def select(self):
        self.setOutline("yellow")

    def deselect(self):
        self.setOutline("white")

    def _getPosMoves(self) -> tuple[int, ...]:
        if self._isKing:
            if self._tilenum % BOARD_SIZE == 0 or self._tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # edge of board
                tempmoves = [self._tilenum - HALF_BOARD_SIZE, self._tilenum + HALF_BOARD_SIZE]
            elif (self.getLocation().getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 1,3,5,7 (odd numbered rows)
                tempmoves = [
                    self._tilenum - HALF_BOARD_SIZE,
                    self._tilenum - HALF_BOARD_SIZE + 1,
                    self._tilenum + HALF_BOARD_SIZE,
                    self._tilenum + HALF_BOARD_SIZE + 1,
                ]
            else:
                # rows 2,4,6,8 (even numbered rows)
                tempmoves = [
                    self._tilenum - HALF_BOARD_SIZE - 1,
                    self._tilenum - HALF_BOARD_SIZE,
                    self._tilenum + HALF_BOARD_SIZE - 1,
                    self._tilenum + HALF_BOARD_SIZE,
                ]
            # filter for tiles that exist
            moves = [tm for tm in tempmoves if tm >= 0 and tm < BOARD_SIZE * HALF_BOARD_SIZE]

        elif self._color == PlayerColor.BLACK:
            if self._tilenum % BOARD_SIZE == 0 or self._tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # edge of board
                moves = [self._tilenum + HALF_BOARD_SIZE]
            elif (self.getLocation().getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 3,5,7
                moves = [self._tilenum + HALF_BOARD_SIZE, self._tilenum + HALF_BOARD_SIZE + 1]
            else:
                # rows 2,4,6,8
                moves = [self._tilenum + HALF_BOARD_SIZE - 1, self._tilenum + HALF_BOARD_SIZE]

        else:
            if self._tilenum % BOARD_SIZE == 0 or self._tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # edge of board
                moves = [self._tilenum - HALF_BOARD_SIZE]
            elif (self.getLocation().getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 1,3,5,7
                moves = [self._tilenum - HALF_BOARD_SIZE, self._tilenum - HALF_BOARD_SIZE + 1]
            else:
                # rows 2,4,6
                moves = [self._tilenum - HALF_BOARD_SIZE - 1, self._tilenum - HALF_BOARD_SIZE]

        return tuple(moves)

    def getMoves(self, board: Board) -> tuple[int, ...]:
        neighbors = self._getPosMoves()
        return tuple(filter(lambda n: not board.getTile(n).isOccupied(), neighbors))

    def getJumps(self, board: Board) -> tuple['Jump', ...]:  # (tile of piece to jump, empty tile to jump to)
        neighbors = self._getPosMoves()
        oppTiles = board.getOpponent(self._color).getTiles()
        jumps: list[Jump] = []
        for n in neighbors:
            if n in oppTiles:  # opponent piece occupies possible move tile
                nLoc = board.getTile(n).getLocation()
                if nLoc.getX() > self._location.getX():
                    if nLoc.getY() > self._location.getY():
                        jumps.append(Jump(n, self._tilenum - BOARD_SIZE + 1))  # down-right
                    else:
                        jumps.append(Jump(n, self._tilenum + BOARD_SIZE + 1))  # up-right
                else:
                    if nLoc.getY() > self._location.getY():
                        jumps.append(Jump(n, self._tilenum - BOARD_SIZE - 1))  # down-left
                    else:
                        jumps.append(Jump(n, self._tilenum + BOARD_SIZE - 1))  # up-left
        return tuple(filter(
            lambda j: not self._isEdgeTile(j.jumpedTile) and not board.getTile(j.endTile).isOccupied(),
            jumps
        ))

    def moveTo(self, board: Board, tile: int) -> Board:
        dx = board.getTile(tile).getLocation().getX() - self._location.getX()
        dy = board.getTile(tile).getLocation().getY() - self._location.getY()
        board.getTile(self._tilenum).setOccupied(False)
        board.getTile(tile).setOccupied()
        self._tilenum = tile
        self._location = board.getTile(tile).getLocation()
        self.move(dx, dy)
        if self._isKing:
            self._crown.move(dx, dy)
        elif (
            (self._color == PlayerColor.BLACK and self._tilenum >= HALF_BOARD_SIZE * (BOARD_SIZE - 1))
            or (self._color == PlayerColor.RED and self._tilenum < HALF_BOARD_SIZE)
        ):
            self._isKing = True
            self._genCrown(board.getWindow())
        return board

    def jumpTo(self, board: Board, jump: 'Jump') -> Board:
        board = self.moveTo(board, jump.endTile)
        board.getOpponent(self._color).killPiece(jump.jumpedTile)
        board.getTile(jump.jumpedTile).setOccupied(False)
        return board

    def doMove(self, board: Board, tj: int | list['Jump']) -> Board:
        if isinstance(tj, int):
            return self.moveTo(board, tj)

        # tj is a list of Jumps
        for j in tj[:-1]:
            self.jumpTo(board, j)
            time.sleep(CPU_DELAY)
        return self.jumpTo(board, tj[-1])

    def isKing(self) -> bool:
        return self._isKing

    def getTile(self) -> int:
        return self._tilenum

    def getLocation(self) -> Point:
        return self._location


class Jump:

    def __init__(self, jumpedTile: int, endTile: int):
        self.jumpedTile = jumpedTile
        self.endTile = endTile


class Player:

    def __init__(self, board: Board, color: PlayerColor):
        self._color = color
        self._populate(board)
        self._selected: Piece | None = None

    def _populate(self, board: Board):
        startTile = 0 if self._color == PlayerColor.BLACK else HALF_BOARD_SIZE * (HALF_BOARD_SIZE + 1)
        self._pieces = [
            Piece(board, self._color, tile)
            for tile in range(startTile, startTile + HALF_BOARD_SIZE * (HALF_BOARD_SIZE - 1))
        ]

    def _canJump(self, board: Board) -> bool:
        return any(piece.getJumps(board) for piece in self._pieces)

    def _noMoves(self, board: Board) -> bool:
        return not any(piece.getMoves(board) or piece.getJumps(board) for piece in self._pieces)

    def takeTurn(self, board: Board) -> typing.Literal["loss"] | tuple[int, list[Jump]] | tuple[int, int]:
        if self._noMoves(board):
            return "loss"

        moves = ()
        jumps = ()
        jumpedJumps: list[Jump] = list()
        startTile = -1

        while True:

            if self._selected:  # piece already selected
                click = board.getWindow().getMouse()
                doubleJump = False

                for jump in jumps:  # if valid jump clicked: jump, deselect all and pass turn
                    endTileLoc = board.getTile(jump.endTile).getLocation()
                    if (
                        abs(click.getX() - endTileLoc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - endTileLoc.getY()) <= TILE_SIZE / 2
                    ):
                        for tile in jumps:
                            board.getTile(tile.endTile).deselect()

                        if startTile < 0:
                            startTile = self._selected.getTile()
                        jumpedJumps.append(jump)

                        wasKing = self._selected.isKing()
                        board = self._selected.jumpTo(board, jump)

                        # Check for double jumps
                        jumps = self._selected.getJumps(board)
                        if not (self._selected.isKing() and not wasKing) and jumps:
                            doubleJump = True
                            for jump in jumps:
                                board.getTile(jump.endTile).select()

                        else:
                            self._selected.deselect()
                            self._selected = None

                            return (startTile, jumpedJumps)

                for move in moves:  # if valid move clicked: move, deselect all, and pass turn
                    moveLoc = board.getTile(move).getLocation()
                    if (
                        abs(click.getX() - moveLoc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - moveLoc.getY()) <= TILE_SIZE / 2
                    ):
                        for tile in moves:
                            board.getTile(tile).deselect()

                        packet = (self._selected.getTile(), move)  # encode the move for sending

                        board = self._selected.moveTo(board, move)
                        self._selected.deselect()
                        self._selected = None

                        return packet

                # else, deselect all
                if not doubleJump:
                    for tile in jumps:
                        board.getTile(tile.endTile).deselect()
                    for tile in moves:
                        board.getTile(tile).deselect()
                    self._selected.deselect()
                    self._selected = None

            else:  # no pieces selected
                click = board.getWindow().getMouse()
                for p in self._pieces:  # if player piece clicked, select all
                    pLoc = p.getLocation()
                    if (
                        abs(click.getX() - pLoc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - pLoc.getY()) <= TILE_SIZE / 2
                    ):
                        self._selected = p
                        self._selected.select()
                        if self._canJump(board):
                            jumps = self._selected.getJumps(board)
                            for jump in jumps:
                                board.getTile(jump.endTile).select()
                        else:
                            moves = self._selected.getMoves(board)
                            for tile in moves:
                                board.getTile(tile).select()
                        break

    def killPiece(self, tilenum: int):
        for piece in self._pieces:
            if piece.getTile() == tilenum:
                self._pieces.remove(piece)
                piece.undraw()
                break

    def getTiles(self) -> list[int]:
        return [p.getTile() for p in self._pieces]

    def getPieces(self) -> list[Piece]:
        return self._pieces

    def getPiece(self, tilenum: int) -> Piece | None:
        for p in self._pieces:
            if p.getTile() == tilenum:
                return p


class CPUPlayer(Player):

    def _genScore(self, board: Board) -> int:
        """A metric to estimate who is winning. Currently unused.

        Return the difference between this player's score and the opponent's score where each remaining pawn scores
        one point and each remaining king scores two points. 

        """
        my_score = sum(2 if piece.isKing() else 1 for piece in self._pieces)
        op_score = sum(2 if piece.isKing() else 1 for piece in board.getOpponent(self._color).getPieces())
        return my_score - op_score

    def takeTurn(self, board: Board) -> typing.Literal["loss"] | None:
        """Make a random legal move.

        :return: `"loss"` if unable to make a move.

        """
        if self._noMoves(board):
            return "loss"

        time.sleep(CPU_DELAY)
        if self._canJump(board):
            jumps = [(piece, jump) for piece in self._pieces for jump in piece.getJumps(board)]
            piece, jump = random.choice(jumps)
            wasKing = piece.isKing()
            board = piece.jumpTo(board, jump)

            if not (piece.isKing() and not wasKing):
                while jumps := piece.getJumps(board):
                    time.sleep(CPU_DELAY)
                    board = piece.jumpTo(board, random.choice(jumps))
        else:
            moves = [(piece, move) for piece in self._pieces for move in piece.getMoves(board)]
            piece, move = random.choice(moves)
            board = piece.moveTo(board, move)

        self._genScore(board)  # BUGTEST


if __name__ == "__main__":
    players = int(input("How many players? "))
    b = Board(players)
    if players == 2:
        winner = b._begin()
        print(winner.capitalize(), "player won.")
