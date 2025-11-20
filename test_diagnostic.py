"""
Diagnostic script to test Gemini LLM directly.
This bypasses the server/agent to see the raw issue.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Test 1: Check environment
print("=" * 60)
print("DIAGNOSTIC TEST 1: Environment Variables")
print("=" * 60)
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL")
print(f"✓ GEMINI_API_KEY: {api_key[:20]}..." if api_key else "✗ GEMINI_API_KEY: NOT SET")
print(f"✓ GEMINI_MODEL: {model_name}" if model_name else "✗ GEMINI_MODEL: NOT SET")

# Test 2: Import and test Gemini directly
print("\n" + "=" * 60)
print("DIAGNOSTIC TEST 2: Direct Gemini API Call")
print("=" * 60)

try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
    
    # Configure API
    genai.configure(api_key=api_key)
    print("✓ API configured with key")
    
    # Try with the exact model name
    model_name_clean = model_name.replace("models/", "").replace("-latest", "")
    print(f"\n→ Attempting to use model: '{model_name_clean}'")
    
    model = genai.GenerativeModel(model_name_clean)
    print(f"✓ GenerativeModel created successfully")
    
    # Try a simple call
    print("\n→ Attempting API call with test prompt...")
    response = model.generate_content(
        "Say 'Hello' in one word only.",
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=10,
        ),
    )
    print(f"✓ API call successful!")
    print(f"✓ Response: {response.text}")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
    print(f"✗ Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

# Test 3: Test our GeminiLLM wrapper
print("\n" + "=" * 60)
print("DIAGNOSTIC TEST 3: GeminiLLM Wrapper")
print("=" * 60)

try:
    from llm.gemini_llm import GeminiLLM
    print("✓ GeminiLLM imported successfully")
    
    llm = GeminiLLM()
    print(f"✓ GeminiLLM initialized")
    print(f"  - Model name: {llm.model_name}")
    print(f"  - Temperature: {llm.temperature}")
    
    # Try a call
    print("\n→ Attempting GeminiLLM.call() with test message...")
    response = llm.call("Say 'Hello' in one word only.")
    print(f"✓ GeminiLLM.call() successful!")
    print(f"✓ Response: {response}")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
    print(f"✗ Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
