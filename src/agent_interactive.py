import os
import sys
from dotenv import load_dotenv

# Thêm thư mục gốc vào đường dẫn để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import ReActAgent
from src.tools.ecommerce_tools import ECOMMERCE_TOOLS

if __name__ == "__main__":
    load_dotenv()
    
    # Khởi tạo Provider
    try:
        from src.core.openai_provider import OpenAIProvider
        llm = OpenAIProvider(model_name="deepseek-v4-flash")
    except Exception as e:
        print(f"Không thể khởi tạo Provider. Kiểm tra lại .env: {e}")
        sys.exit(1)

    agent = ReActAgent(llm=llm, tools=ECOMMERCE_TOOLS, max_steps=5)
    
    print("==================================================")
    print("🤖 REACT AGENT INTERACTIVE MODE")
    print(f"Đang sử dụng model: {llm.model_name}")
    print("Gõ 'exit' hoặc 'quit' để kết thúc.")
    print("==================================================")
    
    while True:
        try:
            user_q = input("\nUser: ")
            if user_q.lower() in ["exit", "quit", "q"]:
                print("Tạm biệt!")
                break
            if not user_q.strip():
                continue
            
            print("\n[Agent đang suy nghĩ và sử dụng Tools...]")
            ans = agent.run(user_q)
            print(f"\n✅ Final Answer:\n{ans}")
            
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break