import json

from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

from chat_service import ChatService

ChatRouter = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


chat_service = ChatService()


@ChatRouter.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await chat_service.connect(websocket)
    while True:
        try:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data["command"] == "send":
                await chat_service.send_message(data["message"], websocket)
            elif data["command"] == "close":
                await chat_service.disconnect(websocket)
                break
        except Exception:
            await chat_service.disconnect(websocket)
            break


@ChatRouter.get("/messages")
async def get_messages():
    return chat_service.get_all_messages()


@ChatRouter.get("", response_class=HTMLResponse)
async def get_chat():
    with open("chat.html") as f:
        return f.read()
