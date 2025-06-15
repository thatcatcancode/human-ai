from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.chat import chat as chat_service


router = APIRouter()

class ChatMessage(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    try:
        response = await chat_service(chat_message.message)
        return { "data": response }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
