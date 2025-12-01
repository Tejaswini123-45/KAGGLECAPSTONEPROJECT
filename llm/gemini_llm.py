"""
Gemini LLM - Simple wrapper for Google's Gemini API.
"""
import os

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    genai = None
    HAS_GENAI = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class GeminiLLM:
    def __init__(self, model_name=None):
        self.model_name = model_name or DEFAULT_MODEL
        self.ready = False
        self._model = None
        
        if HAS_GENAI and GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self._model = genai.GenerativeModel(self.model_name)
                self.ready = True
                print(f"[GeminiLLM] Initialized: {self.model_name}")
            except Exception as e:
                print(f"[GeminiLLM] Init error: {e}")
                self.ready = False
        else:
            print("[GeminiLLM] Not configured (missing SDK or API key)")

    def call(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """Call the LLM with a prompt."""
        if not self.ready or not self._model:
            return "⚠️ AI not configured. Please set GEMINI_API_KEY."
        
        try:
            # Safety settings to reduce blocking
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            # Generation config
            gen_config = None
            if hasattr(genai, "types") and hasattr(genai.types, "GenerationConfig"):
                gen_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            
            # Generate
            response = self._model.generate_content(
                prompt,
                generation_config=gen_config,
                safety_settings=safety_settings
            )
            
            # Extract text
            if hasattr(response, "text"):
                return response.text
            elif hasattr(response, "parts") and response.parts:
                return response.parts[0].text
            elif hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text
            
            return "⚠️ Empty response from AI"
            
        except Exception as e:
            print(f"[GeminiLLM] Error: {e}")
            return f"⚠️ AI error: {str(e)}"

    def stream(self, prompt: str):
        """Stream response (yields chunks)."""
        if not self.ready:
            yield "⚠️ AI not configured"
            return
        
        try:
            response = self._model.generate_content(prompt, stream=True)
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"⚠️ Error: {e}"
