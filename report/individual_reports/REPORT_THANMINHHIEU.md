# Phase 2 Report: Chatbot Baseline

- **Lab**: Lab 3 - Chatbot vs ReAct Agent
- **Phase**: Phase 2 - Chatbot Baseline
- **Date**: 01/06/2026
- **Model Used**: `deepseek-v4-flash`
- **Main File**: `src/chatbot.py`

---

## 1. Objective

Mục tiêu của Phase 2 là chạy chatbot baseline với các câu hỏi phức tạp để quan sát giới hạn của mô hình LLM khi không có cơ chế agentic reasoning. Theo `INSTRUCTOR_GUIDE.md`, giai đoạn này không nhằm tối ưu chatbot đến mức hoàn hảo, mà nhằm chứng minh rằng prompt engineering đơn thuần chưa đủ cho các tác vụ nhiều bước cần dữ liệu chính xác.

Trong project này, chatbot baseline được triển khai trong `src/chatbot.py` bằng class `SimpleChatbot`. Chatbot chỉ gọi LLM trực tiếp một lần cho mỗi câu hỏi của người dùng, không có tool execution, không có `Observation`, và không có vòng lặp `Thought - Action - Observation`.

---

## 2. Baseline Chatbot Design

Chatbot baseline sử dụng system prompt:

```text
You are a helpful e-commerce assistant. Try to answer the user's questions about stock, discounts, and shipping.
```

Luồng xử lý của chatbot:

1. Nhận câu hỏi từ người dùng.
2. Gọi LLM provider bằng `llm.generate(...)`.
3. Ghi log phản hồi LLM.
4. Trả câu trả lời trực tiếp cho người dùng.

Điểm quan trọng là chatbot không có quyền gọi các công cụ như kiểm tra tồn kho, lấy mã giảm giá hay tính phí vận chuyển. Vì vậy, nếu user hỏi về dữ liệu cụ thể, chatbot chỉ có thể dựa vào kiến thức hoặc suy đoán từ model.

---

## 3. Test Cases

Các test case được dùng để đánh giá chatbot baseline tập trung vào bài toán e-commerce nhiều bước, đúng theo kịch bản gợi ý trong instructor guide.

| Test Case | User Query | Expected Behavior |
| :--- | :--- | :--- |
| Simple Q&A | "Hello, can you help me?" | Chatbot trả lời nhanh, tự nhiên. |
| Tax Calculation | "Calculate 10 percent tax on 500 dollars" | Chatbot có thể tính được nếu bài toán đơn giản. |
| Weather + Calculation | "What is the weather in Tokyo and calculate tax on 1000" | Chatbot dễ trộn lẫn dữ liệu thật và dữ liệu suy đoán. |
| E-commerce Multi-step | "I want to buy an iPhone that costs $999. Calculate 10% tax on it. What is the total price? Also, what's the weather in Hanoi?" | Chatbot có thể tính phần toán học nhưng không có nguồn dữ liệu chắc chắn cho weather. |
| Tool-like E-commerce | "I want to buy a macbook. Use my coupon code WINNER and ship it to Hanoi. The package weighs 2kg. What is the final status and cost?" | Chatbot cần tồn kho, discount và shipping nhưng không thể gọi tool để xác minh. |

---

## 4. Observations

### 4.1 Strengths

Chatbot baseline hoạt động tốt với các câu hỏi đơn giản hoặc câu hỏi chỉ cần trả lời ngôn ngữ tự nhiên. Với bài toán tính toán trực tiếp như tính 10% của 500, model có thể tự suy luận và trả lời mà không cần tool.

Chatbot cũng có ưu điểm về tốc độ triển khai. Code ngắn, dễ chạy, dễ hiểu và không cần parser cho action/tool. Đây là baseline phù hợp để so sánh với ReAct Agent ở các phase sau.

### 4.2 Limitations

Hạn chế lớn nhất là chatbot không có khả năng hành động. Khi gặp câu hỏi yêu cầu dữ liệu thực tế như tồn kho MacBook, mã giảm giá `WINNER`, hoặc phí ship tới Hanoi, chatbot không thể kiểm tra dữ liệu từ hệ thống. Nó có thể tạo ra câu trả lời nghe hợp lý nhưng không được xác minh.

Chatbot cũng không có cơ chế tự sửa lỗi. Nếu câu trả lời ban đầu sai hoặc thiếu dữ liệu, nó không nhận được `Observation` từ môi trường để điều chỉnh bước tiếp theo. Điều này khác với ReAct Agent, nơi mỗi tool call tạo ra một observation để model tiếp tục suy luận.

---

## 5. Log and Metrics Review

Log trong `logs/2026-06-01.log` cho thấy nhiều lượt chạy chatbot baseline với event `CHATBOT_RESPONSE`. Một số chỉ số latency và token được ghi nhận:

| Event | Tokens | Latency |
| :--- | ---: | ---: |
| `CHATBOT_RESPONSE` | 604 | 10030 ms |
| `CHATBOT_RESPONSE` | 942 | 7899 ms |
| `CHATBOT_RESPONSE` | 1737 | 16724 ms |
| `CHATBOT_RESPONSE` | 2173 | 20811 ms |
| `CHATBOT_RESPONSE` | 313 | 4116 ms |
| `CHATBOT_RESPONSE` | 3249 | 27118 ms |

Các log này cho thấy chatbot baseline có thể tiêu tốn khá nhiều token khi cố trả lời các câu hỏi nhiều bước. Tuy nhiên, token cao không đồng nghĩa với độ chính xác cao, vì chatbot vẫn không có tool để xác minh dữ liệu.

Một điểm cần cải thiện là format log của chatbot nên thống nhất với agent version mới. Hiện `src/chatbot.py` ghi `CHATBOT_START`, `LLM_RESPONSE`, và `CHATBOT_END`, trong khi log cũ có các event như `CHATBOT_RESPONSE`. Việc thống nhất event name sẽ giúp phân tích metrics giữa chatbot và agent công bằng hơn.

---

## 6. Baseline Result

Kết quả Phase 2 cho thấy chatbot baseline phù hợp với:

- Câu hỏi đơn giản.
- Hội thoại tự nhiên.
- Bài toán tính toán nhỏ không cần dữ liệu ngoài.
- Trường hợp cần phản hồi nhanh và không cần tool.

Nhưng chatbot baseline không phù hợp với:

- Truy vấn nhiều bước.
- Bài toán cần kiểm tra dữ liệu hệ thống.
- Tác vụ cần gọi công cụ.
- Tình huống cần self-correction dựa trên lỗi từ môi trường.

Vì vậy, nếu chỉ dùng chatbot, hệ thống có nguy cơ hallucinate tồn kho, giá, mã giảm giá hoặc phí vận chuyển.

---

## 7. Key Insight for Phase 3

Phase 2 chứng minh lý do cần chuyển từ chatbot sang ReAct Agent. Chatbot giỏi nói chuyện, nhưng agent cần khả năng hành động. Với ReAct, model không chỉ sinh câu trả lời mà còn có thể:

1. Suy nghĩ bước tiếp theo bằng `Thought`.
2. Chọn công cụ bằng `Action`.
3. Nhận kết quả thật bằng `Observation`.
4. Lặp lại cho đến khi đủ thông tin để trả lời bằng `Final Answer`.

Do đó, Phase 2 đóng vai trò baseline quan trọng để so sánh với Phase 3. Nếu chatbot trả lời sai do thiếu dữ liệu, ReAct Agent có thể khắc phục bằng cách gọi tool như `check_stock`, `get_discount`, và `calc_shipping`.

---

## 8. Conclusion

Chatbot baseline là bước khởi đầu cần thiết để hiểu giới hạn của LLM thuần. Dù có thể trả lời tự nhiên và xử lý một số câu hỏi đơn giản, chatbot không đủ tin cậy cho các workflow nhiều bước trong môi trường production. Kết quả Phase 2 củng cố bài học chính của lab: muốn hệ thống AI giải quyết task thực tế, cần bổ sung tool usage, observability và vòng lặp reasoning có feedback từ môi trường.

