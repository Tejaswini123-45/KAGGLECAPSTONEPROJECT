"""
FastAPI server for the AI Company Builder.

A smart chatbot router that uses Google Gemini API to help founders.

Exposes:
- GET / — Chatbot UI (chatbot.html)
- POST /chat — Send a message, get intelligent response from Router Agent (powered by Gemini)

Setup:
  1. Install google-generativeai: pip install google-generativeai
  2. Get API key from: https://ai.google.dev/
  3. Set GEMINI_API_KEY in .env file
  4. Run: python main.py server
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.router_agent import router_agent
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Company Builder",
    description="An AI-powered system to build everything for your business idea.",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    status: str = "success"


@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the chatbot HTML interface."""
    chatbot_path = Path(__file__).parent / "chatbot.html"
    try:
        with open(chatbot_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Chatbot UI not found</h1>"


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the Smart Router Agent (powered by Gemini).
    
    The router will:
    - Guide through 10-question onboarding (if not complete)
    - Understand your business idea
    - Store answers in long-term memory
    - Provide personalized recommendations using stored memory
    - Route to specialized teams when needed
    
    Special commands:
    - "show my answers" - Review your business blueprint
    - "update [field]" - Update any stored information
    - "reset onboarding" - Start onboarding over
    
    Args:
        request: ChatRequest with your message
    
    Returns:
        ChatResponse with the router agent's intelligent response
    """
    try:
        message = request.message.strip()
        if not message:
            return ChatResponse(
                response="Please share your business idea or question. I'm here to help!",
                status="error",
            )

        # Use memory-aware handler for Router Agent
        from agents.router_agent_handler import get_agent_response
        
        # Debug logging for special commands
        if message.strip() == "__CHECK_ONBOARDING__":
            print("[DEBUG] Received __CHECK_ONBOARDING__ command")
        
        response = get_agent_response(message)

        return ChatResponse(
            response=response,
            status="success",
        )
    except Exception as e:
        error_msg = str(e)
        if "GEMINI_API_KEY" in error_msg:
            return ChatResponse(
                response="⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in .env file. Get one at https://ai.google.dev/",
                status="error",
            )
        return ChatResponse(
            response=f"Error processing request: {error_msg}",
            status="error",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)