from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.model.task import Task
from app.db.dependency import get_db
from app.schemas.tasks import CreateTask, UpdateTask
from app.core.auth import get_current_user, required_role
from app.notification.manager import manager


router = APIRouter()

VALID_STATUS = {'pending', 'completed'}

@router.post('/create')
async def create_task(task: CreateTask,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    
    existing_task = db.query(Task).filter(Task.task_name == task.task_name).first() 
    
    if existing_task:
        raise HTTPException(status_code=400, detail="Task already exist")
    
    status = task.task_status.lower()
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
    
    await manager.send_to_user(
        user_id=current_user["user_id"],
        message="Task created successfully"
    )

    return {
        "message": "Task created successfully",
        "task_id": new_task.task_id,
        "user_id": current_user["user_id"]
    }




@router.get('/view')
def view_task(db: Session = Depends(get_db),
              current_user: dict = Depends(get_current_user)):
    
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




# update endpoint
@router.put('/update/{task_id}')
def update_task(task_id: int, task_update: UpdateTask,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    
    existing_task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if (task_update.task_status is None) and (task_update.task_status not in VALID_STATUS):
        raise HTTPException(status_code=400, detail="task_status must be pending or completed")
    
    # excluding fields that weren't provided
    update_data = task_update.model_dump(exclude_unset=True)
    # print(update_data)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provide for updata")
    
    # Update only the fields that were provided
    for field, value in update_data.items():
        setattr(existing_task, field, value)
    
    db.commit()
    db.refresh(existing_task)
    
    return {
        'message': 'Task successfully updated'}
    
    


@router.delete('/delete/{task_id}')
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    
    existing_task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(existing_task)
    
    db.commit()
    db.refresh()
    
    return {"message": "Task successfully deleted"}