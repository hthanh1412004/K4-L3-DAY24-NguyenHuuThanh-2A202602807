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

Báo cáo compliance-mapping và DPIA-lite của CP5 đã hoàn thiện; xem kết quả kiểm tra cuối ở phần CP5 bên dưới.

CP4 — Supply chain và secrets, ngày 12/10/2026

Gitleaks Windows x64 v8.30.1 tải từ release chính thức; SHA256 archive khớp checksum chính thức. Bằng chứng: reports/cp4-scanner-download.log.

Quét lịch sử: 1 finding lab24-synthetic-token ở commit 1bdd849922156c868a5ee9293d68f5b72e242d2c, file lab-fake-secret.txt dòng 1; exit code 1 đúng dự kiến. Không phải credential thật. Bằng chứng: reports/cp4-history.json và reports/cp4-history.log.

Quét thư mục hiện tại: 0 finding, exit code 0. Bằng chứng: reports/cp4-current.json và reports/cp4-current.log. Ngoại lệ gồm đúng fingerprint báo nhầm hàm RegEnumKey của setuptools và cache repo Gitleaks do pre-commit tải về chứa fixture secret. Chi tiết và phạm vi ngoại lệ được ghi trong reports/secrets-incident.md; mã bài làm và token giả trong lịch sử vẫn được quét.

Hook: repo https://github.com/gitleaks/gitleaks, rev v8.30.1, id gitleaks-system, pass_filenames: false. Entry gitleaks dir quét file hiện tại; quét lịch sử được thực hiện riêng. Khi chạy, thêm .tools/gitleaks-v8.30.1 vào PATH và dùng .venv/Scripts/python.exe -m pre_commit run --all-files.

requirements.lock: 11 package, pin phiên bản và SHA256; sinh bằng piptools compile --generate-hashes. pip install --force-reinstall --require-hashes -r requirements.lock thành công, exit code 0. Bằng chứng: reports/cp4-lock-build.log và reports/cp4-lock-install.log. Hash không chứng minh package không có lỗ hổng; pin và hook không thay thế rotate nếu credential thật đã lộ.

Môi trường ban đầu có proxy không hoạt động và PIP_NO_INDEX; các tiến trình tải dependency được chạy với môi trường con bỏ những thiết lập đó, dùng PyPI chính thức. Thiết lập toàn hệ thống không bị thay đổi.

Lần chạy toàn test đầu tiên qua subprocess dùng encoding cp1252 đã lỗi UnicodeEncodeError khi CLI in ký tự tiếng Việt. Chạy lại bằng -X utf8 giải quyết lỗi môi trường, toàn bộ 34 test pass; không sửa test để tạo kết quả pass.

Tóm tắt máy đọc được: reports/cp4-evidence.json. Báo cáo sự cố: reports/secrets-incident.md. CP4 đã được commit ở d3bf818; CP5 bổ sung hai log bắt buộc vào Git và báo cáo cuối.

CP5 — Prove và kiểm tra toàn bài ngày 12/10/2026

Lệnh tái lập: .venv/Scripts/python.exe -X utf8 -m scripts.verify_submission. Script chạy test và check_lure, rồi reset sink riêng sau test và replay đúng query “Tổng hợp các ticket còn mở tuần này” bằng --mock --as dpo. Sink chỉ nghe localhost; phần sink và ledger thật được dùng để lưu evidence, còn pytest dùng ledger riêng trong thư mục tạm.

Kết quả toàn suite: 34 passed, không fail/skip, precision=1.000 và recall=1.000 trên bộ PII synthetic. reports/cp5-tests.log lưu đầu ra. reports/cp5-lures.log xác nhận 4/4 biến thể được tìm thấy và mock nhận diện. Trường hợp cố ý thiếu ticket-904b trong unit test CLI vẫn in lỗi theo kỳ vọng nhưng test đó pass.

Log before chứa 4 POST synthetic KH-000999 tới /reconcile; script không thay đổi file này. SHA256 before: d97af1b21f949b58769d2259649885c9e1142afad18f5d446fe0f13359a54dac. reports/attack-after.log được copy từ sink sau replay cuối, rỗng 0 byte.

Ledger cuối có 183 dòng, verify=True. Lần replay cuối dưới dpo nằm ở dòng 160–183: search_docs allow dòng 160; read_customer mapping allow dòng 161; 21 hồ sơ allow dòng 162–182; http_post deny dòng 183 với reason và on_behalf_of=dpo. Mọi dòng ledger có identity, TTL và reason, không chứa args/hồ sơ PII thô. Thống kê ở reports/cp5-evidence.json; xác minh ở reports/cp5-ledger.log. Các dòng evidence replay từng biến thể 28–135 trong injection-corpus.md vẫn được giữ nguyên.

Gitleaks version: 8.30.1. Quét lịch sử exit code 1 với đúng một lab24-synthetic-token ở commit 1bdd849; quét thư mục hiện tại exit code 0, 0 finding sau các ngoại lệ đã giải thích trong secrets-incident.md. Bằng chứng mới nhất: reports/cp5-history.json, reports/cp5-history.log, reports/cp5-current.json, reports/cp5-current.log. pre-commit run --all-files pass, exit code 0; log reports/cp5-pre-commit.log.

compliance-mapping.md đã ghi đủ ba văn bản pháp luật và OWASP ASI01/03/04, với file/dòng evidence và giới hạn. Tên/số văn bản và nguồn chính thức đã xác nhận; điều khoản cụ thể chưa xác minh từ toàn văn nên không ghi số điều/khoản hay kết luận tuân thủ. dpia-lite.md đã trả lời đủ loại dữ liệu, mục đích/principal, luồng dữ liệu/endpoint, allow/deny và giới hạn mock.

Điều kiện nộp: attack-after.log và ledger.jsonl phải được git add -f vì .gitignore chặn. Mã nguồn, lure, báo cáo, lock và cấu hình scanner/hook đều phải có trong commit cuối. Không nộp sink.log, .venv, .cache, .tools hay dữ liệu/credential thật. Repo giữ lịch sử seed 1bdd849. Bonus không bắt buộc.

Không còn lỗi test trong phạm vi bắt buộc. Chế độ --model, authentication production, sandbox OS, đánh giá PII trên dữ liệu thực và hồ sơ tuân thủ pháp lý production chưa thuộc bằng chứng của lab này. Deadline và nơi nộp theo thông báo coach/TA; khi nộp ghi link repo và SHA commit cuối.
