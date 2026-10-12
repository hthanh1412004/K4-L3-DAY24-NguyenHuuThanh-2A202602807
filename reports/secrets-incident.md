# Secret giả trong lịch sử Git — điền trong checkpoint 4

- Scanner và phiên bản:

Gitleaks v8.30.1 bản Windows x64, tải từ https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1. Kiêm tra SHA256 thấy khớp checksum chính thức. Log ở reports/cp4-scanner-download.log, binary ở .tools/gitleaks-v8.30.1/gitleaks.exe.

- Commit chứa token giả:

1bdd849922156c868a5ee9293d68f5b72e242d2c, viết tắt 1bdd849. File đã xóa ở commit ece6ca4 nhưng phiên bản cũ vẫn còn trong lịch sử.

- File, rule và kết quả quét lịch sử:

lab-fake-secret.txt dòng 1, rule lab24-synthetic-token. Token có dạng LAB24-DEMO, được tạo sẵn cho bài và không dùng được ở dịch vụ thật.

Lệnh: gitleaks git --config .gitleaks.toml --redact --verbose --report-format json --report-path reports/cp4-history.json .

Quét thấy 1 finding, exit code 1 đúng dự kiến. reports/cp4-history.json và reports/cp4-history.log có bằng chứng đã redact. Lần cuối ở reports/cp5-history.json và reports/cp5-history.log cũng thấy đúng một finding. Token này không được đưa vào ngoại lệ.

- Kết quả quét file hiện tại:

Lệnh: gitleaks dir --config .gitleaks.toml --redact --verbose --report-format json --report-path reports/cp4-current.json .

Lần đầu báo generic-api-key ở .venv/Lib/site-packages/setuptools/_distutils/msvccompiler.py dòng 45. Mở file thấy RegEnumKey = win32api.RegEnumKey, chỉ là gán hàm thư viện, không phải secret. Log đầu ở reports/cp4-current-initial.json và reports/cp4-current-initial.log. .gitleaksignore chỉ bỏ qua đúng fingerprint này, không bỏ qua cả .venv hay tắt rule.

Sau khi pre-commit tải repo Gitleaks về .cache/pre-commit, scanner thấy thêm 415 finding từ các mẫu secret dùng để test trong repo đó. .gitleaks.toml loại trừ riêng cache này. Quét lại thư muc hiện tại sạch, 0 finding, exit code 0. Log CP4 ở reports/cp4-current.json và reports/cp4-current.log; lần cuối ở reports/cp5-current.json và reports/cp5-current.log. Mã nguồn, corpus, data, reports và lịch sử bài vẫn được quét.

- Nếu đây là credential thật, cần xử lý thế nào:

Thu hồi/rotate tại dịch vụ cấp credential, cập nhật chỗ đang dùng và kiểm tra log truy cập. Sau đó xóa secret khỏi mã/bản phát hành, xử lý các bản sao và lịch sử theo quy trình của nhóm rồi quét lại. Bài này không cần rotate dịch vụ nào vì token vốn đã vô hiệu.

- Vì sao xoá file khỏi HEAD hoặc pin dependency vẫn chưa đủ:

Xóa ở HEAD không làm token mất hiệu lực, cũng không xóa bản sao trong lịch sử hay clone. Pin phiên bản và hash giúp kiểm đúng artifact cài đặt, không đảm bảo package không có lỗ hổng. Hook phát hiện secret ở các lần kiểm tra sau, không thu hồi secret đã lộ. Nếu là secret thật thì vẫn phải rotate.

.pre-commit-config.yaml dùng repo chính thức, rev v8.30.1, id gitleaks-system và pass_filenames: false. Entry gitleaks dir quét file hiện tại, kể cả file chưa stage. Quét lịch sử chạy riêng. pre-commit run --all-files pass, log ở reports/cp5-pre-commit.log.

requirements.lock sinh bằng piptools compile --generate-hashes, mỗi package có phiên bản và SHA256. pip install --force-reinstall --require-hashes -r requirements.lock đã tải/cài lại thành công. Log ở reports/cp4-lock-build.log và reports/cp4-lock-install.log. Cache và binary trong .tools không đưa vào bài nộp.
