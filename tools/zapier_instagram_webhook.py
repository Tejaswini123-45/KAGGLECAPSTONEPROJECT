from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Optional
import requests
import json
from datetime import datetime

class ZapierInstagramWebhookInput(BaseModel):
    """Input schema for Zapier Instagram Webhook Tool."""
    content: str = Field(..., description="The post caption/text content")
    media_urls: Optional[List[str]] = Field(default=None, description="List of image URLs (optional)")
    preferred_posting_time: str = Field(..., description="The preferred posting time (e.g., '1:10 PM')")
    timezone: str = Field(..., description="The timezone for posting (e.g., 'EST')")
    hashtags: Optional[List[str]] = Field(default=None, description="List of hashtags without # symbol (optional)")
    brand_name: Optional[str] = Field(default=None, description="Brand name (optional)")
    

class ZapierInstagramWebhookTool(BaseTool):
    """Tool for sending Instagram post data to Zapier webhook for automated posting."""

    name: str = "zapier_instagram_webhook"
    description: str = (
        "Sends Instagram post data to a Zapier webhook for automated posting. "
        "Handles content, media URLs, posting time, timezone, hashtags and brand information. "
        "Returns webhook confirmation on success or detailed error message on failure."
    )
    args_schema: Type[BaseModel] = ZapierInstagramWebhookInput

    def _run(self, content: str, preferred_posting_time: str, timezone: str, 
             media_urls: Optional[List[str]] = None, hashtags: Optional[List[str]] = None, 
             brand_name: Optional[str] = None) -> str:
        """
        Send Instagram post data to Zapier webhook.
        """
        
        webhook_url = "https://hooks.zapier.com/hooks/catch/25461153/uzfgb5n/"
        timestamp = datetime.now().isoformat()
        
        try:
            # Format hashtags if provided
            formatted_hashtags = []
            if hashtags:
                formatted_hashtags = [f"#{tag.lstrip('#')}" for tag in hashtags]
            
            # Combine content with hashtags
            full_content = content
            if formatted_hashtags:
                full_content += " " + " ".join(formatted_hashtags)
            
            # Prepare JSON payload
            payload = {
                "content": full_content,
                "media_urls": media_urls or [],
                "preferred_posting_time": preferred_posting_time,
                "timezone": timezone,
                "account": "@kskk.2031",
                "post_type": "feed",
                "brand_name": brand_name
            }
            
            # Set headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "CrewAI-InstagramWebhookTool/1.0"
            }
            
            # Send POST request to webhook
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Handle different response codes
            if response.status_code == 200:
                return (
                    f"✅ SUCCESS: Instagram post data sent to Zapier webhook successfully!\n"
                    f"📅 Timestamp: {timestamp}\n"
                    f"⏰ Preferred posting time: {preferred_posting_time} {timezone}\n"
                    f"📝 Content: {full_content[:50]}...\n"
                )
            else:
                return f"❌ FAILURE: Zapier webhook returned status {response.status_code}"
                
        except Exception as e:
            return f"❌ FAILURE: Error sending to webhook: {str(e)}"
