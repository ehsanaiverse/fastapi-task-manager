from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import  Session

from app.db.dependency import get_db
from app.model.user import User
from app.core.auth import required_role, hashed_password
from app.schemas.users import RegistorUsers


router = APIRouter()

@router.get('/users')
def get_all_users(db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):
    
    return db.query(User).all()



@router.get('/users/{user_id}')
def get_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="user not find")
    
    return user




@router.post("/create-user")
def admin_create_user(
    user: RegistorUsers,
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role("admin"))
):
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password(user.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created by admin"}




@router.delete("/delete-user")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role("admin"))
):
    existing_user = db.query(User).filter(User.id == user_id).first()
    
    if not existing_user:
        raise HTTPException(status_code=404, detail='user not found')
    
    db.delete(existing_user)
    db.commit()

    return {"message": "User deleted by admin"}
    





       

