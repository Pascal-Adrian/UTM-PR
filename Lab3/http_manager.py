import json
import threading
from datetime import time
from socket import socket, AF_INET, SOCK_DGRAM

import pika
import requests
from pika.exceptions import StreamLostError


class HTTPManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.current_leader = None
        self._socket = socket(AF_INET, SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        self._socket_thread = None
        self._rabbitmq_thread = None
        self._rabbitmq_host = None
        self._connection = None
        self._channel = None
        self._consuming = False
        self._stop_event = threading.Event()

    def process_socket_data(self):
        data, addr = self._socket.recvfrom(1024)
        data = json.loads(data.decode())
        if data["state"]:
            print(f"HTTP Manager: Received port {data['port']} as the current leader.")
            self.current_leader = data["port"]
        else:
            print(f"HTTP Manager: No current leader.")
            self.current_leader = None

    def socket_receive(self):
        print(f"HTTP Manager: Starting to receive port data.")
        while True:
            self.process_socket_data()

    def open_rabbitmq_channel(self, queue_name: str, rabbitmq_host: str, credentials: pika.PlainCredentials):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=queue_name)
        self._channel.basic_consume(queue=queue_name, on_message_callback=self.rabbitmq_callback, auto_ack=True)

    def rabbitmq_callback(self, ch, method, properties, body):
        data = json.loads(body)
        print(f'HTTP Manager: Received car {data["manufacturer"]} {data["model"]} from RabbitMQ.')
        requests.post(f'http://localhost:{self.current_leader}/car', json=data)

    def rabbitmq_consume(self):
        print(f'HTTP Manager: Starting to consume cars.')
        while True:
            if self.current_leader is not None and not self._consuming:
                print('HTTP Manager: Reconnecting to RabbitMQ.')
                self._channel.start_consuming()
                self._consuming = True
            elif self.current_leader is None and self._consuming:
                print('HTTP Manager: No leader, stopping RabbitMQ consuming.')
                self._channel.stop_consuming()
                self._consuming = False

    def run(self, credentials: pika.PlainCredentials, queue_name, rabbitmq_host: str = 'localhost'):
        self.open_rabbitmq_channel(queue_name, rabbitmq_host, credentials)
        self._socket_thread = threading.Thread(target=self.socket_receive, daemon=True)
        self._rabbitmq_thread = threading.Thread(target=self.rabbitmq_consume, daemon=True)
        self._rabbitmq_thread.start()
        self._socket_thread.start()

        while self._socket_thread.is_alive():
            self._socket_thread.join(timeout=0.5)
            self._rabbitmq_thread.join(timeout=0.5)

    def stop(self):
        self._stop_event.set()
        self._socket.close()
        self._channel.stop_consuming()
        self._connection.close()
        if self._socket_thread.is_alive():
            self._socket_thread.join()
        if self._rabbitmq_thread.is_alive():
            self._rabbitmq_thread.join()


if __name__ == "__main__":
    manager = HTTPManager('127.0.0.1', 9000)
    try:
        manager.run(rabbitmq_host='localhost', credentials=pika.PlainCredentials('admin', 'admin'), queue_name='cars')
    except KeyboardInterrupt:
        print("\nShutting down HTTP Manager...")
        manager.stop()
        print("HTTP Manager: Shut down.")
