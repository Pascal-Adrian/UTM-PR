import socket
import time
import random


class FileServiceClient:
    """Client to send commands to the FileServiceServer."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))

    def send_command(self, command):
        self.client_socket.sendall(command.encode('utf-8'))

    def read_response(self):
        data = self.client_socket.recv(4096).decode('utf-8')
        print("Data received from server:\n", data)

    def perform_random_operations(self, num_operations):
        """Perform a random sequence of read and write operations."""
        for _ in range(num_operations):
            command = random.choice(["read", "write"])
            print(f"Performing {command} operation")
            self.send_command(command)

            if command == "read":
                self.read_response()

            time.sleep(random.randint(1, 3))

    def close(self):
        self.client_socket.close()


if __name__ == "__main__":
    client = FileServiceClient("localhost", 8080)
    client.connect()

    client.perform_random_operations(num_operations=5)

    client.close()
