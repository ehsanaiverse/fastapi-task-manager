from fastapi import WebSocket, WebSocketDisconnect,APIRouter
from fastapi.responses import HTMLResponse

from app.notification.manager import manager

router = APIRouter()


@router.get("/")
async def get():
    return HTMLResponse()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)