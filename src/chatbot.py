from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class SimpleChatbot:
    """
    A baseline chatbot that calls the LLM directly to simulate non-agentic behavior.
    """
    def __init__(self, llm: LLMProvider, system_prompt: str = None):
        self.llm = llm
        # Theo Instructor Guide (Phase 2), sinh viên sẽ cố gắng "prompt engineer" ở đây
        # để chatbot tự giải quyết multi-step, và nhận ra giới hạn của nó.
        self.system_prompt = system_prompt or (
            "You are a helpful e-commerce assistant. "
            "Try to answer the user's questions about stock, discounts, and shipping."
        )

    def run(self, user_input: str) -> str:
        logger.log_event("CHATBOT_START", {"input": user_input, "model": self.llm.model_name})
        
        result = self.llm.generate(user_input, system_prompt=self.system_prompt)
        response_content = result.get("content", "")
        
        logger.log_event("LLM_RESPONSE", {"response": result})
        logger.log_event("CHATBOT_END", {})
        
        return response_content

if __name__ == "__main__":
    import os
    import sys
    
    # Thêm đường dẫn gốc vào sys.path để chạy trực tiếp không bị lỗi import
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from dotenv import load_dotenv
    load_dotenv()
    
    from src.core.openai_provider import OpenAIProvider

    llm_provider = OpenAIProvider(model_name="deepseek-v4-flash")
            
    chatbot = SimpleChatbot(llm=llm_provider)
    
    print("==================================================")
    print("🤖 CHATBOT INTERACTIVE MODE (BASELINE)")
    print(f"Đang sử dụng model: {llm_provider.model_name}")
    print("Gõ 'exit' hoặc 'quit' để kết thúc.")
    print("==================================================")
    
    while True:
        try:
            user_q = input("\nBạn: ")
            if user_q.lower() in ["exit", "quit", "q"]:
                print("Tạm biệt!")
                break
            if not user_q.strip():
                continue
            
            print("Chatbot đang xử lý...")
            ans = chatbot.run(user_q)
            print(f"Chatbot: {ans}")
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break