import json

from fastapi import WebSocket
from typing import List, Dict
from pydantic import BaseModel
from fastapi.websockets import WebSocketState


class Message(BaseModel):
    message: str
    sender: str


class ChatService:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.messages: List[Message] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections[str(websocket.client.port)] = websocket

    async def send_message(self, message: str, websocket: WebSocket):
        for connection in self.connections.values():
            message_data = Message(message=message, sender=str(websocket.client.port))
            try:
                await connection.send_text(json.dumps(message_data.dict()))
                self.messages.append(message_data)
            except Exception as e:
                print(f"Error sending message: {str(e)}")

    async def disconnect(self, websocket: WebSocket):
        self.connections.pop(str(websocket.client.port))
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()

    async def close_connections(self):
        for connection in self.connections.values():
            if connection.client_state == WebSocketState.CONNECTED:
                await connection.close()

    def get_all_messages(self) -> List[Message]:
        return self.messages
