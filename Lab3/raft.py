import json
import random
import time
import threading
import uuid
from enum import Enum
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Dict, List

import uvicorn
from fastapi import FastAPI

from Lab2.car_router import CarRouter
from Lab2.db import Base, engine


class NodeState(Enum):
    FOLLOWER = 0
    CANDIDATE = 1
    LEADER = 2


class RaftNode:
    def __init__(self, host: str,  port_number: int, manager_port: int, peer_ports: List[int]):
        self.node_id = uuid.uuid4()

        # Raft specific information
        self.state = NodeState.FOLLOWER
        self._election_timeout = self.generate_timeout()
        self._heartbeat_timeout = 2
        self.term = 0

        # UDP specific information
        self.host = host
        self.port = 3000 + port_number
        print(f"{self.term}| Node({self.port}): Election timeout: {self._election_timeout}")

        # Heartbeat socket
        self._socket = socket(AF_INET, SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        self._socket.settimeout(self._heartbeat_timeout / 2)

        # Heartbeat specific information
        self._heartbeat_thread = None
        self._last_heartbeat = time.time()

        # Peer node information
        self._node_ports: List[int] = peer_ports

        # Election specific information
        self._max_votes = len(peer_ports)
        self._votes = 0
        self._voted = None
        self._election_start = None

        # For continuous running
        self._stop = False

        # API integration
        self._manager_port = manager_port
        self.api_port = 8000 + port_number
        self._api_thread = None
        self._api_router = CarRouter

    def generate_timeout(self):
        return random.randint(5, 10)

    def socket_receive(self):
        print(f"{self.term}| Node({self.port}): Starting to receive heartbeats.")
        while not self._stop:
            try:
                data, addr = self._socket.recvfrom(1024)
                data = json.loads(data.decode())

                if data["type"] == "heartbeat":
                    self.handle_heartbeats(addr)

                elif data["type"] == "election request":
                    self.handle_election_request(data, addr)

                elif data["type"] == "vote":
                    self.handle_votes(data, addr)

                elif data["type"] == "election result":
                    self.handle_election_result(data, addr)

            except TimeoutError:
                if (time.time() - self._last_heartbeat > self._election_timeout
                        and self.state == NodeState.FOLLOWER
                        and self._election_start is None):
                    print(f"{self.term}| Node({self.port}): Leader is dead. Starting election.")
                    self.update_manager()
                    self.term += 1
                    self.state = NodeState.CANDIDATE
                    self.send_election_request()
                    self._election_start = time.time()
                    self._votes += 1
                    self.update_manager()
                elif (self._election_start is not None and
                      time.time() - self._election_start > self._election_timeout
                      and self.state == NodeState.CANDIDATE):
                    if self._votes > self._max_votes / 2:
                        print(f"{self.term}| Node({self.port}): Won the election for term {self.term} with {self._votes} votes.")
                        self.state = NodeState.LEADER
                        self._election_start = None
                        self._votes = 0
                        self._voted = None
                        self._election_timeout = self.generate_timeout()
                        self.send_election_result(True)
                        self.update_manager()
                        break        # Exit the loop to start sending heartbeats
                    else:
                        print(f"{self.term}| Node({self.port}): Lost the election with {self._votes} votes.")
                        self.state = NodeState.FOLLOWER
                        self._election_start = None
                        self._votes = 0
                        self._voted = None
                        self._election_timeout = self.generate_timeout()
                        self.send_election_result(False)

    def send_heartbeats(self):
        data = {
            "type": "heartbeat",
        }
        while True:
            for port in self._node_ports:
                self._socket.sendto(json.dumps(data).encode(), (self.host, port))
                print(f"{self.term}| Node({self.port}) Sent heartbeat to {port}.")
            time.sleep(self._heartbeat_timeout)

    def handle_heartbeats(self, addr):
        print(f"{self.term}| Node({self.port}): Received heartbeat from {addr[1]}.")
        self._last_heartbeat = time.time()

    def send_election_request(self):
        data = {
            "type": "election request",
            "term": self.term,
            "port": self.port
        }
        for port in self._node_ports:
            self._socket.sendto(json.dumps(data).encode(), (self.host, port))
            print(f"{self.term}| Node({self.port}) Sent election request to {port}.")

    def handle_election_request(self, data, addr):
        print(f"{self.term}| Node({self.port}): Received election request from {addr[1]}.")
        self._election_start = time.time()
        self._election_timeout = self.generate_timeout()

        if data["term"] < self.term:
            print(f"{self.term}| Node({self.port}): Rejecting election request from {addr[1]}.")
            self.send_vote_reject(data["port"])
            self._election_start = None
        elif self._voted is None:
            print(f"{self.term}| Node({self.port}): Voting for {addr[1]}")
            self.send_vote(data["port"])
            self._voted = data["port"]

    def send_vote(self, port: int):
        data = {
            "type": "vote",
            "vote": True
        }
        self._socket.sendto(json.dumps(data).encode(), (self.host, port))

    def send_vote_reject(self, port: int):
        data = {
            "type": "vote",
            "vote": False
        }
        self._socket.sendto(json.dumps(data).encode(), (self.host, port))

    def send_election_result(self, result: bool):
        data = {
            "type": "election result",
            "result": result,
            "term": self.term,
            "port": self.port
        }
        for port in self._node_ports:
            self._socket.sendto(json.dumps(data).encode(), (self.host, port))
            print(f"{self.term}| Node({self.port}) Sent election result to {port}.")

    def handle_election_result(self, data, addr):
        if data["result"]:
            self.update_term(data["term"], data["port"])
            self.state = NodeState.FOLLOWER
            self._election_timeout = self.generate_timeout()
            self._votes = 0
            self._election_start = None
        else:
            print(f"{self.term}| Node({self.port}): Received election failure from {addr[1]}. Continuing as follower.")

    def update_term(self, term: int, port: int):
        print(f"{term}| Node({self.port}): Received election success from {port}. Updating term to {term}.")
        self.term = term
        self._votes = 0
        self._voted = None
        self._election_start = None
        self.state = NodeState.FOLLOWER
        self._election_timeout = self.generate_timeout()

    def handle_votes(self, data, addr):
        if data["vote"]:
            self._votes += 1
            self._voted = self.port
            print(f"{self.term}| Node({self.port}): Received vote from {addr[1]}, total votes: {self._votes}.")
        else:
            print(f"{self.term}| Node({self.port}): Received rejection from {addr[1]}.")
            self._votes = 0
            self.term -= 1
            self._election_start = None
            self._voted = None
            self.state = NodeState.FOLLOWER
            self._election_timeout = self.generate_timeout()

    def init_socket_thread(self):
        if self.state == NodeState.LEADER:
            self._heartbeat_thread = threading.Thread(target=self.send_heartbeats, daemon=True)
        elif self.state == NodeState.FOLLOWER:
            self._heartbeat_thread = threading.Thread(target=self.socket_receive, daemon=True)

    def update_manager(self):
        data = {
            "state": self.state == NodeState.LEADER,
            "port": self.api_port
        }
        self._socket.sendto(json.dumps(data).encode(), (self.host, self._manager_port))

    def start_app(self):
        Base.metadata.create_all(engine)
        app = FastAPI()
        app.include_router(self._api_router)
        uvicorn.run(app, host=self.host, port=self.api_port)

    def run(self):
        self._api_thread = threading.Thread(target=self.start_app, daemon=True)
        self._api_thread.start()
        while not self._stop:
            try:
                print(f"{self.term}| Node({self.port}): Starting node...")
                self.init_socket_thread()

                self._heartbeat_thread.start()

                while self._heartbeat_thread.is_alive() and self._api_thread.is_alive():
                    self._heartbeat_thread.join(timeout=0.5)
                    self._api_thread.join(timeout=0.5)

            except KeyboardInterrupt:
                self._stop = True
                self._socket.close()
                print(f"Node({self.port}): Shutting down...")
            except Exception as e:
                print(f"Node({self.port}): Error: {e}")
