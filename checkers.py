# Logan Cary
# checkers.py
# A single or two player checkers game, or a simulation of a checkers game

    # 0: random simulation
    # 1: player vs random AI
    # 2: player vs player
    
# Last edited: June 10, 2020


from graphics import *
from tkinter import *
from random import choice
from time import sleep


TILE_SIZE = 80
CPU_DELAY = 1


class Tile(Rectangle):

    def __init__(self, x, y):
        Rectangle.__init__(self, Point(x,y), Point(x+TILE_SIZE,y-TILE_SIZE))
        self.setFill("black")
        self._location = Point(x+TILE_SIZE/2, y-TILE_SIZE/2) # center of tile
        self._isOccupied = False

    def select(self):
        self.setOutline("cyan")

    def deselect(self):
        self.setOutline("black")

    def isOccupied(self):
        return self._isOccupied

    def setOccupied(self, tf=True):
        self._isOccupied = tf

    def getLocation(self):
        return self._location


class Board:

    def __init__(self, window):
        self._window = window
        self._tiles = []
        self._populate()
        self._drawTiles()

        if players == 2: 
            self._blackPlayer = Player(self, "black")
            self._redPlayer = Player(self, "red")
            self._begin()
        elif players == 1:
            self._blackPlayer = Player(self, "black")
            self._redPlayer = CPUPlayer(self, "red")
            self._begin()
        else:
            sims = int(input("How many simulations? "))
            for s in range(sims):
                self._blackPlayer = CPUPlayer(self, "black")
                self._redPlayer = CPUPlayer(self, "red")
                self._begin()
                self._reset()
        
    def _populate(self):  
        y = TILE_SIZE * 8
        for row in range(4):     
            x = 0
            for rep in range(2): 
                for t in range(4):
                    self._tiles.append(Tile(x,y))
                    if len(self._tiles) < 13 or len(self._tiles) > 20: # tile starts with piece
                        self._tiles[-1].setOccupied()
                    x += TILE_SIZE * 2
                y -= TILE_SIZE
                x = TILE_SIZE

    def _drawTiles(self):
        for tile in self._tiles:
            tile.draw(self._window)

    def _begin(self):
        turnColor = "black"
        while self != "loss":
            if turnColor == "black":
                self = self._blackPlayer.takeTurn(self)
                turnColor = "red"
            else:
                self = self._redPlayer.takeTurn(self)
                turnColor = "black"
        print(turnColor, "player won")

    def _reset(self):
        self._tiles = []
        self._populate()
        for piece in self._blackPlayer.getPieces():
            piece.undraw()
        for piece in self._redPlayer.getPieces():
            piece.undraw()

    def getWindow(self):
        return self._window

    def getTile(self, tilenum):
        return self._tiles[tilenum]

    def getOpponent(self, color):
        if color == "black":
            return self._redPlayer
        return self._blackPlayer


class Piece(Circle):

    def __init__(self, board, color, tilenum):
        self._color = color
        self._tilenum = tilenum
        self._isKing = False
        self._location = board.getTile(tilenum).getLocation()
        Circle.__init__(self, self._location, TILE_SIZE/5*2)
        self.setFill(color)
        self.setOutline("white")
        self.draw(board.getWindow())

    def _isEdgeTile(self, tilenum):
        if tilenum > 3 and tilenum < 28 and tilenum % 8 != 0 and tilenum % 8 != 7:
            return False
        return True

    def _genCrown(self, window):
        p1 = Point(self._location.getX()-TILE_SIZE/8, self._location.getY()+TILE_SIZE/10)
        p2 = Point(self._location.getX()-TILE_SIZE/5, self._location.getY()-TILE_SIZE/10)
        p3 = Point(self._location.getX()-TILE_SIZE/10, self._location.getY()-TILE_SIZE/20)
        p4 = Point(self._location.getX(), self._location.getY()-TILE_SIZE/5)
        p5 = Point(self._location.getX()+TILE_SIZE/10, self._location.getY()-TILE_SIZE/20)
        p6 = Point(self._location.getX()+TILE_SIZE/5, self._location.getY()-TILE_SIZE/10)
        p7 = Point(self._location.getX()+TILE_SIZE/8, self._location.getY()+TILE_SIZE/10)
        self._crown = Polygon([p1,p2,p3,p4,p5,p6,p7])
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

    def _getPosMoves(self):
        moves = []
        if self._isKing:
            tempmoves = []
            if self._tilenum % 8 == 0 or self._tilenum % 8 == 7: # edge of board
                tempmoves = [self._tilenum-4, self._tilenum+4]
            elif (self.getLocation().getY()/TILE_SIZE-.5) % 2 == 0: # rows 1,3,5,7
                tempmoves = [self._tilenum-4, self._tilenum-3, self._tilenum+4, self._tilenum+5]
            else: # rows 2,4,6,8
                tempmoves = [self._tilenum-5, self._tilenum-4, self._tilenum+3, self._tilenum+4]
            for tm in tempmoves:
                if tm >= 0 and tm <= 31: # tile exists
                    moves.append(tm)
            
        elif self._color == "black":
            if self._tilenum % 8 == 0 or self._tilenum % 8 == 7: # edge of board
                moves = [self._tilenum+4]
            elif (self.getLocation().getY()/TILE_SIZE-.5) % 2 == 0: # rows 3,5,7
                moves = [self._tilenum+4, self._tilenum+5]
            else: # rows 2,4,6,8
                moves = [self._tilenum+3, self._tilenum+4]
            
        else:
            if self._tilenum % 8 == 0 or self._tilenum % 8 == 7: # edge of board
                moves = [self._tilenum-4]
            elif (self.getLocation().getY()/TILE_SIZE-.5) % 2 == 0: # rows 1,3,5,7
                moves = [self._tilenum-4, self._tilenum-3]
            else: # rows 2,4,6
                moves = [self._tilenum-5, self._tilenum-4]

        return tuple(moves)

    def getMoves(self, board):
        neighbors = self._getPosMoves()
        moves = []
        for n in neighbors:
            if not board.getTile(n).isOccupied():
                moves.append(n)
        return tuple(moves)

    def getJumps(self, board): # (tile of piece to jump, empty tile to jump to)
        neighbors = self._getPosMoves()
        oppTiles = board.getOpponent(self._color).getTiles()
        jumps = []
        for n in neighbors:
            if n in oppTiles: # opponent piece occupies possible move tile
                nLoc = board.getTile(n).getLocation()
                if nLoc.getX() > self._location.getX():
                    if nLoc.getY() > self._location.getY():
                        jumps.append((n, self._tilenum-7)) # down-right
                    else:
                        jumps.append((n, self._tilenum+9)) # up-right
                else:
                    if nLoc.getY() > self._location.getY():
                        jumps.append((n, self._tilenum-9)) # down-left
                    else:
                        jumps.append((n, self._tilenum+7)) # up-left                        
        legalJumps = []
        for j in jumps:
            if not self._isEdgeTile(j[0]) and not board.getTile(j[1]).isOccupied(): # tile to jump to is unoccupied
                legalJumps.append(j)
        return tuple(legalJumps)

    def moveTo(self, board, tile):
        dx = board.getTile(tile).getLocation().getX() - self._location.getX()
        dy = board.getTile(tile).getLocation().getY() - self._location.getY()
        board.getTile(self._tilenum).setOccupied(False)
        board.getTile(tile).setOccupied()
        self._tilenum = tile
        self._location = board.getTile(tile).getLocation()
        self.move(dx, dy)
        if self._isKing:
            self._crown.move(dx, dy)
        elif (self._color == "black" and self._tilenum > 27) or\
           (self._color == "red" and self._tilenum < 4):
            self._isKing = True
            self._genCrown(board.getWindow())
        return board

    def jumpTo(self, board, jump):
        board = self.moveTo(board, jump[1])
        board.getOpponent(self._color).killPiece(jump[0])
        board.getTile(jump[0]).setOccupied(False)
        return board

    def doMove(self, board, tj):
        try:
            return self.jumpTo(board, tj)
        except TypeError:
            return self.moveTo(board, tj)

    def isKing(self):
        return self._isKing

    def getTile(self):
        return self._tilenum

    def getLocation(self):
        return self._location


class Player:

    def __init__(self, board, color):
        self._color = color
        self._pieces = []
        self._populate(board)
        self._selected = None

    def _populate(self, board):
        startTile = 0
        if self._color == "red":
            startTile = 20
        for tile in range(startTile, startTile+12):
            self._pieces.append(Piece(board, self._color, tile))

    def _canJump(self, board):
        for piece in self._pieces:
            if len(piece.getJumps(board)) > 0:
                return True
        return False

    def _noMoves(self, board):
        for piece in self._pieces:
            if len(piece.getMoves(board)) > 0 or len(piece.getJumps(board)) > 0:
                return False
        return True

    def takeTurn(self, board):
        if self._noMoves(board):
            return "loss"
        
        moves = ()
        jumps = ()
        while True:
            
            if self._selected: # piece already selected
                click = board.getWindow().getMouse()
                doubleJump = False
                
                for jump in jumps: # if valid jump clicked: jump, deselect all and pass turn 
                    if abs(click.getX()-board.getTile(jump[1]).getLocation().getX()) <= TILE_SIZE/2 and\
                       abs(click.getY()-board.getTile(jump[1]).getLocation().getY()) <= TILE_SIZE/2:
                        for tile in jumps:
                            board.getTile(tile[1]).deselect()
                        wasKing = self._selected.isKing()
                        board = self._selected.jumpTo(board, jump)
                        jumps = self._selected.getJumps(board)
                        if not (self._selected.isKing() and not wasKing) and len(jumps) > 0:
                            doubleJump = True
                            for jump in jumps:
                                board.getTile(jump[1]).select()
                        else:
                            self._selected.deselect()
                            self._selected = None
                            return board
                    
                for move in moves: # if valid move clicked: move, deselect all and pass turn
                    if abs(click.getX()-board.getTile(move).getLocation().getX()) <= TILE_SIZE/2 and\
                       abs(click.getY()-board.getTile(move).getLocation().getY()) <= TILE_SIZE/2:
                        for tile in moves:
                            board.getTile(tile).deselect()
                        board = self._selected.moveTo(board, move)
                        self._selected.deselect()
                        self._selected = None
                        return board
                    
                # else, deselect all
                if not doubleJump:
                    for tile in jumps:
                        board.getTile(tile[1]).deselect()
                    for tile in moves:
                        board.getTile(tile).deselect()
                    self._selected.deselect()
                    self._selected = None

            else: # no pieces selected
                click = board.getWindow().getMouse()     
                for p in self._pieces: # if player piece clicked, select all
                    if abs(click.getX()-p.getLocation().getX()) <= TILE_SIZE/2 and\
                       abs(click.getY()-p.getLocation().getY()) <= TILE_SIZE/2:
                        self._selected = p
                        self._selected.select()
                        if self._canJump(board):
                            jumps = self._selected.getJumps(board)
                            for jump in jumps:
                                board.getTile(jump[1]).select()
                        else:
                            moves = self._selected.getMoves(board)
                            for tile in moves:
                                board.getTile(tile).select()
                        break

    def killPiece(self, tilenum):
        for piece in self._pieces:
            if piece.getTile() == tilenum:
                self._pieces.remove(piece)
                piece.undraw()
                break

    def getTiles(self):
        tiles = []
        for p in self._pieces:
            tiles.append(p.getTile())
        return tuple(tiles)

    def getPieces(self):
        return self._pieces


class CPUPlayer(Player):

    def __init__(self, board, color):
        Player.__init__(self, board, color)

    def _genScore(self, board): # this is not important
        score = 0
        for piece in self._pieces:
            if piece.isKing():
                score += 2
            else:
                score += 1
        for piece in board.getOpponent(self._color).getPieces():
            if piece.isKing():
                score -= 2
            else:
                score -= 1
        return score

    def _pickMove(self, board, moves):  # BROKEN: causes all pieces to move
        newBoard = None
        for move in moves:
            newBoard = move[0].doMove(board, move[1])

    def takeTurn(self, board):
        if self._noMoves(board):
            return "loss"
        
        sleep(CPU_DELAY)
        if self._canJump(board):
            jumps = []
            for piece in self._pieces:
                for jump in piece.getJumps(board):
                    jumps.append((piece, jump))

            # self._pickMove(board, jumps)  # BROKEN
            jump = choice(jumps)
            
            wasKing = jump[0].isKing()
            board = jump[0].jumpTo(board, jump[1])
            if not (jump[0].isKing() and not wasKing):
                while len(jump[0].getJumps(board)) > 0:
                    sleep(CPU_DELAY)
                    board = jump[0].jumpTo(board, choice(jump[0].getJumps(board)))
        else:
            moves = []
            for piece in self._pieces:
                for move in piece.getMoves(board):
                    moves.append((piece, move))

            # self._pickMove(board, moves)  # BROKEN
            move = choice(moves)
            
            board = move[0].moveTo(board, move[1])

        self._genScore(board)    #BUGTEST
        return board


if __name__ == "__main__":
    players = int(input("How many players? "))
    window = GraphWin("Checkers",TILE_SIZE*8,TILE_SIZE*8)
    window.setBackground("red")
    Board(window)
