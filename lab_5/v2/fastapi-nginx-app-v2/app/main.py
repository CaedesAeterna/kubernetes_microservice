from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import aiosqlite
from pathlib import Path

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./data/tasks.db"
SYNC_DATABASE_URL = "sqlite:///./data/tasks.db"

# Create data directory
Path("./data").mkdir(exist_ok=True)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Models
class TaskDB(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String(20), default="medium")  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

class Task(TaskBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Task Manager API", version="2.0.0")
templates = Jinja2Templates(directory="templates")

# CRUD Operations
class TaskCRUD:
    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> TaskDB:
        db_task = TaskDB(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[TaskDB]:
        return db.query(TaskDB).filter(TaskDB.id == task_id).first()
    
    @staticmethod
    def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[TaskDB]:
        return db.query(TaskDB).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[TaskDB]:
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if db_task:
            update_data = task_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)
            db_task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if db_task:
            db.delete(db_task)
            db.commit()
            return True
        return False

# API Endpoints
@app.get("/", response_class=HTMLResponse)
def read_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        tasks = TaskCRUD.get_tasks(db)
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request, "tasks": tasks, "title": "Task Manager Dashboard"}
        )
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        # Return dashboard with empty tasks list in case of error
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request, "tasks": [], "title": "Task Manager Dashboard"}
        )

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "task-manager", "version": "2.0.0"}

# CRUD API Endpoints
@app.post("/api/tasks", response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        db_task = TaskCRUD.create_task(db, task)
        return db_task
    except Exception as e:
        print(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")

@app.get("/api/tasks", response_model=List[Task])
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        tasks = TaskCRUD.get_tasks(db, skip=skip, limit=limit)
        return tasks
    except Exception as e:
        print(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")

@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = TaskCRUD.get_task(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task")

@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    try:
        task = TaskCRUD.update_task(db, task_id, task_update)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        success = TaskCRUD.delete_task(db, task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")

# Web Form Endpoints (for dashboard)
@app.post("/tasks/create")
def create_task_form(
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    db: Session = Depends(get_db)
):
    task_data = TaskCreate(title=title, description=description, priority=priority)
    TaskCRUD.create_task(db, task_data)
    return {"message": "Task created successfully"}

@app.post("/tasks/{task_id}/toggle")
def toggle_task_completion(task_id: int, db: Session = Depends(get_db)):
    task = TaskCRUD.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = TaskUpdate(completed=not task.completed)
    TaskCRUD.update_task(db, task_id, update_data)
    return {"message": "Task updated successfully"}

@app.post("/tasks/{task_id}/delete")
def delete_task_form(task_id: int, db: Session = Depends(get_db)):
    success = TaskCRUD.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
