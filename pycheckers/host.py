"""
host.py
Author: Logan Cary

This file is the entry point for hosting a game of checkers.
When executed, it will allow the user to enter the number of players.

Number of players:
 0 - simulation
 1 - single-player (PvE)
 2 - multiplayer (PvP)

If multiplayer is selected, the user will be asked to either host or join. If
hosting, the user's public IP address is displayed so that the person joining
can copy it when they select join.

Globals
-------
PORT

Functions
---------
get_local_ip()
send_move()
recv_move()
start_server()
start_client()
main()

"""

import pickle
import socket

from pycheckers.checkers import Board


# The port number that the host should listen on
PORT = 22222


def get_local_ip() -> tuple[str, str]:
    """
    Determine and return the localhost's public IP address as a string by
    momentarily connecting to Google's DNS server. If there is an error
    connecting, return the empty string.
    """
    hn = socket.gethostname()
    try:
        # Create a socket and connect to an external service (e.g., Google's DNS server)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip, hn
    except OSError:
        return "", hn


def send_move(conn: socket.socket, board: Board, is_black=True) -> bool:
    """
    Allow a player to select a move and send it to the other player. If the
    game ends as the result of the move, return True. is_black specifies which
    player is moving.
    """
    # Make a move
    player = board._blackPlayer if is_black else board._redPlayer
    move = player.takeTurn(board)

    # Serialize and send move to the client
    packet = pickle.dumps(move)
    conn.sendall(packet)

    if move == "loss":
        print("You lost...")
        return True

    return False


def recv_move(conn: socket.socket, board: Board, is_black=True) -> bool:
    """
    Wait to receive a move from the other player, then update the board
    accordingly. If the game ends as the result of the move, return True.
    is_black specifies which player is moving.
    """
    # Wait for a move from the client
    packet = conn.recv(1024)
    try:
        from_tile, move = pickle.loads(packet)

        # Update the board with the opponent's move
        player = board._blackPlayer if is_black else board._redPlayer

        if piece := player.getPiece(from_tile):
            piece.doMove(board, move)
        else:
            raise Exception("Received an invalid move from the opponent.")

        return False
    except ValueError:
        print("You won!")
        return True


def start_server(ip="127.0.0.1", host="localhost"):
    """
    Host a checkers game as the given IP address or hostname.

    Accept the first request to connect. The host plays as black and goes
    first. Alternate sending moves back and forth over the network connection
    until someone wins the game. Then terminate the connection.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, PORT))
        s.listen(1)
        print("Your IP address is", ip, "("+host+")")
        print("Waiting for someone to join...")
        conn, addr = s.accept()

        with conn:
            print('Connected to', addr)

            # Set up game
            board = Board()

            while not (send_move(conn, board, is_black=True) or recv_move(conn, board, is_black=False)):
                pass


def start_client(host='localhost') -> bool:
    """
    Join the checkers game hosted at the given IP address or hostname.

    A bad request to connect will timeout after 10 seconds. The joiner plays as
    red and goes second. Alternate sending moves back and forth over the
    network connection until someone wins the game. Then terminate the
    connection.
    """
    print("Joining", host, "...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)
        try:
            s.connect((host, PORT))
        except socket.gaierror:
            print("Unknown host address.")
            return False
        except socket.timeout:
            print("Connection timed out.")
            return False
        except ConnectionRefusedError:
            print("Connection refused.")
            return False
        s.settimeout(None)  # Allow moves to take any length of time

        # Setup game
        board = Board(invert=True)

        while not (recv_move(s, board, is_black=True) or send_move(s, board, is_black=False)):
            pass

    return True  # success


def main():
    """
    Allow the user to select what kind of match to play, then set up the game.
    """
    while True:
        try:
            players = int(input("How many players? "))
            if players in range(3):
                break
            else:
                print("Enter either 0, 1, or 2.")
        except ValueError:
            print("Enter either 0, 1, or 2.")

    if players == 2:
        # Multiplayer

        while True:
            if hj := input("Host or join (H/J)? ").upper():

                if hj[0] == 'H':
                    # Host
                    myIP, myname = get_local_ip()
                    if myIP:
                        start_server(myIP, myname)
                        break
                    else:
                        print("Error fetching local IP address.")

                elif hj[0] == 'J':
                    # Join
                    while not start_client(input("Enter the host IP or hostname: ")):
                        pass
                    break

                else:
                    # Invalid option
                    print("Invalid option.")

            else:
                # Nothing entered
                print("Enter an option.")

    else:
        # Single player or sim
        Board(players)


if __name__ == "__main__":
    main()
