from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.openai_service import openai_service
from models.schemas import ChatRequest
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Эндпоинт для потокового чата с OpenAI
    """
    try:
        async def event_generator():
            full_response = ""
            async for chunk in openai_service.stream_completion(
                messages=[msg.dict() for msg in request.messages],
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            ):
                full_response += chunk
                # Отправляем данные в формате SSE
                yield f"data: {json.dumps({'content': chunk,
                                           'is_final': False})}\n\n"
            
            # Отправляем финальное сообщение
            yield f"data: {json.dumps({'content': '', 'is_final': True})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/normal")
async def chat_normal(request: ChatRequest):
    """
    Эндпоинт для обычного (не потокового) чата
    """
    try:
        response = await openai_service.get_non_streaming_response(
            messages=[msg.dict() for msg in request.messages],
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Проверка здоровья сервиса
    """
    return {"status": "healthy", "service": "OpenAI Chat API"}