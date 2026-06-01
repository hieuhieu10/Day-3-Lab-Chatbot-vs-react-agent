import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import SimpleChatbot
from src.agent.agent import ReActAgent
from src.tools.ecommerce_tools import ECOMMERCE_TOOLS

def run_comparison():
    load_dotenv()
    
    # Khởi tạo Provider
    try:
        from src.core.openai_provider import OpenAIProvider
        llm = OpenAIProvider(model_name="deepseek-v4-flash")
        print("Using OpenAI Provider (Custom Endpoint)\n" + "-"*30)
    except Exception as e:
        print(f"Không thể khởi tạo Provider. Vui lòng kiểm tra lại cấu hình .env! {e}")
        sys.exit(1)

    # Khởi tạo Baseline Chatbot (Không có tools)
    chatbot_prompt = (
        "You are an e-commerce assistant. Answer user queries. "
        "Note: You don't have access to real-time inventory or calculators. Do your best to guess."
    )
    chatbot = SimpleChatbot(llm=llm, system_prompt=chatbot_prompt)
    
    # Khởi tạo ReAct Agent (Được trang bị Tools)
    agent = ReActAgent(llm=llm, tools=ECOMMERCE_TOOLS, max_steps=5)

    # Bài toán đánh giá (Cần kiểm tra kho, mã giảm giá và tính phí ship)
    test_query = "I want to buy a macbook. Use my coupon code 'WINNER' and ship it to Hanoi. The package weighs 2kg. What is the final status and cost?"

    print("\n[PHASE 2: CHATBOT BASELINE]")
    print(">> Chatbot đang cố gắng trả lời (nhưng không có Tools). Sẽ xảy ra hiện tượng chém gió (Hallucination)...")
    chatbot_response = chatbot.run(test_query)
    print(f"Chatbot Output:\n{chatbot_response}\n")

    print("\n[PHASE 3: REACT AGENT]")
    print(">> Agent đang phân tích suy nghĩ (Thought) và sử dụng Tools (Action)...")
    agent_response = agent.run(test_query)
    print(f"\nFinal Agent Output:\n{agent_response}\n")

if __name__ == "__main__":
    run_comparison()