import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Demo App", version="1.0.0")


class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


# In-memory storage. Replace with a DB for real use.
_tasks: list[Task] = []
_next_id = 1


@app.get("/api/health")
def health():
    return {"status": "ok", "version": app.version}


@app.get("/api/tasks")
def list_tasks() -> list[Task]:
    return _tasks


@app.post("/api/tasks", status_code=201)
def create_task(payload: TaskIn) -> Task:
    global _next_id
    task = Task(id=_next_id, title=payload.title.strip())
    _next_id += 1
    _tasks.append(task)
    return task


@app.post("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int) -> Task:
    for task in _tasks:
        if task.id == task_id:
            task.done = not task.done
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    global _tasks
    before = len(_tasks)
    _tasks = [t for t in _tasks if t.id != task_id]
    if len(_tasks) == before:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
