import socket
import multiprocessing
import threading
import time
import random
from multiprocessing import Lock, Condition


class FileCoordinator:
    """Coordinates read and write operations on a shared file with priority for writes."""

    def __init__(self, file_path: str = "shared_file.txt"):
        self.file_path = file_path
        self.write_lock = Lock()
        self.write_count = 0
        self.read_ready = Condition(Lock())

    def write_to_file(self):
        with self.write_lock:
            self.write_count += 1

        sleep_duration = random.randint(1, 7)
        time.sleep(sleep_duration)

        with open(self.file_path, "a") as f:
            data = f"Writing data at {time.ctime()}\n"
            f.write(data)
            print("Write completed:", data)

        with self.write_lock:
            self.write_count -= 1
            if self.write_count == 0:
                with self.read_ready:
                    self.read_ready.notify_all()

    def read_from_file(self):
        with self.read_ready:
            self.read_ready.wait_for(lambda: self.write_count == 0)

        with open(self.file_path, "r") as f:
            data = f.read()
        print("Read completed.")

        return data


class ClientHandler:
    """Handles each client connection and processes their requests."""

    def __init__(self, connection, address, file_coordinator):
        self.connection = connection
        self.address = address
        self.file_coordinator = file_coordinator

    def handle(self):
        print(f"Client {self.address} connected.")
        try:
            while True:
                message = self.connection.recv(1024).decode('utf-8')
                if not message:
                    break

                command = message.strip().lower()
                if command == "write":
                    thread = threading.Thread(target=self.file_coordinator.write_to_file)
                    thread.start()
                    thread.join()
                elif command == "read":
                    thread = threading.Thread(target=self.send_read_result)
                    thread.start()
                    thread.join()
                else:
                    print("Invalid command received.")
        finally:
            self.connection.close()
            print(f"Client {self.address} disconnected.")

    def send_read_result(self):
        data = self.file_coordinator.read_from_file()
        self.connection.sendall(data.encode('utf-8'))


class FileServiceServer:
    """Sets up a TCP server to manage client connections and coordinate file operations."""

    def __init__(self, host: str = "localhost", port: int = "2003", file_path: str = "shared_file.txt"):
        self.host = host
        self.port = port
        self.file_coordinator = FileCoordinator(file_path)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server started, listening on {self.host}:{self.port}...")

            while True:
                connection, address = self.server_socket.accept()
                client_process = multiprocessing.Process(target=self.handle_client, args=(connection, address))
                client_process.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()

    def handle_client(self, connection, address):
        client_handler = ClientHandler(connection, address, self.file_coordinator)
        client_handler.handle()


if __name__ == "__main__":
    server = FileServiceServer("localhost", 8080, "shared_file.txt")
    server.start()
