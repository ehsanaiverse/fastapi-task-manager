from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import  Session

from app.db.dependency import get_db
from app.model.task import Task
from app.model.notification import Notification
from app.core.auth import required_role
from app.schemas.tasks import UpdateTask, CreateTask
from app.notification.manager import manager

router = APIRouter()


VALID_STATUS = {'pending', 'completed'}

@router.post('/create')
async def create_task(task: CreateTask,
                db: Session = Depends(get_db),
                current_user: dict = Depends(required_role('admin'))
):
    
    existing_task = db.query(Task).filter(Task.task_name == task.task_name).first() 
    
    if existing_task:
        raise HTTPException(status_code=400, detail="Task already exist")
    
    status = task.task_status.lower().strip()
    if status not in VALID_STATUS:
        raise HTTPException(status_code=400, detail="task_status must be pending or completed")
    
    new_task = Task(
        task_name = task.task_name,
        task_description = task.task_description,
        task_status = task.task_status,
        user_id = current_user["user_id"]
        
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    
    notification_meassage = Notification(
        user_id = current_user["user_id"],
        message = "New task created by admin"
    )
    
    db.add(notification_meassage)
    db.commit()
    db.refresh(notification_meassage)
    
    await manager.send_to_user(
        user_id=current_user["user_id"],
        message="Task created"
    )
    
    
    return {
        "message": "Admin created task successfully ",
        "task_id": new_task.task_id,
        "user_id": current_user["user_id"]
    }


@router.get('/view-task')
def admin_view_task(db: Session = Depends(get_db),
              current_user: dict = Depends(required_role('admin'))
):
    
    tasks = db.query(Task).all()
    
    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
     # Convert to list of dictionaries for JSON serialization
    return [
        {
            'id': task.task_id,
            'task_name': task.task_name,
            'task_description': task.task_description,
            'task_status': task.task_status
        }
        for task in tasks
    ]


@router.put("/update-task/{task_id}")
async def admin_update_task(
    task_id: int,
    up_task: UpdateTask,
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role("admin"))
):
    task = db.query(Task).filter(Task.task_id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = up_task.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided")

    if "task_name" in update_data:
        existing_task = db.query(Task).filter(
            Task.task_name == update_data["task_name"],
            Task.task_id != task_id
        ).first()

        if existing_task:
            raise HTTPException(
                status_code=400,
                detail="Task name already exists"
            )

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    notification_message = Notification(
        user_id=task.user_id,
        message="Task updated"
    )

    db.add(notification_message)
    db.commit()

    await manager.send_to_user(
        user_id=task.user_id,
        message="Task updated successfully"
    )

    return {"message": "Task updated"}



@router.delete('/task/{task_id}')
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted"}