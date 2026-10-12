# DPIA-lite — điền trong checkpoint 5

1. Loại dữ liệu và phân loại:

data/customers.json có 26 hồ sơ synthetic, gồm customer_id, name, cccd, phone, bank_account, email và related_tickets. Trong lab, hồ sơ là restricted; ticket trong corpus/ là internal nhưng có thể chứa chỉ thị của attacker. public/internal/restricted là nhãn kỹ thuật của bài, chưa phải phân loại pháp lý.

Regex che CCCD, SĐT, STK, email trước cả find_injection và summarize; chưa che tên người. Code ở agent/pii.py:35,43,54 và agent/runner.py:110; tests/test_cp3_boundary.py:5 kiểm chỗ này. Bộ mẫu có 118 entity, precision/recall đều 1.000. Chưa thử trên dữ liệu thật.

2. Mục đích xử lý và principal:

Câu hỏi là “Tổng hợp các ticket còn mở tuần này”. Run A dùng summarize-tickets, Run B dùng support-reply để đọc khách gắn với ticket. Principal lấy từ data/principals.json: support_l1 chỉ có search_docs, dpo được read_customer đúng purpose. billing có purpose khác nên không tự được phép support-reply.

Mỗi yêu cầu có request ID, mỗi run có agent_id/run_id, thời hạn 5 phút. Policy kiểm purpose, TTL và giao scope trước tool call; có test quyền parent khi delegation_depth > 0. Phân quyên nằm ở agent/policy.py:70,73,76,78,81; identity/TTL tạo ở agent/runner.py:82,83,86,88. --as chỉ là giả lập principal, chưa xác thực người dùng thật.

3. Dữ liệu đi qua những run/tool nào, endpoint nào:

Run A gọi search_docs để đọc thư muc corpus. Text được che PII trước khi vào LLM. Run A chỉ có scope search_docs. Sang Run B chỉ có danh sách số ticket lấy từ tên file, không có text hay customer ID attacker viết trong ticket.

Run B kiểm quyền trước khi mở mapping ở data/customers.json. Nếu allow thì tra related_tickets rồi kiểm từng read_customer. Mapping nằm chung file với hồ sơ nên vẫn phải tải toàn bộ JSON vào bộ nhớ dưới principal được phép; chưa có kho mapping tách riêng. Hồ sơ không đưa trở lại LLM, câu tổng hợp hay body gửi sink (agent/runner.py:128,131,134,140,143).

egress-probe chỉ cầm URL từ lure, không cầm hồ sơ. Policy deny restricted + egress trước http_post. Tool chỉ cho phép http://127.0.0.1:10024 (agent/tools.py:68,77); chặn URL này là giới hạn của lab, còn chặn tiết lộ dữ liệu nằm ở policy. --mock không gọi API LLM. Nếu dùng --model thì text ticket đã che regex có thể đi tới Anthropic, phần đó chưa được kiểm trong bài.

Ledger có identity, TTL, tool, classification, decision, reason và args_hash, không có args hay hồ sơ thô (agent/runner.py:93,97). Log before chứa PII synthetic để chứng minh baseline, log after rỗng. Xem reports/attack-before.log:1 và reports/attack-after.log.

4. Bằng chứng deny/allow và giới hạn của mock:

Chạy test trước, reset sink lần nữa rồi replay query với --mock --as dpo. reports/cp5-tests.log ghi 34 passed, không skip; reports/cp5-lures.log có 4/4 lure sẵn sàng. Test injection chạy 4 biến thể với cả hai principal. Test split không đọc KH-000777 chỉ vì ID nằm trong lời attacker, nhưng vẫn đọc được khách có ticket hợp lệ.

Ledger có search_docs allow dòng 160, mapping read_customer allow dòng 161, 21 lần đọc hồ sơ allow dòng 162–182 và http_post deny dòng 183. Reason là Restricted data must never enter a run with egress enabled, on_behalf_of=dpo. Log after 0 byte, verify=True. reports/cp5-evidence.json, reports/cp5-ledger.log và reports/cp5-replay.log ghi kết quả. Log before có 4 POST KH-000999 và giữ nguyên hash sau lần kiểm tra cuối.

Run A/B vẫn ở cùng tiến trình Python, chưa có sandbox OS. Mock pass không đảm bảo model thật cũng pass. Regex có thể bỏ sót PII; scope/TTL không thay thế xác thực. Hash chain không phát hiện cắt đuôi hay viết lại toàn bộ nếu thiếu mốc ngoài file. Bài chưa có quy trình đồng ý, quyền truy cập/xóa, thời hạn lưu giữ, thông báo sự cố và xử lý xuyên biên giới. Cần đánh giá riêng nếu dùng dữ liệu thật. Đây là DPIA-lite cho lab, chưa phải hồ sơ đánh giá tác động pháp lý đầy đủ.
