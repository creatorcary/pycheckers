# client.py
import socket
import pickle
from checkers import *


def start_client():
    host = 'localhost'  # Server's IP
    port = 12345  # The same port as used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # Setup game
        board = Board()

        while True:
            # Wait for a move from the host
            packet = s.recv(1024)
            from_tile, move = pickle.loads(packet)  # Convert bytes back to object
            print('Received response:', from_tile, move)

            # Update the board with the opponent's move
            board._blackPlayer.getPiece(from_tile).doMove(board, move)

            # Make a move
            move = board._redPlayer.takeTurn(board)
            print(move)

            # Serialize and send move to the host
            packet = pickle.dumps(move)
            s.sendall(packet)

        input()


if __name__ == "__main__":
    start_client()