"""Content Agent - Generates website copy."""
import json
from pathlib import Path
from llm.gemini_llm import GeminiLLM

class ContentAgent:
    def __init__(self, llm: GeminiLLM):
        self.llm = llm
        self.output_dir = Path(__file__).parent.parent / "pipeline_outputs"
        self.output_dir.mkdir(exist_ok=True)
    
    def execute(self, blueprint_path: Path, context: dict) -> Path:
        print("[Content] Generating copy...")
        
        blueprint = json.loads(blueprint_path.read_text()) if blueprint_path.exists() else {}
        
        prompt = f"""Write website copy JSON for:
- Brand: {context.get('brand_name', 'My Business')}
- Problem: {context.get('problem', 'N/A')}
- Services: {context.get('services', 'N/A')}
- Unique: {context.get('unique_feature', 'N/A')}
- CTA: {context.get('primary_cta', 'Get Started')}
- Trust: {context.get('trust_factors', 'N/A')}

Return ONLY valid JSON:
{{"hero": {{"h1": "Headline", "subtext": "Description", "cta": {{"primary": "CTA Text"}}}},
"features": [{{"title": "Feature", "description": "Description"}}],
"how_it_works": [{{"step": 1, "title": "Step", "description": "Description"}}],
"testimonials": [{{"quote": "Quote", "author": "Name", "role": "Role"}}],
"cta": {{"title": "Ready?", "button": "Get Started"}}}}"""
        
        try:
            response = self.llm.call(prompt, max_tokens=1000)
            response = response.strip()
            if "```" in response:
                response = response.split("```")[1].replace("json", "").strip()
            content = json.loads(response)
        except:
            cta = context.get('primary_cta', 'Get Started')
            content = {
                "hero": {
                    "h1": context.get('brand_name', 'Welcome'),
                    "subtext": context.get('problem', 'We solve your problems'),
                    "cta": {"primary": cta}
                },
                "features": [
                    {"title": "Quality", "description": "We deliver excellence"},
                    {"title": "Speed", "description": "Fast results"},
                    {"title": "Support", "description": "24/7 help"}
                ],
                "how_it_works": [
                    {"step": 1, "title": "Contact", "description": "Reach out"},
                    {"step": 2, "title": "Plan", "description": "We discuss"},
                    {"step": 3, "title": "Deliver", "description": "We deliver"}
                ],
                "testimonials": [{"quote": "Great service!", "author": "Customer", "role": "Client"}],
                "cta": {"title": "Ready to start?", "button": cta}
            }
        
        output = self.output_dir / "content_copy.json"
        output.write_text(json.dumps(content, indent=2))
        print(f"[Content] Saved: {output}")
        return output
