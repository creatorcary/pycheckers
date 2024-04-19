# server.py
import socket
import pickle
from checkers import *


def start_server():
    host = 'localhost'  # Host IP
    port = 12345  # Use a non-privileged port number
    print("Waiting for someone to join...")

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


def start_client():
    host = 'localhost'  # Server's IP
    port = 12345  # The same port as used by the server
    print("Joining...")

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
    players = int(input("How many players? "))
    if players == 2:
        if input("Host or join (H/J)? ").upper()[0] == 'H':
            start_server()
        else:
            start_client()
    else:
        Board(players)
    