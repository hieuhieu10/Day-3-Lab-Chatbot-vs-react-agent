import os
import time
from typing import Dict, Any, Optional, Generator
from openai import OpenAI
from src.core.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(model_name, api_key)
        resolved_base_url = base_url or os.getenv("LLM_ENDPOINT") or None
        resolved_api_key = self.api_key or os.getenv("API_KEY") or "no-key"
        self.client = OpenAI(api_key=resolved_api_key, base_url=resolved_base_url)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Extraction from OpenAI response
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "openai"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from dotenv import load_dotenv
    load_dotenv()

    model = os.getenv("MODEL", "deepseek-v4-flash")
    print(f"Endpoint : {os.getenv('LLM_ENDPOINT')}")
    print(f"Model    : {model}")

    provider = OpenAIProvider(model_name=model)

    prompt = "Say hello in one sentence."
    print(f"User: {prompt}")
    print("Assistant: ", end="", flush=True)

    for chunk in provider.stream(prompt):
        print(chunk, end="", flush=True)
    print()