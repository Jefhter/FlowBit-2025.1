from typing import List, Optional
import os
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import *
from logger import LoggerFactory
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.getenv('STATIC_DIR', os.path.join(BASE_DIR, "static"))
TEMPLATES_DIR = os.getenv('TEMPLATE_DIR', os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
logger = LoggerFactory.getLogger('server')
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"📥 Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"❌ Error: {e}", stack_info=True)
        raise e
    
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "dark_mode": os.getenv("DEFAULT_DARK_MODE", "false") == "true", 
    })

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))

@app.get("/tasks", response_model=List[TaskOut])
def list_tasks(done: Optional[str] = Query(None), db: Session = Depends(engine)):
    query = db.query(Task)

    if done in ("true", "false"):
        done_bool = done == "true"
        query = query.filter(Task.done.is_(done_bool))

    tasks = query.all()
    return tasks

# ➡️ Criar nova tarefa
@app.post("/tasks", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(engine)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ➡️ Atualizar tarefa existente
@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(engine)):
    db_task = db.query(Task).get(task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in task.dict(exclude_unset=True).items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task

# ➡️ Deletar tarefa
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(engine)):
    db_task = db.query(Task).get(task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}