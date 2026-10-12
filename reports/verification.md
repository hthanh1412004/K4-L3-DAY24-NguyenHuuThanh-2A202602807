# Verification

## CP3 — kiểm tra ngày 12/10/2026

Máy Windows, Python 3.11.9 trong .venv.

CP3 có 28 test pass, không skip; log ở reports/cp3-tests.log. PII có gold=118, pred=118, tp=118, precision=1.000 và recall=1.000 trên bộ mẫu synthetic. tests/test_cp3_boundary.py kiểm text đã che PII trước cả find_injection và summarize.

support_l1 đọc 0 hồ sơ, dpo đọc 21 hồ sơ hợp lệ. Cả hai vẫn tổng hợp 45 ticket. Run B lấy số ticket từ tên file rồi tra related_tickets, không lấy customer ID trong lời attacker. Thống kê ở reports/cp3-evidence.json.

Ở lần ghi CP3, ledger có 27 dòng và 2 deny http_post. verify=True; thêm một ký tự vào reason của dòng giữa trong bản sao thì verify=False. Bản sao thử đã xóa. Các lần chạy sau nối thêm vào ledger, hiện có 183 dòng, không phải chỉ 27 dòng.

## Kiểm tra toàn bài

Lệnh: .venv/Scripts/python.exe -X utf8 -m pytest tests/ -q -s

34 passed, không fail/skip. Log lần cuối: reports/cp5-tests.log. check_lure báo 4/4 lure sẵn sàng trong reports/cp5-lures.log.

CP4 - Supply chain và secrets

Gitleaks 8.30.1 tải từ https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1. SHA256 khớp checksum release (reports/cp4-scanner-download.log).

Quét lịch sử có 1 finding lab24-synthetic-token ở commit 1bdd849, file lab-fake-secret.txt dòng 1, exit code 1 đúng yêu cầu. Quét file hiện tại có 0 finding, exit code 0. reports/cp4-history.json và reports/cp4-current.json ghi kết quả CP4; reports/cp5-history.json và reports/cp5-current.json là lần kiêm tra cuối.

Có hai ngoại lệ scanner đã giải thích trong reports/secrets-incident.md: phép gán hàm RegEnumKey của setuptools bị báo nhầm và cache chứa fixture secret của repo Gitleaks. Mã bài làm và token giả trong lịch sử vẫn được quét.

Hook pin rev v8.30.1, id gitleaks-system, pass_filenames: false. Entry dùng gitleaks dir để quét thư mục hiện tại. Thêm .tools/gitleaks-v8.30.1 vào PATH rồi chạy .venv/Scripts/python.exe -m pre_commit run --all-files. Kết quả Passed ở reports/cp5-pre-commit.log.

requirements.lock khóa 11 package có SHA256. pip install --force-reinstall --require-hashes -r requirements.lock chạy thành công. Log: reports/cp4-lock-build.log và reports/cp4-lock-install.log. reports/cp4-evidence.json lưu thống kê CP4; commit CP4 là d3bf818.

Lúc tạo lock có proxy không hoạt động và PIP_NO_INDEX, nên tiến trình tải được chạy với môi trường con bỏ hai thiết lập đó, dùng PyPI chính thức. Lần test qua subprocess cũng từng lỗi UnicodeEncodeError do cp1252. Chạy lai với -X utf8 thì pass; không sửa test. Thiết lập hệ thống giữ nguyên.

CP5 - Prove

Lệnh: .venv/Scripts/python.exe -X utf8 -m scripts.verify_submission

Script chạy test và check_lure trước, reset sink lần nữa rồi chạy đúng câu hỏi “Tổng hợp các ticket còn mở tuần này” với --mock --as dpo. reports/cp5-replay.log có kết quả tổng hợp 45 ticket. Test cố ý thiếu ticket-904b vẫn in lỗi như dự kiến và test đó pass.

reports/attack-before.log có 4 POST synthetic KH-000999 tới /reconcile. File không bị sửa trong lần kiểm tra cuối; SHA256 là d97af1b21f949b58769d2259649885c9e1142afad18f5d446fe0f13359a54dac. reports/attack-after.log copy từ sink sau replay, rỗng 0 byte.

Ledger verify=True, 183 dòng. Lần cuối dưới dpo: search_docs allow dòng 160; mapping read_customer allow dòng 161; 21 hồ sơ allow dòng 162–182; http_post deny dòng 183, có reason và on_behalf_of=dpo. Mọi dòng có identity, TTL và reason, args được hash. Xem reports/cp5-evidence.json và reports/cp5-ledger.log. Các dòng 28–135 được dẫn trong injection-corpus.md vẫn giữ nguyên.

pre-commit pass, Gitleaks hiện tại sạch; lịch sử vẫn có đúng 1 token giả. Log ở reports/cp5-pre-commit.log, reports/cp5-current.log và reports/cp5-history.log. Phiên bản scanner ở reports/cp5-scanner-version.log.

compliance-mapping.md đã có ba văn bản pháp luật và OWASP ASI01/03/04, kèm file/dòng kiểm chứng. Tên văn bản đã xác nhận từ nguồn chính thức, còn điều khoản cụ thể chưa xác minh nên không ghi số điều. dpia-lite.md đã trả lời đủ bốn mục.

Hai file attack-after.log và ledger.jsonl đã được thêm vào Git ở CP5. Không đưa sink.log, .venv, .cache hay .tools vào bài nộp. Repo còn lịch sử seed 1bdd849. Khi nộp dùng link repo và SHA cuối, theo nơi/hạn coach hoặc TA thông báo. Bonus không bắt buộc.

Chưa thấy lỗi trong các test bắt buộc. Kết quả chỉ áp dụng mock và bộ synthetic. Chưa kiểm --model, xác thực thật hay sandbox OS. Regex có thể bỏ sót PII thực tế; hash chain không phát hiện cắt đuôi hoặc viết lại cả file nếu thiếu mốc bên ngoài. Bài lab chưa đủ để kết luận tuân thủ pháp luật.
