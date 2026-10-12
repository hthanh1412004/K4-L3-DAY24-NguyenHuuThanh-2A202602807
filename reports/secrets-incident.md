# Secret giả trong lịch sử Git — điền trong checkpoint 4

- Scanner và phiên bản:

Gitleaks v8.30.1, binary Windows x64 tải từ release chính thức https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1. SHA256 archive khớp checksums của release; bằng chứng ở reports/cp4-scanner-download.log. Binary nằm trong .tools/gitleaks-v8.30.1/gitleaks.exe.

- Commit chứa token giả:

1bdd849922156c868a5ee9293d68f5b72e242d2c (viết tắt 1bdd849). File bị xóa trong commit ece6ca4; lịch sử Git vẫn giữ phiên bản chứa token.

- File, rule và kết quả quét lịch sử:

File lab-fake-secret.txt, dòng 1. Rule lab24-synthetic-token bắt token LAB24-DEMO giả, vô hiệu, được cài sẵn cho bài lab. Đây là dữ liệu synthetic, không phải credential thật hay bằng chứng một dịch vụ thật bị xâm nhập.

Lệnh: gitleaks git --config .gitleaks.toml --redact --verbose --report-format json --report-path reports/cp4-history.json .

Kết quả: 1 finding, exit code 1 đúng dự kiến. reports/cp4-history.json và reports/cp4-history.log lưu bằng chứng; giá trị token đã được redact. Không dùng baseline hay ngoại lệ để che finding trong lịch sử này.

- Kết quả quét file hiện tại:

Lệnh: gitleaks dir --config .gitleaks.toml --redact --verbose --report-format json --report-path reports/cp4-current.json .

Lần quét ban đầu báo 1 finding generic-api-key tại .venv/Lib/site-packages/setuptools/_distutils/msvccompiler.py dòng 45. Kiểm tra nguồn xác nhận nội dung là RegEnumKey = win32api.RegEnumKey, một phép gán hàm Windows registry của thư viện, không phải secret. Bằng chứng lần đầu nằm ở reports/cp4-current-initial.json và reports/cp4-current-initial.log.

.gitleaksignore chỉ chứa fingerprint của finding cụ thể trên. Không bỏ qua cả .venv, không tắt rule generic-api-key, không bỏ qua mã bài làm hay token giả trong Git.

Sau khi pre-commit tải repo Gitleaks về .cache/pre-commit, quét thư mục còn thấy 415 finding từ các fixture kiểm thử secret của chính Gitleaks trong cache. .gitleaks.toml loại trừ riêng đường dẫn cache sinh tự động này; .gitignore cũng không đưa cache và binary .tools vào bài nộp. Mã nguồn, corpus, data, reports và lịch sử Git của bài vẫn được quét. Quét lại sau các ngoại lệ đã giải thích: 0 finding, exit code 0; bằng chứng ở reports/cp4-current.json và reports/cp4-current.log.

- Nếu đây là credential thật, cần xử lý thế nào:

Thu hồi/rotate ngay ở dịch vụ cấp credential; cập nhật nơi sử dụng sang credential mới và kiểm tra log truy cập để đánh giá việc sử dụng trái phép. Xóa secret khỏi mã và các bản phát hành, xử lý bản sao/lịch sử theo quy trình của nhóm, rồi quét lại. Không thực hiện rotate một dịch vụ thật trong bài này vì token chỉ là fixture vô hiệu.

- Vì sao xoá file khỏi HEAD hoặc pin dependency vẫn chưa đủ:

Xóa file ở HEAD không thu hồi credential và không xóa bản sao trong lịch sử, clone hay log. Pin phiên bản và SHA256 trong requirements.lock giúp tái lập dependency và kiểm tra artifact cài đặt; hash không chứng minh dependency không có lỗ hổng. Hook giúp phát hiện secret trong lần kiểm tra tiếp theo, không vô hiệu hóa secret đã lộ. Vì vậy pin và hook không thay thế thu hồi/rotate.

Hook .pre-commit-config.yaml dùng repo chính thức, rev v8.30.1, id gitleaks-system và pass_filenames: false. Entry được đặt thành gitleaks dir để pre-commit run --all-files thực sự quét thư mục hiện tại, kể cả file chưa stage. Quét lịch sử chạy riêng và vẫn trả 1 finding như dự kiến.

requirements.lock được sinh bằng piptools compile --generate-hashes; mỗi package pin phiên bản và có SHA256. pip install --force-reinstall --require-hashes -r requirements.lock đã thành công, bảo đảm tải/cài lại artifact thay vì chỉ báo package đã có sẵn. Log ở reports/cp4-lock-build.log và reports/cp4-lock-install.log.
