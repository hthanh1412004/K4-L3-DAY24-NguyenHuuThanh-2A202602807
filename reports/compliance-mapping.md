# Compliance mapping — điền trong checkpoint 5

| Nguồn / yêu cầu | Control đã làm | Evidence file:dòng | Giới hạn |
|---|---|---|---|
| Luật 91/2025/QH15 — Bảo vệ dữ liệu cá nhân | Đối chiếu kỹ thuật do người làm bài suy luận: che CCCD, SĐT, STK, email trước LLM; kiểm mục đích/quyền trước đọc hồ sơ; chặn egress dữ liệu restricted. | agent/pii.py:43,54; agent/runner.py:110,131,140; agent/policy.py:62,73; reports/ledger.jsonl:183; reports/attack-after.log (0 byte). | Đã xác nhận văn bản và nguồn chính thức; chưa xác minh điều khoản cụ thể từ toàn văn. Không kết luận tuân thủ, không có quy trình consent/quyền chủ thể dữ liệu production. |
| NĐ 356/2025/NĐ-CP — Quy định chi tiết một số điều và biện pháp thi hành Luật Bảo vệ dữ liệu cá nhân | Đối chiếu kỹ thuật: lập bản đồ dữ liệu, mục đích, nơi đi và quyết định allow/deny trong DPIA-lite; giữ args_hash thay vì PII thô trong ledger. | reports/dpia-lite.md:5,11,17,27; agent/runner.py:93,97; agent/ledger.py:45,64; reports/ledger.jsonl:160,161,183. | Đã xác nhận văn bản; chưa xác minh điều khoản cụ thể. restricted là nhãn của lab, không tự đồng nhất với phân loại pháp lý. DPIA-lite này không phải hồ sơ đánh giá tác động theo mẫu pháp lý. |
| Luật AI 134/2025/QH15 — Luật Trí tuệ nhân tạo | Đối chiếu kỹ thuật: giới hạn quyền hành động của agent qua policy, tách luồng xử lý nội dung không tin cậy/hồ sơ riêng và lưu dấu vết quyết định. | agent/runner.py:85,93,112,128; agent/policy.py:76,78,84; tests/test_obo.py:51; tests/test_split.py:75; reports/cp5-tests.log. | Đã xác nhận văn bản; chưa xác minh điều khoản cụ thể. Chưa xác định phân loại rủi ro pháp lý của hệ thống hay nghĩa vụ đánh giá/chứng nhận; mock không phải triển khai AI production. |
| OWASP ASI01 — Agent Goal Hijack | Run B chỉ nhận ID ticket lấy từ tên file và ánh xạ từ related_tickets tin cậy; chỉ thị trong ticket không quyết định customer ID. PEP chặn http_post trước thực thi. | agent/runner.py:112,116,128,136; agent/policy.py:62; tests/test_split.py:75; tests/test_injection.py:71; reports/ledger.jsonl:183. | 4 biến thể × 2 principal đã được replay; phạm vi là mock và fixtures. Run A/B là vùng xử lý logic trong một tiến trình, chưa cách ly bằng sandbox OS. KH-000999 vẫn có thể được dpo đọc hợp lệ vì gắn với ticket; PEP mới chặn chặng egress. |
| OWASP ASI03 — Identity & Privilege Abuse | Principal tra từ fixture tin cậy; giao allowed_tools với agent_scopes và parent_scopes khi có delegation; kiểm purpose và TTL trước tool call. Mọi decision lưu identity/reason. | data/principals.json:2,4; agent/policy.py:70,73,76,78,81; agent/runner.py:88,95; tests/test_obo.py:34,39,44,51; reports/ledger.jsonl:160,183. | --as chỉ mô phỏng principal, không có authentication production. Runner hiện dùng delegation_depth=0; giao parent scopes được kiểm bằng unit test policy. Hash chain không phát hiện cắt đuôi/viết lại toàn bộ nếu thiếu mốc tin cậy ngoài file. |
| OWASP ASI04 — Agentic Supply Chain Vulnerabilities | Pin Gitleaks v8.30.1; hook quét file hiện tại; khóa 11 package với SHA256 và cài lại bằng --require-hashes; quét lịch sử phát hiện token giả; ghi cách rotate nếu là secret thật. | .pre-commit-config.yaml:2,3,5,6,7; requirements.lock:7; .gitleaks.toml:7; reports/cp4-lock-install.log; reports/cp5-history.json:3; reports/secrets-incident.md. | Hash kiểm tra artifact, không chứng minh package an toàn. Ngoại lệ scanner chỉ áp dụng finding hàm RegEnumKey đã xác minh và cache fixture Gitleaks; quét lịch sử vẫn có một finding synthetic. Chưa kiểm thử MCP rug pull; đây là bonus. |

Chỉ ghi điều khoản cụ thể khi đã đối chiếu văn bản gốc. Mô phỏng kỹ thuật không tự chứng minh tuân thủ pháp luật.

Nguồn chính thức kiểm tra ngày 12/10/2026

Luật 91/2025/QH15: https://vanban.chinhphu.vn/?pageid=27160&docid=214590

NĐ 356/2025/NĐ-CP: https://chinhphu.vn/?pageid=27160&docid=216387

Luật AI 134/2025/QH15: https://vanban.chinhphu.vn/?pageid=27160&docid=216334

OWASP: https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/

Ba dòng pháp luật là liên hệ kỹ thuật do người làm bài suy luận, không diễn giải một điều khoản chưa kiểm được. Các trang chính thức xác nhận tên/số văn bản; bản PDF toàn văn là bản scan, chưa đối chiếu đủ nội dung điều khoản để ghi số điều/khoản. Các mục ASI01/03/04 và tên rủi ro đã đối chiếu nguồn OWASP chính thức.

Evidence cuối: reports/cp5-evidence.json xác nhận query baseline, principal dpo, ledger dòng 160–183, http_post deny dòng 183, log after 0 byte và hash chain True. Có 22 decision read_customer allow, gồm một lần cho phép truy cập mapping và 21 lần đọc hồ sơ. Kết quả tổng hợp 45 ticket nằm trong reports/cp5-replay.log.
