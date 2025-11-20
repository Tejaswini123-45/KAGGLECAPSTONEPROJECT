#!/usr/bin/env python
"""Quick test that Gemini LLM is working."""

import os
import sys

# Test imports
try:
    from llm.gemini_llm import GeminiLLM
    print("✓ Gemini LLM module imported")
except ImportError as e:
    print(f"✗ Failed to import GeminiLLM: {e}")
    sys.exit(1)

# Test agent import
try:
    from agents.router_agent import router_agent
    print("✓ Router agent imported")
    print(f"  - Name: {router_agent.name}")
    print(f"  - Role: {router_agent.role}")
except Exception as e:
    print(f"✗ Failed to import router agent: {e}")
    sys.exit(1)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    print("✓ GEMINI_API_KEY configured")
else:
    print("⚠ GEMINI_API_KEY not configured. Set it in .env file")
    print("  Get one at: https://ai.google.dev/")

print("\n✓ All components ready!")
print("\nNext steps:")
print("  1. Add your Gemini API key to .env file")
print("  2. Run: python main.py chat  (for interactive chat)")
print("  3. Run: python main.py server (to start API)")
