"""
Gemini LLM wrapper for CrewAI - Direct Implementation.

Uses Google's Generative AI (Gemini) API directly.
Supports: gemini-1.5-flash (fast, cheap) and gemini-1.5-pro (smarter)

Requires GEMINI_API_KEY environment variable.
"""

import os
from typing import Optional
from crewai.llms.base_llm import BaseLLM

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


class GeminiLLM(BaseLLM):
    """
    Direct Gemini LLM wrapper for CrewAI.
    
    Supported models:
    - gemini-flash-latest: Fast, cheap, good for simple tasks (default)
    - gemini-2.0-flash: Latest Flash model with improved performance
    - gemini-2.5-flash: Even newer Flash model
    - gemini-pro-latest: Smarter, better for complex reasoning
    - gemini-2.5-pro: Latest Pro model
    
    Environment:
        GEMINI_API_KEY: Your Google Generative AI API key
        GEMINI_MODEL: Model name (default: "gemini-flash-latest")
    
    Example:
        llm = GeminiLLM()  # Uses env variables (defaults to gemini-flash-latest)
        llm = GeminiLLM(model="gemini-2.0-flash")  # Override model
    """
    
    # Class-level cache for model instances and configuration
    _model_cache = {}
    _api_key_configured = False

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        **kwargs,
    ):
        """Initialize Gemini LLM.
        
        Args:
            model: Model name - "gemini-flash-latest", "gemini-2.0-flash", "gemini-pro-latest", etc.
            api_key: Gemini API key (or use GEMINI_API_KEY env var)
            temperature: Temperature for generation (0.0-1.0)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai not installed. Install with: pip install google-generativeai"
            )

        # Get API key from parameter or environment
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not provided. Set it via environment variable or parameter."
            )

        # Configure genai with API key (only once - improves startup speed)
        if not GeminiLLM._api_key_configured:
            genai.configure(api_key=api_key)
            GeminiLLM._api_key_configured = True

        # Set model name - handle various formats
        # google.generativeai.GenerativeModel() expects model name WITHOUT "models/" prefix
        model_raw = model or os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        
        # Clean up model name - remove "models/" or "gemini/" prefixes if present
        if model_raw.startswith("models/"):
            model_raw = model_raw.replace("models/", "")
        if model_raw.startswith("gemini/"):
            model_raw = model_raw.replace("gemini/", "")
        model_raw = model_raw.strip()
        
        # Handle deprecated or missing models - map to working equivalents
        model_mapping = {
            "gemini-1.5-flash": "gemini-flash-latest",
            "gemini-1.5-flash-001": "gemini-flash-latest",
            "gemini-1.5-flash-latest": "gemini-flash-latest",
            "gemini-1.5-pro": "gemini-pro-latest",
            "gemini-1.5-pro-001": "gemini-pro-latest",
            "gemini-1.5-pro-latest": "gemini-pro-latest",
        }
        
        # Use mapped model if available, otherwise use the provided name
        self.model_name = model_mapping.get(model_raw, model_raw)
        
        # Store API key and temperature
        self.api_key = api_key
        self.temperature = temperature or 0.7
        
        # Initialize BaseLLM with a generic label (avoid model name conflicts)
        super().__init__(model="gemini", temperature=self.temperature, **kwargs)
        
        print(f"[INFO] Initialized GeminiLLM with model: {self.model_name}")

    def call(
        self,
        messages,
        tools=None,
        callbacks=None,
        available_functions=None,
        from_task=None,
        from_agent=None,
        response_model=None,
    ) -> str:
        """Call Gemini API with the given messages.
        
        Args:
            messages: String or list of message dicts
            tools, callbacks, etc.: Ignored (for BaseLLM compatibility)
        
        Returns:
            Generated text response from Gemini
        """
        # Convert messages to string
        if isinstance(messages, list):
            try:
                prompt = " ".join([m.get("content", str(m)) for m in messages])
            except Exception:
                prompt = str(messages)
        else:
            prompt = str(messages)

        try:
            # Check cache for model instance to avoid recreating on every call
            if self.model_name not in GeminiLLM._model_cache:
                # Create the model instance - pass model name WITHOUT "models/" or "gemini/" prefix
                # GenerativeModel() expects just the model name (e.g., "gemini-flash-latest")
                # The SDK handles the prefix internally
                GeminiLLM._model_cache[self.model_name] = genai.GenerativeModel(self.model_name)
            
            model = GeminiLLM._model_cache[self.model_name]

            # Generate content with proper configuration
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=2048,
                    top_p=1.0,
                ),
            )

            # Extract text from response
            if response.text:
                return response.text
            else:
                return "No response generated from Gemini."

        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Gemini API call failed: {error_msg}")
            raise RuntimeError(f"Gemini API call failed: {error_msg}") from e
