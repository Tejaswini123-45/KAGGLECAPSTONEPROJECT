"""Strategy Agent - Creates website blueprint."""
import json
from pathlib import Path
from llm.gemini_llm import GeminiLLM

class StrategyAgent:
    def __init__(self, llm: GeminiLLM):
        self.llm = llm
        self.output_dir = Path(__file__).parent.parent / "pipeline_outputs"
        self.output_dir.mkdir(exist_ok=True)
    
    def execute(self, context: dict) -> Path:
        print("[Strategy] Creating blueprint...")
        
        prompt = f"""Create a website blueprint JSON for this business:
- Brand: {context.get('brand_name', 'My Business')}
- Problem: {context.get('problem', 'N/A')}
- Audience: {context.get('target_audience', 'N/A')}
- Services: {context.get('services', 'N/A')}
- Unique: {context.get('unique_feature', 'N/A')}

Return ONLY valid JSON:
{{"site_structure": ["Hero", "Features", "How It Works", "Testimonials", "Pricing", "CTA"],
"color_palette": {{"primary": "#4F46E5", "secondary": "#1F2937", "accent": "#10B981"}},
"tone": "professional and friendly",
"positioning": "We help [audience] solve [problem]"}}"""
        
        try:
            response = self.llm.call(prompt, max_tokens=500)
            response = response.strip()
            if "```" in response:
                response = response.split("```")[1].replace("json", "").strip()
            blueprint = json.loads(response)
        except:
            blueprint = {
                "site_structure": ["Hero", "Features", "How It Works", "Testimonials", "CTA"],
                "color_palette": {"primary": "#4F46E5", "secondary": "#1F2937"},
                "tone": "professional",
                "positioning": context.get('unique_feature', 'Your solution')
            }
        
        output = self.output_dir / "website_blueprint.json"
        output.write_text(json.dumps(blueprint, indent=2))
        print(f"[Strategy] Saved: {output}")
        return output
