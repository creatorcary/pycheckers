# server.py
import socket
import pickle


def start_server():
    host = 'localhost'  # Host IP
    port = 12345  # Use a non-privileged port number

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()

        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            obj = pickle.loads(data)  # Convert bytes back to object
            print('Received object:', obj)

            # Send a response back to the client
            response_obj = {"response": "Received your object!"}
            response_data = pickle.dumps(response_obj)
            conn.sendall(response_data)


if __name__ == "__main__":
    start_server()