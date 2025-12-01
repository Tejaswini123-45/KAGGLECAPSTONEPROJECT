"""
Instagram Poster - FREE solution using Instagrapi.
No Facebook, No Zapier, No Business Account needed!
Just your regular Instagram account.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    from instagrapi import Client
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False
    print("⚠️ Instagrapi not installed. Run: pip install instagrapi")

class InstagramPoster:
    """
    Free Instagram posting using Instagrapi library.
    Works with regular Instagram accounts - NO Facebook needed!
    """
    
    def __init__(self):
        # Get credentials from environment
        self.username = os.getenv("INSTAGRAM_USERNAME", "")
        self.password = os.getenv("INSTAGRAM_PASSWORD", "")
        
        self.output_dir = Path(__file__).parent.parent / "marketing_outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        self.client = None
        if INSTAGRAPI_AVAILABLE:
            self.client = Client()
            self.client.delay_range = [1, 3]  # Delay between requests to avoid rate limits
    
    def post_to_instagram(self, caption: str, image_path: str, hashtags: list = None) -> Dict:
        """
        Post directly to Instagram using Instagrapi (FREE, NO Facebook needed).
        
        Args:
            caption: Post caption
            image_path: Local path to image file
            hashtags: List of hashtags
            
        Returns:
            Dict with status and post details
        """
        if not INSTAGRAPI_AVAILABLE:
            return {
                "status": "error",
                "message": "Instagrapi not installed. Run: pip install instagrapi"
            }
        
        if not self.username or not self.password:
            return {
                "status": "error",
                "message": "Instagram credentials not configured. Add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to .env file"
            }
        
        # Format caption with hashtags
        full_caption = caption
        if hashtags:
            hashtag_str = " ".join([f"#{h.lstrip('#')}" for h in hashtags])
            full_caption = f"{caption}\n\n{hashtag_str}"
        
        try:
            # Check if image exists
            if not Path(image_path).exists():
                return {
                    "status": "error",
                    "message": f"Image file not found: {image_path}"
                }
            
            # Login to Instagram
            print(f"[Instagram] Logging in as {self.username}...")
            self.client.login(self.username, self.password)
            print("[Instagram] Login successful!")
            
            # Upload photo
            print(f"[Instagram] Uploading photo from {image_path}...")
            media = self.client.photo_upload(
                path=image_path,
                caption=full_caption
            )
            
            post_id = media.pk
            self._save_post_record(caption, image_path, hashtags, str(post_id))
            
            print(f"[Instagram] ✅ Posted successfully! ID: {post_id}")
            print(f"[Instagram] View at: https://www.instagram.com/p/{media.code}/")
            
            return {
                "status": "success",
                "message": f"Posted to Instagram successfully! View at: https://www.instagram.com/p/{media.code}/",
                "post_id": str(post_id),
                "post_url": f"https://www.instagram.com/p/{media.code}/",
                "caption": full_caption[:100] + "...",
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            error_msg = str(e)
            print(f"[Instagram] ❌ Error: {error_msg}")
            
            # Provide helpful error messages
            if "challenge_required" in error_msg.lower():
                error_msg = "Instagram requires verification. Please log in to Instagram on your phone/browser and complete any security checks, then try again."
            elif "login" in error_msg.lower() or "password" in error_msg.lower():
                error_msg = "Login failed. Check your INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env file."
            elif "two_factor" in error_msg.lower() or "2fa" in error_msg.lower():
                error_msg = "Two-factor authentication detected. You may need to use an app-specific password or disable 2FA temporarily."
            
            return {
                "status": "error",
                "message": f"Error posting to Instagram: {error_msg}"
            }
    
    def _save_post_record(self, caption: str, image_path: str, hashtags: list, post_id: str):
        """Save a record of the posted content."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record = {
            "post_id": post_id,
            "caption": caption,
            "image_path": image_path,
            "hashtags": hashtags,
            "posted_at": datetime.now().isoformat()
        }
        
        filepath = self.output_dir / f"posted_{timestamp}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
    
    def get_setup_instructions(self) -> Dict:
        """Get instructions for setting up Instagram posting (FREE, NO Facebook!)."""
        return {
            "title": "FREE Instagram Setup (NO Facebook Account Needed!)",
            "steps": [
                {
                    "step": 1,
                    "title": "Install Instagrapi",
                    "description": "Open terminal and run: pip install instagrapi",
                    "command": "pip install instagrapi"
                },
                {
                    "step": 2,
                    "title": "Add Credentials to .env",
                    "description": "Add your regular Instagram username and password to .env file:\nINSTAGRAM_USERNAME=your_username\nINSTAGRAM_PASSWORD=your_password"
                },
                {
                    "step": 3,
                    "title": "That's It!",
                    "description": "You're ready to post! No Facebook, no business account, no API tokens needed."
                }
            ],
            "helpful_links": {
                "Instagrapi GitHub": "https://github.com/adw0rd/instagrapi",
                "Instagrapi Docs": "https://adw0rd.github.io/instagrapi/"
            },
            "notes": [
                "✅ Completely FREE - No Zapier, no Facebook needed",
                "✅ Works with regular Instagram accounts",
                "✅ Just username and password",
                "✅ No business account conversion needed",
                "⚠️ Uses unofficial Instagram API (works but not officially supported)",
                "⚠️ Use strong password and enable 2FA for security",
                "💡 Tip: Create a separate Instagram account for automation"
            ]
        }


# Helper function for API use
def post_to_instagram_free(caption: str, image_path: str, hashtags: list = None) -> Dict:
    """Post to Instagram using FREE Instagrapi (NO Facebook needed!)."""
    poster = InstagramPoster()
    return poster.post_to_instagram(caption, image_path, hashtags)
