from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.db.database import Base, engine
from app.admin.userRoutes import router as admin_user
from app.admin.taskRoutes import router as admin_task
from app.routers.users import router as user_account
from app.routers.tasks import router as user_task
from app.admin.admin import create_default_admin

# load env FIRST
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables
    Base.metadata.create_all(bind=engine)

    # create default admin if not exists
    create_default_admin()

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_account, prefix="/users", tags=["User"])
app.include_router(user_task, prefix="/tasks", tags=["Task"])
app.include_router(admin_user, prefix="/admin", tags=["Admin-User"])
app.include_router(admin_task, prefix="/admin", tags=["Admin-Task"])
