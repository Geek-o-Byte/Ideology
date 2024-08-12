from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import uuid
from models import Idea, SessionLocal, init_db
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

# Инициализация базы данных
init_db()

app = FastAPI()

# Настройка шаблонизатора Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_ideas(request: Request, db: Session = Depends(get_db)):
    ideas = db.query(Idea).all()
    template = env.get_template("index.html")
    return template.render(request=request, ideas=ideas)

@app.post("/add", response_class=RedirectResponse)
async def add_idea(title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    new_idea = Idea(uuid=str(uuid.uuid4()), title=title, description=description)
    db.add(new_idea)
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/like/{idea_uuid}", response_class=RedirectResponse)
async def like_idea(idea_uuid: str, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.uuid == idea_uuid).first()
    if idea:
        idea.likes += 1
        db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/idea/{idea_uuid}", response_class=HTMLResponse)
async def read_idea(request: Request, idea_uuid: str, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.uuid == idea_uuid).first()
    if not idea:
        return RedirectResponse("/", status_code=303)
    template = env.get_template("idea.html")
    return template.render(request=request, idea=idea)
