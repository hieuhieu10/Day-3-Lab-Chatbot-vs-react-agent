"""Run the ReAct agent with sample tools."""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.sample_tools import calculator, weather_lookup, tax_calculator
from src.telemetry.logger import logger

load_dotenv()

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate math expressions. Use like: calculator(2 + 3 * 4)",
        "function": calculator,
    },
    {
        "name": "weather_lookup",
        "description": "Get current weather for a city. Use like: weather_lookup(hanoi)",
        "function": weather_lookup,
    },
    {
        "name": "tax_calculator",
        "description": "Calculate tax. Use like: tax_calculator(100, 0.1)",
        "function": tax_calculator,
    },
]


def run_agent(message: str) -> str:
    """Run the ReAct agent on a single message."""
    provider = OpenAIProvider(
        model_name=os.getenv("MODEL", "gpt-4o"),
        api_key=os.getenv("API_KEY")
    )
    agent = ReActAgent(llm=provider, tools=TOOLS, max_steps=8)
    response = agent.run(message)
    return response


if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = "I want to buy an iPhone that costs $999. Calculate 10% tax on it. What is the total price? Also, what's the weather in Hanoi?"

    print(f"User: {message}")
    print("Agent: ", end="", flush=True)
    response = run_agent(message)
    print(response)
