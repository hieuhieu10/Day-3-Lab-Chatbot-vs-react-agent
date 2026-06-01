"""Sample tools for the ReAct agent."""
import math


def calculator(expression: str) -> str:
    """Evaluate a math expression. Supports: +, -, *, /, **, sqrt, pi, e."""
    allowed = {
        "sqrt": math.sqrt, "abs": abs, "round": round,
        "pow": pow, "pi": math.pi, "e": math.e,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


def weather_lookup(location: str) -> str:
    """Return mock weather data for a location. Format: 'Sunny, 30C'."""
    mock_data = {
        "hanoi": "Sunny, 30°C",
        "saigon": "Rainy, 32°C",
        "danang": "Cloudy, 28°C",
        "tokyo": "Sunny, 22°C",
        "new york": "Cold, 5°C",
        "london": "Rainy, 10°C",
    }
    key = location.strip().lower()
    return mock_data.get(key, f"Weather data unavailable for {location}")


def tax_calculator(amount: float, rate: float = 0.1) -> str:
    """Calculate tax. Default rate is 10%. Returns formatted tax and total."""
    try:
        amount = float(amount)
        rate = float(rate)
        tax = amount * rate
        total = amount + tax
        return f"Tax: {tax:.2f}, Total: {total:.2f}"
    except (ValueError, TypeError) as e:
        return f"Error: {e}"
