from fastapi import WebSocket, WebSocketDisconnect,APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.notification.manager import manager
from app.model.notification import Notification
from app.db.dependency import get_db

router = APIRouter()


@router.get('/all')
def get_all_notif(db: Session = Depends(get_db)):
    
    notification = db.query(Notification).all()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notifications not found")
    
    
    return [
        {
            'id': notif.id,
            'user_id': notif.user_id,
            'message': notif.message,
            'is_read': notif.is_read,
            'created_at': notif.created_at
        }
        for notif in notification
    ]



@router.put('/{notif_id}/read')
def mark_as_read(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        return {"error": "Notification not found"}
    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}



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