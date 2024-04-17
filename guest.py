# client.py
import socket
import pickle


def start_client():
    host = 'localhost'  # Server's IP
    port = 12345  # The same port as used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        obj = {"key": "value"}  # Some object
        data = pickle.dumps(obj)  # Convert object to bytes
        s.sendall(data)

        # Receive a response from the server
        response_data = s.recv(1024)
        response_obj = pickle.loads(response_data)  # Convert bytes back to object
        print('Received response:', response_obj)


if __name__ == "__main__":
    start_client()