"""Frontend Agent - Generates HTML website."""
import json
from pathlib import Path
from typing import Dict, Optional
from llm.gemini_llm import GeminiLLM

class FrontendDevAgent:
    def __init__(self, llm: GeminiLLM):
        self.llm = llm
        self.output_dir = Path(__file__).parent.parent / "pipeline_outputs"
        self.output_dir.mkdir(exist_ok=True)
    
    def execute(self, blueprint_path: Path, content_path: Path, tweaks: Optional[Dict] = None) -> Path:
        print("[Frontend] Building HTML...")
        
        blueprint = json.loads(blueprint_path.read_text()) if blueprint_path.exists() else {}
        content = json.loads(content_path.read_text()) if content_path.exists() else {}
        
        tweak_text = ""
        if tweaks:
            if "headline" in tweaks:
                tweak_text += f"\nUse headline: {tweaks['headline']}"
            if "color" in tweaks:
                tweak_text += f"\nUse primary color: {tweaks['color']}"
        
        prompt = f"""Create a modern landing page HTML with Tailwind CSS.

BLUEPRINT: {json.dumps(blueprint)}
CONTENT: {json.dumps(content)}
{tweak_text}

Requirements:
- Use <script src="https://cdn.tailwindcss.com"></script>
- Responsive design
- Smooth scroll (scroll-smooth on html)
- Navigation with anchor links
- Hero, Features, How It Works, Testimonials, CTA sections
- Modern styling with gradients

Return ONLY the complete HTML code."""
        
        try:
            response = self.llm.call(prompt, max_tokens=4000)
            html = response.strip()
            if "```html" in html:
                html = html.split("```html")[1].split("```")[0].strip()
            elif "```" in html:
                html = html.split("```")[1].split("```")[0].strip()
            
            if not html.startswith("<!DOCTYPE") and not html.startswith("<html"):
                raise ValueError("Invalid HTML")
        except:
            html = self._fallback_html(blueprint, content)
        
        output = self.output_dir / "index.html"
        output.write_text(html, encoding="utf-8")
        print(f"[Frontend] Saved: {output}")
        return output
    
    def _fallback_html(self, blueprint: dict, content: dict) -> str:
        hero = content.get("hero", {})
        features = content.get("features", [])
        color = blueprint.get("color_palette", {}).get("primary", "#4F46E5")
        
        features_html = "".join([
            f'<div class="bg-white p-6 rounded-lg shadow"><h3 class="text-xl font-bold mb-2">{f.get("title","")}</h3><p class="text-gray-600">{f.get("description","")}</p></div>'
            for f in features[:3]
        ])
        
        return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{hero.get("h1","Website")}</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={{theme:{{extend:{{colors:{{primary:"{color}"}}}}}}}}</script>
</head>
<body class="bg-gray-50">
<nav class="fixed w-full bg-white shadow z-50"><div class="max-w-7xl mx-auto px-4 py-4 flex justify-between">
<span class="text-xl font-bold text-primary">Logo</span>
<div class="space-x-6"><a href="#features" class="text-gray-600 hover:text-primary">Features</a>
<a href="#contact" class="bg-primary text-white px-4 py-2 rounded">Get Started</a></div></div></nav>

<section class="pt-32 pb-20 bg-gradient-to-b from-white to-gray-50">
<div class="max-w-7xl mx-auto px-4 text-center">
<h1 class="text-5xl font-bold text-gray-900 mb-6">{hero.get("h1","Welcome")}</h1>
<p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">{hero.get("subtext","Your solution")}</p>
<button onclick="alert('Thank you!')" class="bg-primary text-white px-8 py-4 rounded-lg text-lg font-semibold hover:opacity-90">
{hero.get("cta",{}).get("primary","Get Started")}</button></div></section>

<section id="features" class="py-20"><div class="max-w-7xl mx-auto px-4">
<h2 class="text-3xl font-bold text-center mb-12">Features</h2>
<div class="grid md:grid-cols-3 gap-8">{features_html}</div></div></section>

<section id="contact" class="py-20 bg-primary"><div class="max-w-7xl mx-auto px-4 text-center">
<h2 class="text-3xl font-bold text-white mb-6">Ready to get started?</h2>
<button onclick="alert('Thank you!')" class="bg-white text-primary px-8 py-4 rounded-lg font-semibold">Contact Us</button>
</div></section>

<footer class="bg-gray-900 text-white py-8"><div class="max-w-7xl mx-auto px-4 text-center">
<p>&copy; 2024 All rights reserved.</p></div></footer>
</body></html>'''
