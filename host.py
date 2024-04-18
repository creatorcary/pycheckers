# server.py
import socket
import pickle
from checkers import *


def start_server():
    host = 'localhost'  # Host IP
    port = 12345  # Use a non-privileged port number

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()

        with conn:
            print('Connected by', addr)

            # Setup game
            board = Board()

            while True:
                # Make a move
                move = board._blackPlayer.takeTurn(board)
                print(move)

                # Serialize and send move to the client
                packet = pickle.dumps(move)
                conn.sendall(packet)

                # Wait for a move from the client
                packet = conn.recv(1024)
                from_tile, move = pickle.loads(packet)
                print('Received response:', from_tile, move)

                # Update the board with the opponent's move
                board._redPlayer.getPiece(from_tile).doMove(board, move)

            input()


if __name__ == "__main__":
    start_server()