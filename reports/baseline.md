CP1 - Phân tích baseline

1. Agent đã có identity riêng cho mỗi lần chạy chưa?
   Chưa có. \_naive_loop(message, llm) chỉ nhận câu hỏi và LLM, không tạo agent_id/run_id và chưa kiêm tra scope hay thời hạn trước khi đọc hồ sơ (agent/loop.py:27,39). CLI có principal nhưng nhánh fallback không truyền xuống (agent/loop.py:74). Cờ --as chỉ chọn principal giả lập.

2. Ai là người cho phép gọi http_post?
   Baseline không kiểm tra quyền gọi. Nó thấy chỉ thị trong ticket thì lấy customer ID, đọc hô sơ rồi gửi luôn (agent/loop.py:34,37,39,44). http_post chỉ kiểm URL thuộc http://127.0.0.1:10024, không kiểm dữ liệu có được phép gửi hay không (agent/tools.py:76,84).

3. Bằng chứng nào cho thấy dữ liệu đã bị gửi sai?
   agent/loop.py:44 dựng body {"records": collected}, agent/tools.py:84 gửi POST, còn sink ghi path và body vào log (sink/sink.py:37,44,47). Dòng 1 reports/attack-before.log có POST /reconcile chứa KH-000999 cùng cccd, phone, bank_account. Câu hỏi chỉ yêu cầu tổng hợp ticket nhưng agent lại gửi hồ sơ khách. Toàn bộ dữ liệu này là synthetic của bài.

SHA: 3366966ed745135114c5d699e98297916295caea
