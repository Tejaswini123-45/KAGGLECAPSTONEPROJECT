"""
Marketing Agent - Generates Instagram posts with captions, hashtags, and images.
Posts directly to Instagram using FREE Instagrapi (no Facebook needed).
"""
import os
import json
import requests
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from llm.gemini_llm import GeminiLLM

class MarketingAgent:
    """Agent for generating and posting social media content."""
    
    def __init__(self):
        self.llm = GeminiLLM()
        self.output_dir = Path(__file__).parent.parent / "marketing_outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # Zapier webhook URL - user can configure this
        self.webhook_url = os.getenv("ZAPIER_WEBHOOK_URL", "https://hooks.zapier.com/hooks/catch/25461153/uzfgb5n/")
    
    def generate_post(self, topic: str, audience: str, tone: str, brand_name: str = "GrowthHub") -> Dict:
        """
        Generate a complete Instagram post with caption, hashtags, and image prompt.
        
        Args:
            topic: What the post is about
            audience: Target audience
            tone: Tone of voice (professional, casual, exciting, etc.)
            brand_name: Brand name for the post
            
        Returns:
            Dict with caption, hashtags, image_prompt, image_url
        """
        print(f"[Marketing] Generating post for: {topic}")
        
        prompt = f"""Create an Instagram post for a business.

Topic: {topic}
Target Audience: {audience}
Tone: {tone}
Brand: {brand_name}

Generate:
1. A compelling caption (2-3 sentences, engaging, with emojis)
2. 10-15 relevant hashtags
3. An image description for AI image generation

Return ONLY valid JSON:
{{
    "caption": "Your engaging caption here with emojis 🚀",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "image_prompt": "Description of the image to generate"
}}"""
        
        try:
            response = self.llm.call(prompt, max_tokens=500)
            response = response.strip()
            
            # Clean JSON from markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response)
            
            # Generate and download image
            result["image_path"] = self._generate_image(result.get("image_prompt", topic))
            # Create URL for preview in UI
            image_filename = Path(result["image_path"]).name
            result["image_url"] = f"/marketing/image/{image_filename}"
            
        except Exception as e:
            print(f"[Marketing] Error: {e}")
            # Fallback content
            fallback_image_path = self._generate_image(f"Professional business image about {topic}")
            image_filename = Path(fallback_image_path).name
            result = {
                "caption": f"🚀 {topic} - Discover how we can help you succeed! {brand_name} is here for you. 💪",
                "hashtags": ["business", "success", "growth", "entrepreneur", "motivation", 
                            topic.lower().replace(" ", ""), brand_name.lower()],
                "image_prompt": f"Professional business image about {topic}",
                "image_url": f"/marketing/image/{image_filename}",
                "image_path": fallback_image_path
            }
        
        # Save the generated post
        self._save_post(result, topic)
        
        return result
    
    def _generate_image(self, prompt: str) -> str:
        """
        Generate and download AI image using FREE Pollinations.ai API.
        No API key needed!
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"post_image_{timestamp}.png"
        filepath = self.output_dir / filename
        
        try:
            # Use Pollinations.ai - FREE AI image generation (no API key!)
            safe_prompt = prompt.replace(" ", "%20")
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1080&height=1080&nologo=true"
            
            print(f"[Marketing] Generating AI image: {prompt[:50]}...")
            
            # Download with proper headers
            req = urllib.request.Request(
                image_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
            
            print(f"[Marketing] Image saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[Marketing] Error generating image: {e}")
            # Create a simple colored image as fallback
            return self._create_fallback_image(filepath, prompt)
    
    def _create_fallback_image(self, filepath: Path, text: str) -> str:
        """Create a simple colored image with text as fallback."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a gradient background
            img = Image.new('RGB', (1080, 1080), color='#7c3aed')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            # Wrap text
            words = text[:100].split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 30:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text centered
            y = 400
            for line in lines[:3]:  # Max 3 lines
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1080 - text_width) // 2
                draw.text((x, y), line, fill='white', font=font)
                y += 80
            
            img.save(filepath)
            print(f"[Marketing] Created fallback image: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[Marketing] Could not create fallback image: {e}")
            # Last resort: create a tiny valid PNG
            with open(filepath, 'wb') as f:
                # Minimal valid PNG (1x1 purple pixel)
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82')
            return str(filepath)
    
    def _save_post(self, post: Dict, topic: str):
        """Save generated post to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"post_{timestamp}.json"
        filepath = self.output_dir / filename
        
        post["generated_at"] = datetime.now().isoformat()
        post["topic"] = topic
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(post, f, indent=2, ensure_ascii=False)
        
        print(f"[Marketing] Saved: {filepath}")
    
    def post_now(self, post: Dict, instagram_account: str = None) -> Dict:
        """
        Post immediately to Instagram using FREE Instagrapi.
        
        Args:
            post: Post data from generate_post()
            instagram_account: Instagram account username (for display only)
            
        Returns:
            Dict with status and details
        """
        print(f"[Marketing] Posting to Instagram...")
        
        from agents.instagram_poster import InstagramPoster
        poster = InstagramPoster()
        
        # Get image path - if not exists, download from URL
        image_path = post.get("image_path")
        if not image_path or not Path(image_path).exists():
            # Download image from URL
            image_url = post.get("image_url", "")
            if image_url:
                import urllib.request
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = str(self.output_dir / f"temp_image_{timestamp}.png")
                try:
                    urllib.request.urlretrieve(image_url, image_path)
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Failed to download image: {str(e)}"
                    }
        
        # Post to Instagram
        result = poster.post_to_instagram(
            caption=post.get("caption", ""),
            image_path=image_path,
            hashtags=post.get("hashtags", [])
        )
        
        return result
    
    def get_post_preview(self, post: Dict) -> str:
        """Get a formatted preview of the post."""
        hashtags = " ".join([f"#{tag}" for tag in post.get("hashtags", [])])
        
        return f"""
📸 INSTAGRAM POST PREVIEW
━━━━━━━━━━━━━━━━━━━━━━━━

📝 Caption:
{post.get('caption', '')}

#️⃣ Hashtags:
{hashtags}

🖼️ Image:
{post.get('image_url', 'No image')}

━━━━━━━━━━━━━━━━━━━━━━━━
"""


# Standalone functions for API use
def generate_instagram_post(topic: str, audience: str, tone: str, brand: str = "GrowthHub") -> Dict:
    """Generate an Instagram post."""
    agent = MarketingAgent()
    return agent.generate_post(topic, audience, tone, brand)

def post_to_instagram_now(post: Dict, account: str = None) -> Dict:
    """Post immediately to Instagram (FREE)."""
    agent = MarketingAgent()
    return agent.post_now(post, account)
