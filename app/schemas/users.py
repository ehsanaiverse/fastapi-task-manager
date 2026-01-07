from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

class RegistorUsers(BaseModel):
    username: str
    email: EmailStr
    password: str
    


class LoginUser(BaseModel):
    email: Annotated[EmailStr, Field(..., description='User email')]
    password: Annotated[str, Field(..., description='User password')]
    
    
class ChangePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class ForgetPassword(BaseModel):
    email: EmailStr


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: int
    new_password: str
    
    
class Profile(BaseModel):
    id: int
    email: EmailStr
    username: str
    