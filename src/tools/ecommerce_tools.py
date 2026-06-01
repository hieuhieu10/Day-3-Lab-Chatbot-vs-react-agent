import json
from typing import Dict, Any

# Mock catalog: item_name (lowercase key) -> stock and unit price (USD)
CATALOG: Dict[str, Dict[str, Any]] = {
    "iphone": {"display_name": "iPhone", "quantity": 50, "unit_price_usd": 999.0, "weight_kg": 0.2},
    "macbook": {"display_name": "MacBook", "quantity": 12, "unit_price_usd": 1499.0, "weight_kg": 1.4},
    "airpods": {"display_name": "AirPods", "quantity": 100, "unit_price_usd": 179.0, "weight_kg": 0.05},
}

COUPONS: Dict[str, float] = {
    "WINNER": 15.0,
    "SAVE10": 10.0,
    "FREESHIP": 0.0,
}

# destination (lowercase) -> base shipping USD per kg
SHIPPING_ZONES: Dict[str, float] = {
    "hanoi": 8.0,
    "ho chi minh": 7.0,
    "saigon": 7.0,
    "bangkok": 12.0,
    "singapore": 15.0,
    "default": 20.0,
}

def check_stock(args: Dict[str, Any]) -> str:
    """Returns available quantity, unit price, and weight for a product."""
    item_name = args.get("item_name", "")
    key = item_name.strip().lower().replace(" ", "")
    
    if not key or key not in CATALOG:
        return json.dumps({"error": "No data found", "item": item_name})

    row = CATALOG[key]
    return json.dumps(
        {
            "item": row["display_name"],
            "quantity_available": row["quantity"],
            "unit_price_usd": row["unit_price_usd"],
            "weight_kg_per_unit": row["weight_kg"],
        }
    )

def get_discount(args: Dict[str, Any]) -> str:
    """Returns discount percentage for a valid coupon code."""
    coupon_code = args.get("coupon_code", "")
    code = coupon_code.strip().upper()
    
    if not code or code not in COUPONS:
        return json.dumps({"error": "No data found", "coupon_code": coupon_code})

    return json.dumps({"coupon_code": code, "discount_percent": COUPONS[code]})

def calc_shipping(args: Dict[str, Any]) -> str:
    """Calculates shipping cost in USD from total weight and destination city."""
    # Hỗ trợ lấy từ 'weight' hoặc 'weight_kg' để tránh lỗi nế LLM truyền nhầm key
    weight = float(args.get("weight", args.get("weight_kg", 0)))
    destination = args.get("destination", "").lower()
    
    if weight <= 0:
        return json.dumps({"error": "weight must be greater than 0"})

    dest_key = destination.strip().lower()
    rate = SHIPPING_ZONES.get(dest_key, SHIPPING_ZONES["default"])
    cost = round(weight * rate, 2)
    
    return json.dumps(
        {
            "destination": destination,
            "weight_kg": weight,
            "shipping_cost_usd": cost,
            "rate_per_kg_usd": rate,
        }
    )

# Danh sách tools để nạp vào ReActAgent
ECOMMERCE_TOOLS = [
    {
        "name": "check_stock",
        "description": "Look up inventory for one product. Argument MUST be a JSON string with one key: 'item_name'. Example: '{\"item_name\": \"iphone\"}'. Returns JSON with quantity, price, and weight.",
        "func": check_stock
    },
    {
        "name": "get_discount",
        "description": "Validate a coupon and return discount percent. Argument MUST be a JSON string with one key: 'coupon_code'. Example: '{\"coupon_code\": \"WINNER\"}'. Returns JSON with discount_percent.",
        "func": get_discount
    },
    {
        "name": "calc_shipping",
        "description": "Compute shipping cost in USD. Argument MUST be a JSON string with two keys: 'weight' (float, total kg) and 'destination' (string city). Example: '{\"weight\": 2.5, \"destination\": \"hanoi\"}'.",
        "func": calc_shipping
    }
]