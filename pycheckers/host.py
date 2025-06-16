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
"""
import pickle
import socket

from pycheckers.checkers import Board, PlayerColor


# The port number that the host should listen on
PORT = 22222


def get_local_ip() -> tuple[str, str]:
    """
    Determine and return the localhost's public IP address as a string by
    momentarily connecting to Google's DNS server. If there is an error
    connecting, return the empty string.
    """
    hostname = socket.gethostname()
    try:
        # Create a socket and connect to an external service (e.g., Google's DNS server)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip, hostname
    except OSError:
        return "", hostname


def send_move(conn: socket.socket, board: Board, color: PlayerColor) -> bool:
    """
    Allow a player to select a move and send it to the other player. If the
    game ends as the result of the move, return True. is_black specifies which
    player is moving.
    """
    # Make a move
    player = board.get_player(color)
    move = player.take_turn()

    # Serialize and send move to the client
    packet = pickle.dumps(move)
    conn.sendall(packet)

    if move == "loss":
        print("You lost...")
        return True

    return False


def recv_move(conn: socket.socket, board: Board, color: PlayerColor) -> bool:
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
        player = board.get_player(color).opponent

        if piece := player.get_piece(from_tile):
            piece.do_move(move)
        else:
            raise Exception("Received an invalid move from the opponent.")

        return False
    except ValueError:
        print("You won!")
        return True


def start_server(ip="127.0.0.1", host="localhost", color=PlayerColor.BLACK):
    """
    Host a checkers game as the given IP address or hostname.

    Accept the first request to connect. The host plays as black and goes
    first. Alternate sending moves back and forth over the network connection
    until someone wins the game. Then terminate the connection.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, PORT))
        s.listen(1)
        print(f"Your IP address is {ip} ({host})")
        print("Waiting for someone to join...")
        conn, addr = s.accept()

        with conn:
            print("Connected to", addr)

            # Set up game
            board = Board()

            while not (send_move(conn, board, color) or recv_move(conn, board, color)):
                pass


def start_client(host="localhost", color=PlayerColor.RED) -> bool:
    """
    Join the checkers game hosted at the given IP address or hostname.

    A bad request to connect will timeout after 10 seconds. The joiner plays as
    red and goes second. Alternate sending moves back and forth over the
    network connection until someone wins the game. Then terminate the
    connection.
    """
    print(f"Joining {host}...")

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

        while not (recv_move(s, board, color) or send_move(s, board, color)):
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

    match players:
        case 2:
            # Multiplayer
            while True:
                if hj := input("Host or join (H/J)? ").upper():

                    if hj[0] == "H":
                        # Host
                        my_ip, my_name = get_local_ip()
                        if my_ip:
                            start_server(my_ip, my_name)
                            break
                        else:
                            print("Error fetching local IP address.")

                    elif hj[0] == "J":
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
        case 1:
            board = Board(players)
            winner = board.play_one()
            print(f"{winner.capitalize()} player won.")
        case 0:
            games = int(input("How many sims? "))
            board = Board(players)
            if games > 1:
                counts = board.play(games)
                print(counts)
            else:
                winner = board.play_one()
                print(f"{winner.capitalize()} player won.")


if __name__ == "__main__":
    main()
