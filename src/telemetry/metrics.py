import json
import os
import glob
from typing import Dict, Any

class MetricsAnalyzer:
    @staticmethod
    def analyze_log(log_file: str) -> Dict[str, Any]:
        if not os.path.exists(log_file):
            return {"error": "Log file not found"}

        total_latency = 0
        total_tokens = 0
        llm_calls = 0
        agent_steps = 0
        
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    event = log_entry.get("event")
                    data = log_entry.get("data", {})
                    
                    if event == "LLM_RESPONSE":
                        response = data.get("response") or {}
                        total_latency += response.get("latency_ms", 0)
                        usage = response.get("usage") or {}
                        total_tokens += usage.get("total_tokens", 0)
                        llm_calls += 1
                        
                    elif event == "AGENT_END":
                        agent_steps += data.get("steps", 0)
                        
                except json.JSONDecodeError:
                    continue
                    
        return {
            "total_llm_calls": llm_calls,
            "average_latency_ms": round(total_latency / llm_calls, 2) if llm_calls > 0 else 0,
            "total_tokens_consumed": total_tokens,
            "total_agent_steps": agent_steps,
            # Ước tính chi phí dựa trên giá DeepSeek-v4-flash (~$0.15 cho 1 triệu token)
            # (Có thể điều chỉnh tỷ giá này theo mô hình bạn dùng)
            "estimated_cost_usd": round((total_tokens / 1_000_000) * 0.15, 6),
            # Tỷ lệ: số token tiêu thụ trung bình mỗi bước suy luận của Agent
            "tokens_per_step": round(total_tokens / agent_steps, 0) if agent_steps > 0 else 0
        }

if __name__ == "__main__":
    logs = glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "*.log"))
    if logs:
        latest_log = max(logs, key=os.path.getctime)
        print(f"--- Analytics for {os.path.basename(latest_log)} ---")
        metrics = MetricsAnalyzer.analyze_log(latest_log)
        print(json.dumps(metrics, indent=4))