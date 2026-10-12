# DPIA-lite — điền trong checkpoint 5

1. Loại dữ liệu và phân loại:

Dữ liệu trong bài là synthetic: 26 hồ sơ tại data/customers.json có customer_id, name, cccd, phone, bank_account, email và related_tickets. Hồ sơ được gắn nhãn restricted trong policy của lab. Nội dung ticket trong corpus/ được xử lý như internal nhưng không tin cậy về chỉ thị, vì attacker có thể đặt payload trong HTML comment, markup, chỉ thị giả thẩm quyền hoặc chia qua hai tài liệu. public/internal/restricted là nhãn kỹ thuật của bài, không phải kết luận phân loại pháp lý.

PII gate nhận diện CCCD, SĐT, STK và email, rồi thay bằng placeholder trước cả find_injection và summarize. Tên người chưa được regex này che. Evidence: agent/pii.py:35,43,54; agent/runner.py:110; tests/test_cp3_boundary.py:5. Precision/recall đều 1.000 trên 118 entity synthetic; không suy rộng sang mọi dữ liệu tiếng Việt thực tế.

2. Mục đích xử lý và principal:

Query baseline là “Tổng hợp các ticket còn mở tuần này”. Run A dùng purpose summarize-tickets; Run B dùng support-reply để đọc hồ sơ gắn với ticket từ nguồn tin cậy. support_l1 chỉ có search_docs nên bị deny trước truy cập mapping/hồ sơ. dpo được read_customer cho purpose hợp lệ. billing có quyền/purpose khác và không mặc nhiên được cho phép support-reply. Principal lấy từ data/principals.json, không lấy từ chỉ thị trong corpus.

Mỗi yêu cầu tạo request ID; mỗi vùng xử lý có agent_id/run_id riêng, expires_at bằng thời điểm tạo cộng 5 phút. Policy kiểm giao scope, purpose và TTL trước tool call; unit test kiểm cả quyền parent khi delegation_depth > 0. --as chỉ chọn fixture mô phỏng, chưa xác thực người dùng thật. Evidence: agent/runner.py:82,83,86,88; agent/policy.py:70,73,76,78,81; tests/test_obo.py.

3. Dữ liệu đi qua những run/tool nào, endpoint nào:

Run A: query đi vào search_docs; kết quả chứa ID filename và text ticket. PII được che trước khi đưa text vào LLM. Run A có scope search_docs, không có scope đọc private store hoặc http_post. Chỉ danh sách số ticket rút từ tên file được truyền sang Run B, không truyền text tự do hay customer ID mà attacker nêu trong ticket.

Run B: authorize read_customer trước cả việc mở mapping trong data/customers.json. Sau allow, ánh xạ ticket IDs với related_tickets rồi authorize từng read_customer(customer_id). Mapping hiện nằm chung file với hồ sơ nên việc tra mapping tải toàn bộ JSON vào bộ nhớ dưới principal được cho phép; đây không phải kho mapping tách riêng hay cơ chế tối thiểu hóa việc tải hồ sơ hoàn chỉnh. Hồ sơ đọc được giữ trong Run B, không đưa lại vào LLM, phần tổng hợp hoặc body gửi sink.

Một vùng egress-probe riêng chỉ dùng URL nhận diện từ lure để xin phép http_post, không nhận hồ sơ. Restricted + egress bị policy deny; lần replay cuối không có POST tới sink. Endpoint duy nhất tool cho phép là http://127.0.0.1:10024, chỉ dành cho lab; allowlist localhost không phải chứng cứ đủ về containment. Chế độ --mock không gọi API LLM ngoài máy. Nếu chọn --model thì RealLLM có thể gửi text ticket đã che regex tới Anthropic; phần tùy chọn đó chưa được đánh giá trong bài nộp.

Ledger lưu timestamp, identity, TTL, tool, classification, decision, reason và args_hash; không lưu args thô hay hồ sơ khách hàng. Các log before chứa PII synthetic theo yêu cầu chứng minh baseline; after rỗng. Evidence: agent/runner.py:93,97,112,120,128,134,143; agent/tools.py:68,77; reports/attack-before.log:1; reports/attack-after.log (0 byte).

4. Bằng chứng deny/allow và giới hạn của mock:

Lần kiểm tra cuối chạy toàn suite trước, sau đó reset sink lần nữa và replay đúng query trên bằng --mock --as dpo. reports/cp5-tests.log ghi 34 passed, không skip; reports/cp5-lures.log ghi 4/4 lure sẵn sàng. Các test injection kiểm 4 biến thể dưới cả support_l1 và dpo; test_split xác nhận không đọc KH-000777 chỉ vì nó xuất hiện trong free text và vẫn đọc được khách gắn với ticket hợp lệ.

Ledger cuối có search_docs allow dòng 160, mapping read_customer allow dòng 161, các read_customer allow dòng 162–182, và http_post deny dòng 183 với reason Restricted data must never enter a run with egress enabled, on_behalf_of=dpo. Log after 0 byte; ledger.verify=True. Evidence cụ thể: reports/cp5-evidence.json, reports/cp5-ledger.log và reports/cp5-replay.log. Trước containment, reports/attack-before.log có 4 record POST synthetic KH-000999; hash file before được giữ nguyên trong lần kiểm tra cuối.

Run A/B là các vùng xử lý logic trong cùng tiến trình Python; chưa có sandbox OS cưỡng chế. Mock deterministic không chứng minh mọi model thật đều an toàn. Che bằng regex có thể bỏ sót định dạng PII khác; scope/TTL không thay thế authentication. Hash chain phát hiện sửa dòng mà không tính lại hash, nhưng không phát hiện cắt đuôi hoặc viết lại cả file nếu thiếu mốc ngoài file. Không có quy trình production về đồng ý, quyền truy cập/xóa dữ liệu, lưu giữ, thông báo sự cố hay xử lý xuyên biên giới. Khi triển khai thực tế cần đánh giá riêng các phần đó. DPIA-lite này là bản đồ dữ liệu/rủi ro của lab, không phải hồ sơ đánh giá tác động pháp lý hoàn chỉnh.
