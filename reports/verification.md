# Verification

## CP3 — kiểm tra ngày 12/10/2026

- OS: Windows, Python 3.11.9 (`.venv/Scripts/python.exe`).
- Lệnh kiểm tra:

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_pii.py tests/test_policy.py tests/test_obo.py tests/test_split.py tests/test_ledger.py tests/test_injection.py tests/test_scaffold_dispatch.py tests/test_cp3_boundary.py -q -s
  ```

- Kết quả: **28 passed**, không skip. Log: reports/cp3-tests.log.
- PII: gold=118, pred=118, tp=118; precision=1.000, recall=1.000 trên bộ synthetic của bài.
- PII được che trước cả llm.find_injection() và llm.summarize(); regression test: tests/test_cp3_boundary.py.
- OBO chạy thử: support_l1 đọc 0 hồ sơ; dpo đọc 21 hồ sơ gắn với ticket hợp lệ. Cả hai vẫn trả về tổng hợp 45 ticket.
- Run B nhận ID ticket lấy từ tên file, tra related_tickets trong nguồn tin cậy
- Ledger: 27 dòng trong reports/ledger.jsonl; mọi dòng có reason, on_behalf_of, agent_id, run_id, expires_at; 2 decision deny cho http_post.
- ledger.verify() trên evidence thật: **True**. Sửa thêm một ký tự vào reason của dòng giữa trong bản sao: **False**. Bản sao thử nghiệm đã được xóa, ledger gốc giữ nguyên.
- Thống kê lần chạy: reports/cp3-evidence.json.
- Không thấy lỗi trong phạm vi kiểm tra CP3. Kết quả mock/synthetic không chứng minh độ chính xác PII trên dữ liệu thực hoặc authentication production. Hash chain không phát hiện cắt đuôi/viết lại toàn bộ nếu không có mốc tin cậy bên ngoài.

## Kiểm tra toàn bài

Gitleaks version: 8.30.1, đã xác minh ở CP4.

.venv/Scripts/python.exe -X utf8 -m pytest tests/ -q -s: 34 passed, không skip. Log: reports/cp4-tests.log.

pre-commit run --all-files: Passed, exit code 0. Log: reports/cp4-pre-commit.log. Gitleaks binary cần có trong PATH khi chạy hook.

Báo cáo compliance-mapping và DPIA-lite của CP5 còn cần hoàn thiện.

CP4 — Supply chain và secrets, ngày 12/10/2026

Gitleaks Windows x64 v8.30.1 tải từ release chính thức; SHA256 archive khớp checksum chính thức. Bằng chứng: reports/cp4-scanner-download.log.

Quét lịch sử: 1 finding lab24-synthetic-token ở commit 1bdd849922156c868a5ee9293d68f5b72e242d2c, file lab-fake-secret.txt dòng 1; exit code 1 đúng dự kiến. Không phải credential thật. Bằng chứng: reports/cp4-history.json và reports/cp4-history.log.

Quét thư mục hiện tại: 0 finding, exit code 0. Bằng chứng: reports/cp4-current.json và reports/cp4-current.log. Ngoại lệ gồm đúng fingerprint báo nhầm hàm RegEnumKey của setuptools và cache repo Gitleaks do pre-commit tải về chứa fixture secret. Chi tiết và phạm vi ngoại lệ được ghi trong reports/secrets-incident.md; mã bài làm và token giả trong lịch sử vẫn được quét.

Hook: repo https://github.com/gitleaks/gitleaks, rev v8.30.1, id gitleaks-system, pass_filenames: false. Entry gitleaks dir quét file hiện tại; quét lịch sử được thực hiện riêng. Khi chạy, thêm .tools/gitleaks-v8.30.1 vào PATH và dùng .venv/Scripts/python.exe -m pre_commit run --all-files.

requirements.lock: 11 package, pin phiên bản và SHA256; sinh bằng piptools compile --generate-hashes. pip install --force-reinstall --require-hashes -r requirements.lock thành công, exit code 0. Bằng chứng: reports/cp4-lock-build.log và reports/cp4-lock-install.log. Hash không chứng minh package không có lỗ hổng; pin và hook không thay thế rotate nếu credential thật đã lộ.

Môi trường ban đầu có proxy không hoạt động và PIP_NO_INDEX; các tiến trình tải dependency được chạy với môi trường con bỏ những thiết lập đó, dùng PyPI chính thức. Thiết lập toàn hệ thống không bị thay đổi.

Lần chạy toàn test đầu tiên qua subprocess dùng encoding cp1252 đã lỗi UnicodeEncodeError khi CLI in ký tự tiếng Việt. Chạy lại bằng -X utf8 giải quyết lỗi môi trường, toàn bộ 34 test pass; không sửa test để tạo kết quả pass.

Tóm tắt máy đọc được: reports/cp4-evidence.json. Báo cáo sự cố: reports/secrets-incident.md. CP4 đã hoàn tất các kiểm tra trên; chưa commit/push.
