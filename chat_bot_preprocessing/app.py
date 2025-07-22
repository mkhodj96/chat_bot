import threading

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .composition import run_pipeline

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="chat_bot_preprocessing/static"),
    name="static"
)
templates = Jinja2Templates(directory="chat_bot_preprocessing/templates")


@app.on_event("startup")
async def startup_event() -> None:
    app.state.is_done = False


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/start")
async def start() -> dict:
    app.state.is_done = False
    threading.Thread(target=run_pipeline_and_set_flag, args=(app,)).start()
    return {"started": True}


@app.get("/status")
async def status() -> dict:
    return {"done": app.state.is_done}


def run_pipeline_and_set_flag(app_instance: FastAPI) -> None:
    run_pipeline()
    app_instance.state.is_done = True
