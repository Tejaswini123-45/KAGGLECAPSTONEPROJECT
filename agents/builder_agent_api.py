"""Builder API - Website generation endpoints."""
import json
import threading
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Optional
from memory import memory_manager as mem
from agents.pipeline_orchestrator import trigger_pipeline

router = APIRouter(prefix="/api/builder", tags=["builder"])

PIPELINE_STATUS = {"status": "idle", "message": "", "step": ""}

class GenerateRequest(BaseModel):
    user_answers: Optional[Dict] = None
    tweaks: Optional[Dict] = None

class GenerateResponse(BaseModel):
    status: str
    message: str = ""
    html: Optional[str] = None

@router.get("/status")
async def get_status():
    return PIPELINE_STATUS

@router.get("/answers")
async def get_answers():
    builder = mem.load_builder()
    return {"answers": builder, "onboarding_complete": builder.get("onboarding_complete", False)}

@router.post("/answers")
async def save_answers(payload: dict):
    answers = payload.get("answers", {})
    builder = mem.load_builder()
    builder.update(answers)
    mem.save_builder(builder)
    return {"status": "success"}

@router.get("/preview", response_class=HTMLResponse)
async def get_preview():
    html_path = Path(__file__).parent.parent / "pipeline_outputs" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return JSONResponse({"error": "No website yet"}, status_code=404)

@router.get("/download")
async def download_site():
    html_path = Path(__file__).parent.parent / "pipeline_outputs" / "index.html"
    if not html_path.exists():
        return JSONResponse({"error": "No website yet"}, status_code=404)
    return FileResponse(path=html_path, filename="index.html", media_type="text/html")

@router.post("/generate", response_model=GenerateResponse)
async def generate_website(request: GenerateRequest):
    global PIPELINE_STATUS
    
    if PIPELINE_STATUS["status"] == "running":
        return GenerateResponse(status="running", message="Already generating")
    
    builder = mem.load_builder()
    if request.user_answers:
        builder.update(request.user_answers)
        mem.save_builder(builder)
    
    required = ["problem", "services"]
    missing = [f for f in required if not builder.get(f)]
    if missing:
        return GenerateResponse(status="error", message=f"Missing: {', '.join(missing)}")
    
    PIPELINE_STATUS = {"status": "running", "message": "Starting...", "step": "init"}
    
    def run():
        global PIPELINE_STATUS
        try:
            def callback(step, msg):
                PIPELINE_STATUS["step"] = step
                PIPELINE_STATUS["message"] = msg
            
            result = trigger_pipeline(builder, status_callback=callback)
            PIPELINE_STATUS["status"] = "completed" if result["status"] == "completed" else "error"
            PIPELINE_STATUS["message"] = result.get("error", "Done!")
        except Exception as e:
            PIPELINE_STATUS = {"status": "error", "message": str(e), "step": "error"}
    
    threading.Thread(target=run, daemon=True).start()
    return GenerateResponse(status="running", message="Started")

@router.post("/regenerate", response_model=GenerateResponse)
async def regenerate_website(request: GenerateRequest):
    from agents.frontend_dev_agent import FrontendDevAgent
    from llm.gemini_llm import GeminiLLM
    
    output_dir = Path(__file__).parent.parent / "pipeline_outputs"
    blueprint_path = output_dir / "website_blueprint.json"
    content_path = output_dir / "content_copy.json"
    
    if not blueprint_path.exists() or not content_path.exists():
        return GenerateResponse(status="error", message="Generate website first")
    
    try:
        blueprint = json.loads(blueprint_path.read_text())
        content = json.loads(content_path.read_text())
        
        tweaks = request.tweaks or {}
        if "headline" in tweaks and "hero" in content:
            content["hero"]["h1"] = tweaks["headline"]
        if "subheadline" in tweaks and "hero" in content:
            content["hero"]["subtext"] = tweaks["subheadline"]
        if "color" in tweaks:
            blueprint["color_palette"] = {"primary": tweaks["color"]}
        
        content_path.write_text(json.dumps(content, indent=2))
        
        llm = GeminiLLM()
        frontend = FrontendDevAgent(llm)
        html_path = frontend.execute(blueprint_path, content_path, tweaks=tweaks)
        
        return GenerateResponse(status="success", message="Regenerated!", html=html_path.read_text())
    except Exception as e:
        return GenerateResponse(status="error", message=str(e))
