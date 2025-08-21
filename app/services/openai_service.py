import os
from openai import OpenAI
from typing import AsyncGenerator
import asyncio
from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("MAX_TOKENS", 1000))
    
    async def stream_completion(
        self, 
        messages: list, 
        model: str = None, 
        max_tokens: int = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Асинхронный генератор для потокового ответа от OpenAI
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.max_tokens
        
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    await asyncio.sleep(0.01)  # Контроль скорости потока
                    
        except Exception as e:
            yield f"Ошибка: {str(e)}"
    
    async def get_non_streaming_response(
        self,
        messages: list,
        model: str = None,
        max_tokens: int = None,
        temperature: float = 0.7
    ) -> str:
        """
        Получение обычного (не потокового) ответа
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.max_tokens
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка: {str(e)}"

# Создаем экземпляр сервиса
openai_service = OpenAIService()