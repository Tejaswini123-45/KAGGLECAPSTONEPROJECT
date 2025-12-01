"""Router API - Chatbot endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from agents.router_agent_handler import process_message_with_memory
from memory import memory_manager as mem

router = APIRouter(prefix="/api/router", tags=["router"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@router.get("/progress")
async def get_progress():
    chatbot = mem.load_chatbot()
    return {
        "current_question": chatbot.get("current", 0),
        "total_questions": 10,
        "complete": mem.is_complete(),
        "answers": chatbot.get("answers", {})
    }

@router.get("/summary")
async def get_summary():
    return {
        "summary": mem.get_summary(),
        "complete": mem.is_complete(),
        "answers": mem.get_answers()
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = process_message_with_memory(request.message)
        return ChatResponse(response=response, status="success")
    except Exception as e:
        return ChatResponse(response=f"Error: {e}", status="error")
