from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from car_router import CarRouter
from chat_router import ChatRouter
import uvicorn
from multiprocessing import Process
from db import Base, engine

Base.metadata.create_all(engine)

car_app = FastAPI()

car_app.include_router(CarRouter)

chat_app = FastAPI()

chat_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_app.include_router(ChatRouter)


def run_app1():
    uvicorn.run(car_app, host="0.0.0.0", port=8000)


def run_app2():
    uvicorn.run(chat_app, host="0.0.0.0", port=8001)


def main():
    http_server_process = Process(target=run_app1)
    websocket_server_process = Process(target=run_app2)

    http_server_process.start()
    websocket_server_process.start()

    try:
        while http_server_process.is_alive() and websocket_server_process.is_alive():
            http_server_process.join(timeout=0.5)
            websocket_server_process.join(timeout=0.5)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        http_server_process.terminate()
        websocket_server_process.terminate()


if __name__ == "__main__":
    main()
