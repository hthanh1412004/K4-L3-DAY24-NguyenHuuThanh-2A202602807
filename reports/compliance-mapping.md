# Compliance mapping — điền trong checkpoint 5

| Nguồn / yêu cầu | Control đã làm | Evidence file:dòng | Giới hạn |
|---|---|---|---|
| Luật 91/2025/QH15 | Che CCCD, SĐT, STK, email trước LLM; kiểm purpose/quyền trước đọc hồ sơ; chặn egress restricted. | agent/pii.py:43,54; agent/runner.py:110,131,140; agent/policy.py:62,73; reports/ledger.jsonl:183; reports/attack-after.log (0 byte). | Chưa xác minh điều khoản cụ thể. Bài chưa có quy trình đồng ý và quyền chủ thể dữ liệu dùng thực tế. |
| NĐ 356/2025/NĐ-CP | Ghi loại dữ liệu, mục đích, luồng xử lý trong DPIA-lite; ledger giữ args_hash và allow/deny. | reports/dpia-lite.md:5,11,17,27; agent/runner.py:93,97; agent/ledger.py:45,64; reports/ledger.jsonl:160,161,183. | restricted là nhãn lab. DPIA-lite chưa phải hồ sơ đánh giá tác động theo mẫu pháp lý. Điều khoản cụ thể chưa xác minh. |
| Luật AI 134/2025/QH15 | Policy giới hạn hành động; tách luồng text ticket và hồ sơ khách; ghi lại các quyết định. | agent/runner.py:85,93,112,128; agent/policy.py:76,78,84; tests/test_obo.py:51; tests/test_split.py:75; reports/cp5-tests.log. | Chưa xác minh điều khoản, phân loại rủi ro pháp lý hoặc nghĩa vụ đánh giá/chứng nhận. Chỉ chạy mock. |
| OWASP ASI01 — Agent Goal Hijack | Run B lấy customer ID từ related_tickets theo số ticket của tên file. Lời attacker không quyết định khách cần đọc. PEP chặn http_post. | agent/runner.py:112,116,128,136; agent/policy.py:62; tests/test_split.py:75; tests/test_injection.py:71; reports/ledger.jsonl:183. | 4 biến thể × 2 principal, dùng dữ liệu mẫu. KH-000999 vẫn được dpo đọc hợp lệ vì gắn với ticket; PEP chặn gửi ra sink. Run A/B chưa có sandbox OS. |
| OWASP ASI03 — Identity & Privilege Abuse | Tra principal từ fixture; kiểm giao allowed_tools, agent_scopes và parent_scopes, purpose, TTL; ghi identity/reason vào ledger. | data/principals.json:2,4; agent/policy.py:70,73,76,78,81; agent/runner.py:88,95; tests/test_obo.py:34,39,44,51; reports/ledger.jsonl:160,183. | --as chỉ giả lập. Runner có delegation_depth=0; giao parent scope được kiểm bằng unit test. Hash chain cần mốc ngoài file để phát hiện cắt đuôi/viết lại toàn bộ. |
| OWASP ASI04 — Agentic Supply Chain Vulnerabilities | Pin Gitleaks v8.30.1; hook quét file hiện tại; khóa 11 package với SHA256; cài lại bằng --require-hashes; quét lịch sử thấy token giả và ghi cách rotate nếu là secret thật. | .pre-commit-config.yaml:2,3,5,6,7; requirements.lock:7; .gitleaks.toml:7; reports/cp4-lock-install.log; reports/cp5-history.json:3; reports/secrets-incident.md. | Hash không đảm bảo package an toàn. Có ngoại lệ RegEnumKey báo nhầm và cache fixture Gitleaks, đã giải thích trong báo cáo CP4. Chưa làm MCP rug pull, phần đó là bonus. |

Chỉ ghi điều khoản cụ thể khi đã đối chiếu văn bản gốc. Mô phỏng kỹ thuật không tự chứng minh tuân thủ pháp luật.

Nguồn đã kiêm tra ngày 12/10/2026:

Luật 91/2025/QH15 — Bảo vệ dữ liệu cá nhân: https://vanban.chinhphu.vn/?pageid=27160&docid=214590

NĐ 356/2025/NĐ-CP — Quy định chi tiết một số điều và biện pháp thi hành Luật Bảo vệ dữ liệu cá nhân: https://chinhphu.vn/?pageid=27160&docid=216387

Luật AI 134/2025/QH15 — Luật Trí tuệ nhân tạo: https://vanban.chinhphu.vn/?pageid=27160&docid=216334

OWASP ASI01/03/04: https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/

Tên và số văn bản đã xác nhận trên trang chính thức. Bản toàn văn PDF là bản scan, chưa đôi chiếu đủ điều khoản nên không ghi số điều/khoản. Ba dòng pháp luật trong bảng là phần liên hệ với control đã làm, chưa phải kết luận đáp ứng nghĩa vụ pháp lý. Tên và mã rủi ro OWASP đã đối chiếu nguồn chính thức.

Lần chạy cuối: reports/cp5-evidence.json có query baseline, principal dpo, ledger dòng 160–183 và http_post deny dòng 183. Log after 0 byte, hash chain True. Có 22 decision read_customer allow: 1 lần cho phép tra mapping, 21 lần đọc hồ sơ. reports/cp5-replay.log có kết quả tổng hợp 45 ticket.
