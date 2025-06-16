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


__all__ = ["PlayerColor", "Board"]


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
        self._is_occupied = False

    def select(self):
        self.setOutline("cyan")

    def deselect(self):
        self.setOutline("black")

    @property
    def is_occupied(self) -> bool:
        return self._is_occupied

    def set_occupied(self, tf=True):
        self._is_occupied = tf

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
        self._draw_tiles()

        match players:
            case 2:
                self._black_player = Player(self, PlayerColor.BLACK)
                self._red_player = Player(self, PlayerColor.RED)
            case 1:
                self._black_player = Player(self, PlayerColor.BLACK)
                self._red_player = CPUPlayer(self, PlayerColor.RED)
            case 0:
                self._black_player = CPUPlayer(self, PlayerColor.BLACK)
                self._red_player = CPUPlayer(self, PlayerColor.RED)
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
                        self._tiles[-1].set_occupied()
                    x += TILE_SIZE * 2
                y -= TILE_SIZE
                x = TILE_SIZE

    def _draw_tiles(self):
        """Draw all tiles in the tiles list to the window."""
        for tile in self._tiles:
            tile.draw(self._window)
    
    def play_one(self) -> PlayerColor:
        """Alias of `play(n=1)`."""
        turn_color = PlayerColor.BLACK
        status = ""
        while status != "loss":
            if turn_color == PlayerColor.BLACK:
                status = self._black_player.take_turn()
                turn_color = PlayerColor.RED
            else:
                status = self._red_player.take_turn()
                turn_color = PlayerColor.BLACK
        self._reset()
        return turn_color

    @typing.overload
    def play(self, n: typing.Literal[1] = 1) -> PlayerColor: ...
    @typing.overload
    def play(self, n: int) -> dict[PlayerColor, int]: ...

    def play(self, n: int = 1) -> PlayerColor | dict[PlayerColor, int]:
        """Play `n` games, alternating turns between players.

        :return: Win counts.
        """
        if n == 1:
            return self.play_one()

        wins = {PlayerColor.BLACK: 0, PlayerColor.RED: 0}
        for _ in range(n):
            winner = self.play_one()
            wins[winner] += 1

        return wins

    def _reset(self):
        """Reset the tiles list and undraw all pieces."""
        for piece in self._black_player.pieces + self._red_player.pieces:
            piece.undraw()
        self._populate()
        self._black_player._populate()
        self._red_player._populate()

    @property
    def window(self) -> GraphWin:
        return self._window

    def get_tile(self, tilenum: int) -> Tile:
        """
        :param tilenum: Index of the tile in the tiles list.
        """
        return self._tiles[tilenum]

    @staticmethod
    def is_edge_tile(tilenum: int) -> bool:
        """Utility function to determine if a tile is on the edge of the board."""
        return (
            tilenum < HALF_BOARD_SIZE  # bottom row
            or tilenum >= (BOARD_SIZE - 1) * HALF_BOARD_SIZE  # top row
            or tilenum % BOARD_SIZE == 0  # left column
            or tilenum % BOARD_SIZE == BOARD_SIZE - 1  # right column
        )

    def get_player(self, color: PlayerColor) -> "Player":
        """Get the player object of the given color."""
        match color:
            case PlayerColor.BLACK:
                return self._black_player
            case PlayerColor.RED:
                return self._red_player
        raise ValueError("Argument must be 'red' or 'black'")


class Jump(typing.NamedTuple):
    jumped_tile: int
    """Index of the tile that is to be "jumped" over."""
    end_tile: int
    """Index of the tile that the jumping piece will subsequently land on."""


class Piece(Circle):

    def __init__(self, board: Board, color: PlayerColor, tilenum: int):
        """
        :param board:
        :param color: Player color that this piece belongs to.
        :param tilenum: Index of the tile that this piece should start on.
        """
        self._board = board
        self._color = color
        self._tilenum = tilenum
        self._is_king = False
        self._location = board.get_tile(tilenum).location
        Circle.__init__(self, self._location, TILE_SIZE / 5 * 2)
        self.setFill(color)
        self.setOutline("white")
        self.draw(board.window)

    def _draw_crown(self):
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
        window = self._board.window
        my_x, my_y = self._location.getX(), self._location.getY()

        if window.trans:
            points = [Point(my_x + p.x, my_y + p.y * -1) for p in points]
        else:
            points = [Point(my_x + p.x, my_y + p.y) for p in points]

        self._crown = Polygon(points)
        self._crown.setFill("gold")
        self._crown.setOutline("gold")
        self._crown.draw(window)

    def undraw(self):
        if self._is_king:
            self._crown.undraw()
        Circle.undraw(self)

    def select(self):
        self.setOutline("yellow")

    def deselect(self):
        self.setOutline("white")

    def _get_possible_moves(self) -> list[int]:
        """
        :return: List of tile numbers representing the tiles that this piece can move to if they are unoccupied.
        """
        tilenum = self._tilenum
        if self._is_king:
            if tilenum % BOARD_SIZE == 0 or tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # left or right edge of the board
                tempmoves = [tilenum - HALF_BOARD_SIZE, tilenum + HALF_BOARD_SIZE]
            elif (self.location.getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 1,3,5,7 (odd numbered rows)
                tempmoves = [
                    tilenum - HALF_BOARD_SIZE,
                    tilenum - HALF_BOARD_SIZE + 1,
                    tilenum + HALF_BOARD_SIZE,
                    tilenum + HALF_BOARD_SIZE + 1,
                ]
            else:
                # rows 2,4,6,8 (even numbered rows)
                tempmoves = [
                    tilenum - HALF_BOARD_SIZE - 1,
                    tilenum - HALF_BOARD_SIZE,
                    tilenum + HALF_BOARD_SIZE - 1,
                    tilenum + HALF_BOARD_SIZE,
                ]
            # filter for tiles that exist
            moves = list(filter(lambda tm: tm >= 0 and tm < BOARD_SIZE * HALF_BOARD_SIZE, tempmoves))

        elif self._color == PlayerColor.BLACK:
            if tilenum % BOARD_SIZE == 0 or tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # edge of board
                moves = [tilenum + HALF_BOARD_SIZE]
            elif (self.location.getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 3,5,7
                moves = [tilenum + HALF_BOARD_SIZE, tilenum + HALF_BOARD_SIZE + 1]
            else:
                # rows 2,4,6,8
                moves = [tilenum + HALF_BOARD_SIZE - 1, tilenum + HALF_BOARD_SIZE]

        else:
            if tilenum % BOARD_SIZE == 0 or tilenum % BOARD_SIZE == BOARD_SIZE - 1:
                # edge of board
                moves = [tilenum - HALF_BOARD_SIZE]
            elif (self.location.getY() / TILE_SIZE - 0.5) % 2 == 0:
                # rows 1,3,5,7
                moves = [tilenum - HALF_BOARD_SIZE, tilenum - HALF_BOARD_SIZE + 1]
            else:
                # rows 2,4,6
                moves = [tilenum - HALF_BOARD_SIZE - 1, tilenum - HALF_BOARD_SIZE]

        return moves

    @property
    def moves(self) -> list[int]:
        """
        List of tile numbers representing the tiles that this piece can move to.
        """
        neighbors = self._get_possible_moves()
        return list(filter(lambda n: not self._board.get_tile(n).is_occupied, neighbors))

    @property
    def jumps(self) -> list[Jump]:  # (tile of piece to jump, empty tile to jump to)
        """
        Jumps that this piece can make.
        """
        board = self._board
        neighbors = self._get_possible_moves()
        opponent_tiles = board.get_player(self._color).opponent.tiles
        jumps: list[Jump] = []
        for n in filter(lambda n: n in opponent_tiles, neighbors):
            # opponent piece occupies possible move tile
            n_loc = board.get_tile(n).location
            if n_loc.getX() > self._location.getX():
                if n_loc.getY() > self._location.getY():
                    jumps.append(Jump(n, self._tilenum - BOARD_SIZE + 1))  # down-right
                else:
                    jumps.append(Jump(n, self._tilenum + BOARD_SIZE + 1))  # up-right
            else:
                if n_loc.getY() > self._location.getY():
                    jumps.append(Jump(n, self._tilenum - BOARD_SIZE - 1))  # down-left
                else:
                    jumps.append(Jump(n, self._tilenum + BOARD_SIZE - 1))  # up-left
        return list(filter(
            lambda j: not board.is_edge_tile(j.jumped_tile) and not board.get_tile(j.end_tile).is_occupied,
            jumps
        ))

    def move_to(self, tilenum: int):
        """Redraw this piece on another tile and update the board state accordingly.

        :param tilenum: Index of the tile to move to.
        """
        board = self._board
        tile = board.get_tile(tilenum)
        tile_loc = tile.location
        dx = tile_loc.getX() - self._location.getX()
        dy = tile_loc.getY() - self._location.getY()

        board.get_tile(self._tilenum).set_occupied(False)
        tile.set_occupied()
        self._tilenum = tilenum
        self._location = tile_loc
        self.move(dx, dy)
        if self._is_king:
            self._crown.move(dx, dy)
        elif (
            (self._color == PlayerColor.BLACK and self._tilenum >= HALF_BOARD_SIZE * (BOARD_SIZE - 1))
            or (self._color == PlayerColor.RED and self._tilenum < HALF_BOARD_SIZE)
        ):
            self._is_king = True
            self._draw_crown()

    def jump_to(self, jump: Jump):
        """Complete a jump by moving this piece, eliminating the jumped
        piece, and updating the board state accordingly.

        :param jump:
        """
        board = self._board
        self.move_to(jump.end_tile)
        board.get_player(self._color).opponent.kill_piece(jump.jumped_tile)
        board.get_tile(jump.jumped_tile).set_occupied(False)

    def do_move(self, tj: int | list[Jump]):
        """Generalized method for completing a move.

        :param tj: Index of the tile to move to or a list of consecutive jumps to make.
        """
        if isinstance(tj, int):
            return self.move_to(tj)

        # tj is a list of Jumps
        for j in tj[:-1]:
            self.jump_to(j)
            time.sleep(CPU_DELAY)
        self.jump_to(tj[-1])

    @property
    def is_king(self) -> bool:
        return self._is_king

    @property
    def tilenum(self) -> int:
        """Index of the tile that this piece currently occupies."""
        return self._tilenum

    @property
    def location(self) -> Point:
        """Coordinates for the center of this piece. Same as the location of the tile that this piece occupies."""
        return self._location


class Player:

    def __init__(self, board: Board, color: PlayerColor):
        self._board = board
        self._color = color
        self._populate()

    def _populate(self):
        """Reset and populate the list of pieces this player controls."""
        start_tile = 0 if self._color == PlayerColor.BLACK else HALF_BOARD_SIZE * (HALF_BOARD_SIZE + 1)
        self._pieces = [
            Piece(self._board, self._color, tile)
            for tile in range(start_tile, start_tile + HALF_BOARD_SIZE * (HALF_BOARD_SIZE - 1))
        ]

    @property
    def can_jump(self) -> bool:
        """
        :return: Any piece owned by this player can perform a jump.
        """
        return any(piece.jumps for piece in self._pieces)

    @property
    def has_move(self) -> bool:
        """
        :return: A piece owned by this player can still move or jump.
        """
        return any(piece.moves or piece.jumps for piece in self._pieces)

    def take_turn(self) -> typing.Literal["loss"] | tuple[int, int | list[Jump]]:
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
        if not self.has_move:
            return "loss"

        moves = []
        jumps = []
        jumped_jumps: list[Jump] = []
        selected: Piece | None = None
        start_tile = -1
        board = self._board

        while True:

            if selected:  # piece already selected
                click = board.window.getMouse()
                double_jump = False

                for jump in jumps:  # if valid jump clicked: jump, deselect all and pass turn
                    end_tile_loc = board.get_tile(jump.end_tile).location
                    if (
                        abs(click.getX() - end_tile_loc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - end_tile_loc.getY()) <= TILE_SIZE / 2
                    ):
                        for tile in jumps:
                            board.get_tile(tile.end_tile).deselect()

                        if start_tile < 0:
                            start_tile = selected.tilenum
                        jumped_jumps.append(jump)

                        was_king = selected.is_king
                        selected.jump_to(jump)

                        # Check for double jumps
                        jumps = selected.jumps
                        if not (selected.is_king and not was_king) and jumps:
                            double_jump = True
                            for jump in jumps:
                                board.get_tile(jump.end_tile).select()

                        else:
                            selected.deselect()
                            selected = None

                            return start_tile, jumped_jumps

                for move in moves:  # if valid move clicked: move, deselect all, and pass turn
                    move_loc = board.get_tile(move).location
                    if (
                        abs(click.getX() - move_loc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - move_loc.getY()) <= TILE_SIZE / 2
                    ):
                        for tile in moves:
                            board.get_tile(tile).deselect()

                        packet = (selected.tilenum, move)  # encode the move for sending

                        selected.move_to(move)
                        selected.deselect()
                        selected = None

                        return packet

                # else, deselect all
                if not double_jump:
                    for tile in jumps:
                        board.get_tile(tile.end_tile).deselect()
                    for tile in moves:
                        board.get_tile(tile).deselect()
                    selected.deselect()
                    selected = None

            else:  # no pieces selected
                click = board.window.getMouse()
                for p in self._pieces:  # if player piece clicked, select all
                    p_loc = p.location
                    if (
                        abs(click.getX() - p_loc.getX()) <= TILE_SIZE / 2
                        and abs(click.getY() - p_loc.getY()) <= TILE_SIZE / 2
                    ):
                        selected = p
                        selected.select()
                        if self.can_jump:
                            jumps = selected.jumps
                            for jump in jumps:
                                board.get_tile(jump.end_tile).select()
                        else:
                            moves = selected.moves
                            for tile in moves:
                                board.get_tile(tile).select()
                        break

    def kill_piece(self, tilenum: int):
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

    @property
    def opponent(self) -> "Player":
        """This player's opponent."""
        return self._board.get_player(PlayerColor.BLACK if self._color == PlayerColor.RED else PlayerColor.RED)

    def get_piece(self, tilenum: int) -> Piece | None:
        """Retrieve the `Piece` object of this player's piece at the given tile index."""
        for p in filter(lambda p: p.tilenum == tilenum, self._pieces):
            return p


class CPUPlayer(Player):

    @property
    def score(self) -> int:
        """A metric to estimate who is winning. Currently unused.

        Return the difference between this player's score and the opponent's score where each remaining pawn scores
        one point and each remaining king scores two points. 
        """
        my_score = sum(2 if piece.is_king else 1 for piece in self._pieces)
        op_score = sum(2 if piece.is_king else 1 for piece in self.opponent.pieces)
        return my_score - op_score

    def take_turn(self) -> typing.Literal["loss"] | None:
        """Make a random legal move.

        :return: `"loss"` if unable to make a move.
        """
        if not self.has_move:
            return "loss"

        time.sleep(CPU_DELAY)
        if self.can_jump:
            jumps = [(piece, jump) for piece in self._pieces for jump in piece.jumps]
            piece, jump = random.choice(jumps)
            was_king = piece.is_king
            piece.jump_to(jump)

            if not (piece.is_king and not was_king):
                while jumps := piece.jumps:
                    time.sleep(CPU_DELAY)
                    piece.jump_to(random.choice(jumps))
        else:
            moves = [(piece, move) for piece in self._pieces for move in piece.moves]
            piece, move = random.choice(moves)
            piece.move_to(move)


if __name__ == "__main__":
    players = int(input("How many players? "))
    board = Board(players)
    if players == 0:
        games = int(input("How many sims? "))
        counts = board.play(games)
        print(counts)
    else:
        board.play_one()
