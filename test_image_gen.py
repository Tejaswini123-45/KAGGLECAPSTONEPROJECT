"""Quick test for image generation"""
import urllib.request
from pathlib import Path

# Test Pollinations.ai (FREE AI image generator)
prompt = "Delicious millet cake on a wooden table, professional food photography"
safe_prompt = prompt.replace(" ", "%20")
image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1080&height=1080&nologo=true"

output_dir = Path("marketing_outputs")
output_dir.mkdir(exist_ok=True)
filepath = output_dir / "test_image.png"

print(f"Generating image: {prompt}")
print(f"URL: {image_url}")

try:
    req = urllib.request.Request(
        image_url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        with open(filepath, 'wb') as f:
            f.write(response.read())
    
    print(f"✅ Success! Image saved to: {filepath}")
    print(f"File size: {filepath.stat().st_size} bytes")
    
except Exception as e:
    print(f"❌ Error: {e}")
