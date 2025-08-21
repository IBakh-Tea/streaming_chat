from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes import chat
import os

app = FastAPI(
    title="OpenAI Streaming API",
    description="API для потокового чата с OpenAI",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем роуты
app.include_router(chat.router)

@app.get("/")
async def serve_frontend():
    """Обслуживание фронтенд приложения"""
    return FileResponse("app/static/index.html")

@app.get("/api/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "OpenAI Streaming API", 
        "version": "1.0.0",
        "endpoints": {
            "stream_chat": "/api/chat/stream",
            "normal_chat": "/api/chat/normal",
            "health": "/api/chat/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 8000))
    )