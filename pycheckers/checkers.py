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
"""Half of `BOARD_SIZE`. Also how many playable tiles fit in one row."""
CPU_DELAY = 0.5
"""Number of seconds to wait between double jumps and CPU-player moves."""


class PlayerColor(enum.StrEnum):
    BLACK = "black"
    RED = "red"


class Tile(Rectangle):
    """A single black tile on the board that pieces can play on."""

    def __init__(self, x: int | float, y: int | float):
        """
        :param x: x-coordinate of the tile's bottom-left corner.
        :param y: y-coordinate of the tile's bottom-left corner.
        """
        Rectangle.__init__(self, Point(x, y), Point(x + TILE_SIZE, y - TILE_SIZE))
        self.setFill("black")
        self._location = Point(x + TILE_SIZE / 2, y - TILE_SIZE / 2)  # center of tile
        self._isOccupied = False

    def select(self):
        self.setOutline("cyan")

    def deselect(self):
        self.setOutline("black")

    @property
    def isOccupied(self) -> bool:
        return self._isOccupied

    def setOccupied(self, tf=True):
        self._isOccupied = tf

    @property
    def location(self) -> Point:
        """Coordinates for the center of this tile (where a piece would be drawn)."""
        return self._location


class Board:

    def __init__(self, players: int = 2, invert: bool = False):
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
        """Reset and populate the tiles list.

        Tile indices are arranged like so:
        |  |  |  |  |  |  |  |  |
        |-:|-:|-:|-:|-:|-:|-:|-:|
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
        """Draw all tiles in the tiles list to the window."""
        for tile in self._tiles:
            tile.draw(self._window)

    def _begin(self) -> PlayerColor:
        """Play a single game, alternating turns between players.

        :return: The winner.
        """
        turnColor = PlayerColor.BLACK
        status = ""
        while status != "loss":
            if turnColor == PlayerColor.BLACK:
                status = self._blackPlayer.takeTurn()
                turnColor = PlayerColor.RED
            else:
                status = self._redPlayer.takeTurn()
                turnColor = PlayerColor.BLACK
        return turnColor

    def _reset(self):
        """Reset the tiles list and undraw all pieces."""
        self._populate()
        for piece in self._blackPlayer.pieces:
            piece.undraw()
        for piece in self._redPlayer.pieces:
            piece.undraw()

    @property
    def window(self) -> GraphWin:
        return self._window

    def getTile(self, tilenum: int) -> Tile:
        """
        :param tilenum: Index of the tile in the tiles list.
        """
        return self._tiles[tilenum]

    @staticmethod
    def isEdgeTile(tilenum: int) -> bool:
        """Utility function to determine if a tile is on the edge of the board."""
        return (
            tilenum < HALF_BOARD_SIZE  # bottom row
            or tilenum >= (BOARD_SIZE - 1) * HALF_BOARD_SIZE  # top row
            or tilenum % BOARD_SIZE == 0  # left column
            or tilenum % BOARD_SIZE == BOARD_SIZE - 1  # right column
        )

    def getOpponent(self, color: PlayerColor) -> 'Player | CPUPlayer':
        """Get the player object that opposes the given color."""
        if color == PlayerColor.BLACK:
            return self._redPlayer
        return self._blackPlayer


class Piece(Circle):

    def __init__(self, board: Board, color: PlayerColor, tilenum: int):
        """
        :param board:
        :param color: Player color that this piece belongs to.
        :param tilenum: Index of the tile that this piece should start on.
        """
        self._color = color
        self._tilenum = tilenum
        self._isKing = False
        self._location = board.getTile(tilenum).location
        Circle.__init__(self, self._location, TILE_SIZE / 5 * 2)
        self.setFill(color)
        self.setOutline("white")
        self.draw(board.window)

    def _genCrown(self, window: GraphWin):
        """Draw a gold crown on this piece."""
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

    def _getPosMoves(self) -> list[int]:
        """
        :return: List of tile numbers representing the tiles that this piece can move to if they are unoccupied.
        """
        if self._isKing:
            if self._tilenum % BOARD_SIZE == 0 or self._tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # left or right edge of the board
                tempmoves = [self._tilenum - HALF_BOARD_SIZE, self._tilenum + HALF_BOARD_SIZE]
            elif (self.location.getY() / TILE_SIZE - 0.5) % 2 == 0:
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
            moves = list(filter(lambda tm: tm >= 0 and tm < BOARD_SIZE * HALF_BOARD_SIZE, tempmoves))

        elif self._color == PlayerColor.BLACK:
            if self._tilenum % BOARD_SIZE == 0 or self._tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # edge of board
                moves = [self._tilenum + HALF_BOARD_SIZE]
            elif (self.location.getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 3,5,7
                moves = [self._tilenum + HALF_BOARD_SIZE, self._tilenum + HALF_BOARD_SIZE + 1]
            else:
                # rows 2,4,6,8
                moves = [self._tilenum + HALF_BOARD_SIZE - 1, self._tilenum + HALF_BOARD_SIZE]

        else:
            if self._tilenum % BOARD_SIZE == 0 or self._tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # edge of board
                moves = [self._tilenum - HALF_BOARD_SIZE]
            elif (self.location.getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 1,3,5,7
                moves = [self._tilenum - HALF_BOARD_SIZE, self._tilenum - HALF_BOARD_SIZE + 1]
            else:
                # rows 2,4,6
                moves = [self._tilenum - HALF_BOARD_SIZE - 1, self._tilenum - HALF_BOARD_SIZE]

        return moves

    def getMoves(self, board: Board) -> list[int]:
        """
        :return: List of tile numbers representing the tiles that this piece can move to.
        """
        neighbors = self._getPosMoves()
        return list(filter(lambda n: not board.getTile(n).isOccupied, neighbors))

    def getJumps(self, board: Board) -> tuple['Jump', ...]:  # (tile of piece to jump, empty tile to jump to)
        """
        :return: Jumps that this piece can make.
        """
        neighbors = self._getPosMoves()
        oppTiles = board.getOpponent(self._color).tiles
        jumps: list[Jump] = []
        for n in filter(lambda n: n in oppTiles, neighbors):
            # opponent piece occupies possible move tile
            nLoc = board.getTile(n).location
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
            lambda j: not board.isEdgeTile(j.jumpedTile) and not board.getTile(j.endTile).isOccupied,
            jumps
        ))

    def moveTo(self, board: Board, tile: int) -> Board:
        """Redraw this piece on another tile and update the board state accordingly.
    
        :param board:
        :param tile: Index of the tile to move to.
        """
        dx = board.getTile(tile).location.getX() - self._location.getX()
        dy = board.getTile(tile).location.getY() - self._location.getY()
        board.getTile(self._tilenum).setOccupied(False)
        board.getTile(tile).setOccupied()
        self._tilenum = tile
        self._location = board.getTile(tile).location
        self.move(dx, dy)
        if self._isKing:
            self._crown.move(dx, dy)
        elif (
            (self._color == PlayerColor.BLACK and self._tilenum >= HALF_BOARD_SIZE * (BOARD_SIZE - 1))
            or (self._color == PlayerColor.RED and self._tilenum < HALF_BOARD_SIZE)
        ):
            self._isKing = True
            self._genCrown(board.window)
        return board

    def jumpTo(self, board: Board, jump: 'Jump') -> Board:
        """Complete a jump by moving this piece, eliminating the jumped
        piece, and updating the board state accordingly.

        :param board:
        :param jump:
        """
        board = self.moveTo(board, jump.endTile)
        board.getOpponent(self._color).killPiece(jump.jumpedTile)
        board.getTile(jump.jumpedTile).setOccupied(False)
        return board

    def doMove(self, board: Board, tj: int | list['Jump']) -> Board:
        """Generalized method for completing a move.

        :param board:
        :param tj: Index of the tile to move to or a list of consecutive jumps to make.
        """
        if isinstance(tj, int):
            return self.moveTo(board, tj)

        # tj is a list of Jumps
        for j in tj[:-1]:
            self.jumpTo(board, j)
            time.sleep(CPU_DELAY)
        return self.jumpTo(board, tj[-1])

    @property
    def isKing(self) -> bool:
        return self._isKing

    @property
    def tilenum(self) -> int:
        """Index of the tile that this piece currently occupies."""
        return self._tilenum

    @property
    def location(self) -> Point:
        """Coordinates for the center of this piece. Same as the location of the tile that this piece occupies."""
        return self._location


class Jump(typing.NamedTuple):
    jumpedTile: int
    """Index of the tile that is to be "jumped" over."""
    endTile: int
    """Index of the tile that the jumping piece will subsequently land on."""


class Player:

    def __init__(self, board: Board, color: PlayerColor):
        self._board = board
        self._color = color
        self._populate()
        self._selected: Piece | None = None

    def _populate(self):
        """Reset and populate the list of pieces this player controls."""
        startTile = 0 if self._color == PlayerColor.BLACK else HALF_BOARD_SIZE * (HALF_BOARD_SIZE + 1)
        self._pieces = [
            Piece(self._board, self._color, tile)
            for tile in range(startTile, startTile + HALF_BOARD_SIZE * (HALF_BOARD_SIZE - 1))
        ]

    @property
    def canJump(self) -> bool:
        """
        :return: Any piece owned by this player can perform a jump.
        """
        return any(piece.getJumps(self._board) for piece in self._pieces)

    @property
    def hasMove(self) -> bool:
        """
        :return: A piece owned by this player can still move or jump.
        """
        return any(piece.getMoves(self._board) or piece.getJumps(self._board) for piece in self._pieces)

    def takeTurn(self) -> typing.Literal["loss"] | tuple[int, list[Jump]] | tuple[int, int]:
        """Use mouse input to complete a turn.

        A clicked piece will be highlighted along with its available moves. Clicking on one of its available moves will
        trigger the move. Multijumps require consecutive move selection. If any piece can perform a jump this turn, the
        player will be forced to select a jump.

        :return:
            * If no moves are available at the start of the turn, `"loss"` is returned.

            * If a jump is chosen, the first return is the initial tile index of the piece that is jumping. The second
              return is the list of consecutive jump(s) made.

            * If a move is chosen, the pair of numbers returned is the start tile and end tile of the moving piece.
        """
        if not self.hasMove:
            return "loss"

        moves = ()
        jumps = ()
        jumpedJumps: list[Jump] = list()
        startTile = -1

        while True:

            if self._selected:  # piece already selected
                click = self._board.window.getMouse()
                doubleJump = False

                for jump in jumps:  # if valid jump clicked: jump, deselect all and pass turn
                    endTileLoc = self._board.getTile(jump.endTile).location
                    if (
                        abs(click.getX() - endTileLoc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - endTileLoc.getY()) <= TILE_SIZE / 2
                    ):
                        for tile in jumps:
                            self._board.getTile(tile.endTile).deselect()

                        if startTile < 0:
                            startTile = self._selected.tilenum
                        jumpedJumps.append(jump)

                        wasKing = self._selected.isKing
                        self._board = self._selected.jumpTo(self._board, jump)

                        # Check for double jumps
                        jumps = self._selected.getJumps(self._board)
                        if not (self._selected.isKing and not wasKing) and jumps:
                            doubleJump = True
                            for jump in jumps:
                                self._board.getTile(jump.endTile).select()

                        else:
                            self._selected.deselect()
                            self._selected = None

                            return (startTile, jumpedJumps)

                for move in moves:  # if valid move clicked: move, deselect all, and pass turn
                    moveLoc = self._board.getTile(move).location
                    if (
                        abs(click.getX() - moveLoc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - moveLoc.getY()) <= TILE_SIZE / 2
                    ):
                        for tile in moves:
                            self._board.getTile(tile).deselect()

                        packet = (self._selected.tilenum, move)  # encode the move for sending

                        self._board = self._selected.moveTo(self._board, move)
                        self._selected.deselect()
                        self._selected = None

                        return packet

                # else, deselect all
                if not doubleJump:
                    for tile in jumps:
                        self._board.getTile(tile.endTile).deselect()
                    for tile in moves:
                        self._board.getTile(tile).deselect()
                    self._selected.deselect()
                    self._selected = None

            else:  # no pieces selected
                click = self._board.window.getMouse()
                for p in self._pieces:  # if player piece clicked, select all
                    pLoc = p.location
                    if (
                        abs(click.getX() - pLoc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - pLoc.getY()) <= TILE_SIZE / 2
                    ):
                        self._selected = p
                        self._selected.select()
                        if self.canJump:
                            jumps = self._selected.getJumps(self._board)
                            for jump in jumps:
                                self._board.getTile(jump.endTile).select()
                        else:
                            moves = self._selected.getMoves(self._board)
                            for tile in moves:
                                self._board.getTile(tile).select()
                        break

    def killPiece(self, tilenum: int):
        """Eliminate this player's piece at the given tile index from the game."""
        for piece in filter(lambda piece: piece.tilenum == tilenum, self._pieces):
            self._pieces.remove(piece)
            piece.undraw()
            break

    @property
    def tiles(self) -> set[int]:
        """Set of all tile indices that this player's pieces occupy."""
        return {p.tilenum for p in self._pieces}

    @property
    def pieces(self) -> list[Piece]:
        """List of this player's pieces."""
        return self._pieces

    def getPiece(self, tilenum: int) -> Piece | None:
        """Retrieve the `Piece` object of this player's piece at the given tile index."""
        for p in filter(lambda p: p.tilenum == tilenum, self._pieces):
            return p


class CPUPlayer(Player):

    def _genScore(self, board: Board) -> int:
        """A metric to estimate who is winning. Currently unused.

        Return the difference between this player's score and the opponent's score where each remaining pawn scores
        one point and each remaining king scores two points. 
        """
        my_score = sum(2 if piece.isKing else 1 for piece in self._pieces)
        op_score = sum(2 if piece.isKing else 1 for piece in board.getOpponent(self._color).pieces)
        return my_score - op_score

    def takeTurn(self) -> typing.Literal["loss"] | None:
        """Make a random legal move.

        :return: `"loss"` if unable to make a move.
        """
        if not self.hasMove:
            return "loss"

        time.sleep(CPU_DELAY)
        if self.canJump:
            jumps = [(piece, jump) for piece in self._pieces for jump in piece.getJumps(self._board)]
            piece, jump = random.choice(jumps)
            wasKing = piece.isKing
            board = piece.jumpTo(self._board, jump)

            if not (piece.isKing and not wasKing):
                while jumps := piece.getJumps(board):
                    time.sleep(CPU_DELAY)
                    board = piece.jumpTo(board, random.choice(jumps))
        else:
            moves = [(piece, move) for piece in self._pieces for move in piece.getMoves(self._board)]
            piece, move = random.choice(moves)
            board = piece.moveTo(self._board, move)

        self._genScore(board)  # BUGTEST


if __name__ == "__main__":
    players = int(input("How many players? "))
    b = Board(players)
    if players == 2:
        winner = b._begin()
        print(winner.capitalize(), "player won.")
