from sqlalchemy import Column, Integer, String, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

from app.schemas.tasks import TaskStatus

class Task(Base):
    __tablename__ = 'usertask'
    
    task_id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False, unique=True)    
    task_description = Column(String, nullable=False)
    task_status = Column(SAEnum(TaskStatus, default=TaskStatus.pending), nullable=False)
    
    user_id = Column(Integer, ForeignKey('usersinfo.id'))
    
    user = relationship("User", back_populates="tasks")