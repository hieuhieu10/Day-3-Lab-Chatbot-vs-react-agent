# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Team League of Mini Demons
- **Team Members**: Đỗ Quốc An, Nguyễn Khánh Linh, Trần Khánh Linh, Thân Minh Hiếu
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: 100% trên các kịch bản kiểm thử đa bước (Multi-step scenarios).
- **Key Outcome**: Môi trường Agent sử dụng cơ chế ReAct vượt trội hoàn toàn so với Baseline Chatbot. Trong khi Chatbot có xu hướng "bịa đặt" (hallucinate) dữ liệu kho hàng và giá cả khi gặp các câu hỏi yêu cầu dữ liệu thực tế, Agent của chúng tôi đã gọi chính xác chuỗi 3 công cụ (kiểm tra kho, lấy mã giảm giá, tính phí ship) để đưa ra câu trả lời chính xác cuối cùng.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
Hệ thống hoạt động dựa trên vòng lặp **Thought-Action-Observation** (Tối đa `max_steps=5`). 
1. **Thought**: LLM phân tích câu hỏi và quyết định công cụ cần sử dụng.
2. **Action**: LLM tạo ra chuỗi gọi công cụ dưới định dạng JSON. Parser v2 của chúng tôi tự động làm sạch các ký tự markdown thừa (như ```json) trước khi parse.
3. **Observation**: Kết quả thực thi công cụ được trả về dưới dạng chuỗi và đưa lại vào Prompt để LLM suy luận bước tiếp theo.

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `check_stock` | `json` | Kiểm tra số lượng tồn kho của một sản phẩm (VD: macbook). |
| `get_discount` | `json` | Tra cứu phần trăm giảm giá dựa vào mã coupon. |
| `calc_shipping` | `json` | Tính toán chi phí vận chuyển dựa trên cân nặng và điểm đến. |

### 2.3 LLM Providers Used
- **Primary**: `deepseek-v4-flash` (Thông qua OpenAI SDK Custom Endpoint `https://opencode.ai/zen/go/v1`).
- **Secondary (Backup)**: `gemini-1.5-flash` (Được cấu hình làm Fallback Provider nếu DeepSeek gặp sự cố).

---

## 3. Telemetry & Performance Dashboard

*Dữ liệu được trích xuất từ `src/telemetry/metrics.py` trong quá trình chạy bộ test.*

- **Average Latency (P50)**: ~1500ms / LLM call
- **Total Agent Steps (Average)**: ~3.5 steps cho một truy vấn E-commerce phức tạp.
- **Average Tokens per Task**: ~450 tokens / step (Bao gồm Prompt chứa Tool Descriptions và Context lịch sử).
- **Estimated Cost USD**: Đạt mức rất thấp (~$0.0003 mỗi lượt chạy) nhờ tối ưu sử dụng model `deepseek-v4-flash` ($0.15 / 1M tokens).

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study: Lỗi định dạng JSON (Hallucinated Markdown Argument)
- **Input**: "I want to buy a macbook."
- **Observation**: Tool Executor báo lỗi `JSONDecodeError` và trả về `Error: Invalid JSON arguments provided for check_stock. Received: ```json {"item_name": "macbook"} ``` `
- **Root Cause**: LLM tự động bọc payload của Action trong khối Code Block của Markdown để tối ưu hiển thị giao diện người dùng, nhưng hàm `json.loads()` của Python không hiểu định dạng này.
- **Fix Implementation**: Cải tiến Agent v1 lên **Agent v2**. Viết thêm logic tiền xử lý đầu vào trong hàm `_execute_tool()`: `clean_args = args.strip(" \n'\"`")` và loại bỏ tiền tố `json`, kèm theo Try-Catch để Agent tự sửa lỗi ở step tiếp theo.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Chatbot vs Agent trên cùng 1 Test Case
**Test Case**: *"I want to buy a macbook. Use my coupon code 'WINNER' and ship it to Hanoi. The package weighs 2kg. What is the final status and cost?"*
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| **Simple Q** (Hỏi đáp thông thường) | Trả lời nhanh chóng, tự nhiên. | "Overthink", tốn token để suy luận. | **Chatbot** |
| **Multi-step** (Thương mại điện tử) | Bịa ra phí ship 5$ và giảm giá ảo 20%. | Gọi 3 Tools thành công, tính toán chuẩn xác phí ship 7$. | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: Đã tích hợp Try-Catch cho JSON parsing, tuy nhiên cần bổ sung Input Validation (ví dụ dùng thư viện `Pydantic`) để đảm bảo LLM không truyền mã độc hoặc Type Casting sai vào trong tham số của Tool.
- **Guardrails**: Hệ thống đã giới hạn `max_steps = 5` để ngăn chặn Agent rơi vào vòng lặp vô hạn gây tiêu tốn chi phí API (Infinite Billing Loop).
- **Scaling**: Khi hệ thống mở rộng lên hàng chục E-commerce Tools, Context Window sẽ bị phình to. Giải pháp là tích hợp cơ chế Tool Retrieval (RAG) để Agent tự tìm kiếm 3-5 Tools phù hợp nhất với câu hỏi trước khi bắt đầu suy luận.