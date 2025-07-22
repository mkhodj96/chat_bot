import asyncio
import json
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .composition import bot
from .config import config
from .data_mcp_server import mcp

app = FastAPI()
templates = Jinja2Templates(directory="chat_bot/templates")
app.mount("/static", StaticFiles(directory="chat_bot/static"), name="static")


@app.on_event("startup")
async def startup_combined() -> None:
    def run_mcp() -> None:
        asyncio.run(mcp.run_sse_async())
    threading.Thread(target=run_mcp, daemon=True).start()
    await asyncio.sleep(1)
    await bot.initialize()


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chatbot")
async def chatbot_message(message: str = "Hello", session_id: str = "default") -> str:
    return await bot.run_query(message, session_id)


@app.get("/conversations")
async def list_conversations() -> dict:
    files = [f.stem for f in Path(config.CONV_DIR).iterdir() if f.name.endswith(".json")]
    return {"conversations": files}


@app.post("/save_conversation")
async def save_conversation(request: Request) -> dict:
    data = await request.json()
    conv_id = str(uuid.uuid4())
    file_path = Path(config.CONV_DIR) / f"{conv_id}.json"
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": conv_id}


@app.get("/conversations/{conv_id}", response_model=None)
async def get_conversation(conv_id: str) -> JSONResponse | dict:
    file_path = Path(config.CONV_DIR) / f"{conv_id}.json"
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "Conversation not found"})
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return {"messages": data}


@app.delete("/conversations/{conv_id}", response_model=None)
async def delete_conversation(conv_id: str) -> dict:
    file_path = Path(config.CONV_DIR) / f"{conv_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Conversation not found")
    file_path.unlink()
    return {"message": "Conversation deleted"}
