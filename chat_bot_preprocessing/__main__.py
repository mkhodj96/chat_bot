import uvicorn

uvicorn.run("chat_bot_preprocessing.app:app", host="127.0.0.1", port=8000, reload=True)
