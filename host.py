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
            data = board._blackPlayer.takeTurn(board)
            print(data)
            
            """
            data = conn.recv(1024)
            obj = pickle.loads(data)  # Convert bytes back to object
            print('Received object:', obj)
"""
            # Send a response back to the client
            #response_obj = {"response": "Received your object!"}
            response_data = pickle.dumps(data)
            conn.sendall(response_data)

            input()
            


if __name__ == "__main__":
    start_server()

###