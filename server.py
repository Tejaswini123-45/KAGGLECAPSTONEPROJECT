"""Growth Hub Server - Main FastAPI application."""
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from agents.router_agent_handler import process_message_with_memory, process_message_stream, router_agent
from agents.builder_agent_api import router as builder_router
from agents.router_agent_api import router as router_api

app = FastAPI(title="Growth Hub AI")
app.include_router(builder_router)
app.include_router(router_api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    return FileResponse(path) if os.path.exists(path) else JSONResponse({"error": "Not found"}, 404)

@app.get("/chatbot.html")
def serve_chatbot():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot.html")
    return FileResponse(path) if os.path.exists(path) else JSONResponse({"error": "Not found"}, 404)

@app.get("/builder")
def serve_builder():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "builder.html")
    return FileResponse(path) if os.path.exists(path) else JSONResponse({"error": "Not found"}, 404)

@app.get("/health")
async def health():
    ready = getattr(router_agent, "llm", None) and getattr(router_agent.llm, "ready", False)
    return {"status": "online", "llm_ready": ready}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    reply = process_message_with_memory(data.get("message", ""))
    return {"response": reply}

@app.post("/chat-stream")
async def chat_stream(req: Request):
    data = await req.json()
    return StreamingResponse(process_message_stream(data.get("message", "")), media_type="text/plain")

@app.post("/marketing/generate-post")
async def generate_post(req: Request):
    """Generate an Instagram post with caption, hashtags, and image."""
    data = await req.json()
    try:
        from agents.marketing_agent import MarketingAgent
        agent = MarketingAgent()
        
        post = agent.generate_post(
            topic=data.get('topic', 'Business Growth'),
            audience=data.get('audience', 'Entrepreneurs'),
            tone=data.get('tone', 'Professional'),
            brand_name=data.get('brand', 'GrowthHub')
        )
        
        return {
            "status": "success",
            "result": post,
            "preview": agent.get_post_preview(post)
        }
    except Exception as e:
        print(f"Marketing Error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/marketing/post-now")
async def post_now(req: Request):
    """Post immediately to Instagram using FREE Graph API."""
    data = await req.json()
    try:
        from agents.marketing_agent import post_to_instagram_now
        
        # Get post data
        if "post" not in data:
            from agents.marketing_agent import generate_instagram_post
            post = generate_instagram_post(
                topic=data.get('topic', 'Business'),
                audience=data.get('audience', 'Entrepreneurs'),
                tone=data.get('tone', 'Professional'),
                brand=data.get('brand', 'GrowthHub')
            )
        else:
            post = data["post"]
        
        # Post to Instagram
        result = post_to_instagram_now(post, data.get('instagram_account'))
        
        return {"status": "success", "result": result}
    except Exception as e:
        print(f"Post Error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/marketing/setup")
async def get_setup_instructions():
    """Get FREE Instagram API setup instructions."""
    from agents.instagram_poster import InstagramPoster
    poster = InstagramPoster()
    return poster.get_setup_instructions()

@app.get("/marketing/image/{filename}")
async def serve_marketing_image(filename: str):
    """Serve generated marketing images."""
    from pathlib import Path
    image_path = Path(__file__).parent / "marketing_outputs" / filename
    if image_path.exists():
        return FileResponse(image_path)
    return JSONResponse({"error": "Image not found"}, status_code=404)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
