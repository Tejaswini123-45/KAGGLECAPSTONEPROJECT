"""
FastAPI backend for The Growth Hub — AI Company Builder
Frontend + Backend served from SAME server on port 8000
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from agents.router_agent_handler import get_agent_response
from memory.memory_manager import load_memory, is_onboarding_complete

app = FastAPI(
    title="The Growth Hub",
    description="AI-powered business builder using Google Gemini.",
    version="1.0.0",
)

# -------------------------------------------------------------
# CORS SETTINGS
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# MODELS
# -------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    question_index: int | None = None
    onboarding_complete: bool = False

# -------------------------------------------------------------
# SERVE CHATBOT UI
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_chatbot():
    chatbot_file = Path(__file__).parent / "chatbot.html"
    if chatbot_file.exists():
        # return FileResponse so browser loads static HTML
        return FileResponse(str(chatbot_file))
    return HTMLResponse("<h1>❌ ERROR: chatbot.html not found</h1>", status_code=404)

# -------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "message": "Growth Hub backend is running"}

# -------------------------------------------------------------
# CHAT ENDPOINT
# -------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        user_msg = request.message.strip()
        if not user_msg:
            return ChatResponse(
                response="Please enter a valid message.",
                status="error",
                question_index=load_memory().get("current_question_index", 0),
                onboarding_complete=is_onboarding_complete()
            )

        # Process with router handler which uses memory_manager internally
        bot_reply = get_agent_response(user_msg)

        mem = load_memory()
        question_index = mem.get("current_question_index", 0)
        onboard_flag = is_onboarding_complete()

        return ChatResponse(
            response=bot_reply,
            status="success",
            question_index=question_index,
            onboarding_complete=onboard_flag
        )

    except Exception as e:
        mem = load_memory()
        return ChatResponse(
            response=f"⚠️ Server error: {str(e)}",
            status="error",
            question_index=mem.get("current_question_index", 0),
            onboarding_complete=is_onboarding_complete()
        )

# -------------------------------------------------------------
# RUN SERVER
# -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Growth Hub backend on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
