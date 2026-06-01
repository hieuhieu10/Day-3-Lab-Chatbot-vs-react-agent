import os
import time
from typing import Dict, Any, Optional
from src.core.llm_provider import LLMProvider

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        super().__init__(model_name)
        if genai is None:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        if system_prompt:
            model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)
        else:
            model = genai.GenerativeModel(self.model_name)
            
        response = model.generate_content(prompt)
        end_time = time.time()
        
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if hasattr(response, 'usage_metadata'):
            usage = {
                "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
            }
            
        return {
            "content": response.text,
            "usage": usage,
            "latency_ms": int((end_time - start_time) * 1000),
            "provider": "gemini"
        }