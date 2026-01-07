from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.model.user import User
from app.db.dependency import get_db
from app.schemas.users import RegistorUsers, LoginUser, ChangePassword, ForgetPassword, VerifyOTP
from app.core.auth import create_token, get_current_user, hashed_password, verify_password, gen_otp, required_role

SECRET_KEY = "This is my secret key"
ALGORITHM = "HS256"


router = APIRouter()

# register user
@router.post("/register")
def register(user: RegistorUsers, db: Session = Depends(get_db)):
    
    # fitch data from the database check is user already exist
    user_exist = db.query(User).filter(User.email == user.email).first()
    
    if user_exist:
        raise HTTPException(status_code=400, detail='User already exist in database')

    # insert data into table
    new_user = User(
       username = user.username,
        email = user.email,
        password = hashed_password(user.password),
        role = "user"
    )
    
    # add user record into table
    db.add(new_user)
    
    
    # save data
    db.commit()
    
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "name": new_user.username}



# User login
@router.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):

    # fitch data from the database
    user_db = db.query(User).filter(User.email == user.email).first()

    # verify password 
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    
    payload = {
        'email': user_db.email,
        'user_id': user_db.id,
        'username': user_db.username,
        'role': user_db.role,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    access_token = create_token(data=payload)
   

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.get('/profile')
def profile(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "role": current_user["role"]
    }




# user change password
@router.post('/change')
def change_password(user: ChangePassword, db: Session = Depends(get_db)):

    # fitch data from database
    user_db = db.query(User).filter(User.email == user.email).first()

    # checking for password verification
    if user_db:
        if not verify_password(user.old_password, user_db.password):
            raise HTTPException(status_code=401, detail='Old password is incorrect')
        
        # make new password hashed
        user_db.password = hashed_password(user.new_password)
        
        # save update in database
        db.commit()
        
        return {"message": "Password changed successfully"}
    
    raise HTTPException(status_code=404, detail='User not found')
        
    

            
# user forget password
@router.post('/forget')
def forget_password(user: ForgetPassword, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if not existing_user:
        raise HTTPException(status_code=404, detail='User not found from database')
    
    otp = gen_otp()
    
    
    # assign otp to existing user
    existing_user.otp = otp
    
    db.commit()
    
    return {
        "message": "OTP sent successfully",
        "OTP": existing_user.otp
    }
    



# verify otp
@router.post('/verify-otp')
def verify_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == data.email).first()
    
    if not existing_user:
        raise HTTPException(status_code=404, detail='User not found from database')
    
    if not existing_user.otp:
        raise HTTPException(status_code=400, detail='No OTP request found')
    
    if data.otp != existing_user.otp:
        raise HTTPException(status_code=401, detail='Invalid OTP')
    
    existing_user.password = hashed_password(data.new_password)
    
    existing_user.otp = None
    
    db.commit()
    
    return {
        "message": "OTP verified and password reset successfully"
    }
