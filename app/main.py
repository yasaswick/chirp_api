from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from .dependency.dependencies import  get_db
import json
from .router import user_router
from .controller import user_controller

#fast api instance
app = FastAPI(
        title="Chirp Api - Equiwatt Test"
)

#connection manager class to handle connection states
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

#connection manager instantiation
manager = ConnectionManager()


#web sockets
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            jsondata = json.loads(data)
            await manager.broadcast(data)
            

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


#routers
app.include_router(user_router.router)