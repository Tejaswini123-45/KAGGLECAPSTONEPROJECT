"""Test script to verify Gemini chatbot is working."""

import os
from agents.router_agent import router_agent

# Load env variables
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*60)
print("🤖 AI Company Builder - Gemini Chatbot Test")
print("="*60 + "\n")

# Test 1: Check API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    print("✓ Gemini API Key configured")
else:
    print("✗ Gemini API Key not found in .env")
    exit(1)

# Test 2: Check router agent
print("✓ Router Agent loaded")
print(f"  - Role: {router_agent.role}")

# Test 3: Send a test message to Gemini
print("\n" + "-"*60)
print("Testing Gemini response...")
print("-"*60 + "\n")

try:
    llm = router_agent.llm
    
    test_messages = [
        "I want to start a SaaS business, what should I do?",
        "How do I build a website?",
        "What's the first step in starting a business?",
    ]
    
    # Test with first message
    message = test_messages[0]
    print(f"📝 Question: {message}\n")
    
    response = llm.call(message)
    
    print(f"🤖 Router Response:\n{response}\n")
    
    if response and len(response) > 10:
        print("✓ Gemini API is working!")
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - System is ready!")
        print("="*60)
        print("\nYou can now use:")
        print("  • python main.py chat       (interactive)")
        print("  • python main.py server     (API server)")
        print("  • python main.py            (full crew)\n")
    else:
        print("✗ No response from Gemini")
        exit(1)
        
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check .env file has GEMINI_API_KEY")
    print("  2. Verify API key is valid at https://ai.google.dev/")
    print("  3. Check internet connection")
    exit(1)
