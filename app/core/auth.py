import os
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import bcrypt
from random import randint
from dotenv import load_dotenv

from app.db.dependency import get_db

# load env FIRST
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_HOURS = 1

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in .env")


# it used to get the token from the request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") 
http_bearer = HTTPBearer()

def create_token(data: dict):
    to_encode = data.copy()
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token




# it used to get the current user from the token
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("email")
        username = payload.get("username")
        role = payload.get("role")
        
        if email is None or user_id is None or username is None or role is None:
            raise credentials_exception
        
        return {
            "user_id": user_id,
            "email": email,
            "username": username,
            "role": role
        }
    
    except JWTError:
        raise credentials_exception
    




def hashed_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode("utf-8"),
        bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            hashed.encode("utf-8"))
    except Exception as exp:
        return exp


def required_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user['role'] != required_role:
            raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied"
                )
        return current_user
    return role_checker
    



def gen_otp():
    otp = randint(100000, 999999)
    return otp
