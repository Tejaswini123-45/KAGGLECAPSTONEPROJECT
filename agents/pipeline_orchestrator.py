"""Pipeline Orchestrator - Runs website generation."""
import json
from pathlib import Path
from typing import Dict, Callable, Optional
from llm.gemini_llm import GeminiLLM
from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.frontend_dev_agent import FrontendDevAgent

OUTPUT_DIR = Path(__file__).parent.parent / "pipeline_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def trigger_pipeline(memory: Dict, status_callback: Optional[Callable] = None) -> Dict:
    results = {"status": "running"}
    
    def notify(step, msg):
        if status_callback:
            try:
                status_callback(step, msg)
            except:
                pass
    
    try:
        print("[PIPELINE] Starting...")
        llm = GeminiLLM()
        
        # Save context
        notify("init", "Preparing data...")
        (OUTPUT_DIR / "context.json").write_text(json.dumps(memory, indent=2))
        
        # Strategy
        notify("strategy", "Creating blueprint...")
        print("[PIPELINE] Phase 1: Strategy")
        strategy = StrategyAgent(llm)
        blueprint_path = strategy.execute(memory)
        
        # Content
        notify("content", "Writing copy...")
        print("[PIPELINE] Phase 2: Content")
        content = ContentAgent(llm)
        content_path = content.execute(blueprint_path, memory)
        
        # Frontend
        notify("frontend", "Building website...")
        print("[PIPELINE] Phase 3: Frontend")
        frontend = FrontendDevAgent(llm)
        html_path = frontend.execute(blueprint_path, content_path)
        
        results["status"] = "completed"
        notify("completed", "Website ready!")
        print("[PIPELINE] Done!")
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        print(f"[PIPELINE] Error: {e}")
    
    return results
