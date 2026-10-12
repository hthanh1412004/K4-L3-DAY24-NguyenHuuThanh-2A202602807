CP1 - Phân tích baseline

1. Agent đã có identity riêng cho mỗi lần chạy chưa?
   Chưa có. \_naive_loop(message, llm) chỉ nhận câu hỏi và LLM, không tạo agent_id hay run_id, cũng không kiểm tra danh tính, scope hay thời hạn trước khi đọc hồ sơ (agent/loop.py:27, agent/loop.py:39). CLI có principal mô phỏng nhưng nhánh fallback không truyền nó xuống (agent/loop.py:74), và cờ --as cũng chỉ là giả lập chứ không phải xác thực thật.

2. Ai là người cho phép gọi http_post?
   Không ai. Baseline coi chỉ thị trong ticket như lệnh: sau llm.find_injection(combined_text), nó lấy customer ID, gọi read_customer rồi gửi luôn, không qua policy nào (agent/loop.py:34, agent/loop.py:37, agent/loop.py:39, agent/loop.py:44). Còn http_post() chỉ kiểm tra URL thuộc http://127.0.0.1:10024, không quan tâm dữ liệu gửi đi (agent/tools.py:76, agent/tools.py:84).

3. Bằng chứng nào cho thấy dữ liệu đã bị gửi sai?
   Body {"records": collected} được dựng ở agent/loop.py:44 và gửi đi thật ở agent/tools.py:84. Sink ghi lại {path, body} vào reports/sink.log (sink/sink.py:37, sink/sink.py:44, sink/sink.py:47). Dòng 1 của reports/attack-before.log cho thấy POST /reconcile chứa hồ sơ synthetic KH-000999 với cccd, phone, bank_account, vượt quá mục đích chỉ tóm tắt ticket.
