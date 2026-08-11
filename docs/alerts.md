# Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- **Tên:** HighLatencyAlert
- **Severity:** warning
- **SLI/SLO liên quan:** `latency_p95_ms <= 2000` (ngưỡng challenge K4)
- **Điều kiện và thời gian duy trì:** P95 latency lớn hơn 2000 ms liên tục 5 phút.
- **Ảnh hưởng tới người dùng:** Phản hồi AI chậm, tăng nguy cơ timeout và người dùng gửi lại yêu cầu.
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra panel Latency và `/metrics` để xác nhận P95, thời điểm bắt đầu và phạm vi ảnh hưởng.
  2. Lọc Langfuse traces trong cùng cửa sổ thời gian, mở trace chậm và xác định span chiếm nhiều thời gian nhất.
  3. Dùng `correlation_id` hoặc `trace_id` từ trace để tìm các dòng liên quan trong `data/logs.jsonl` và kiểm tra feature/error đi kèm.
- **Mitigation tạm thời:** Tắt incident practice nếu đang bật; giảm concurrency hoặc chuyển luồng sang fallback an toàn; scale worker nếu tài nguyên bão hòa. Theo dõi P95 ít nhất 5 phút sau mitigation.
- **Owner:** platform-team

## Alert 2

- **Tên:** HighErrorRateAlert
- **Severity:** critical
- **SLI/SLO liên quan:** `error_rate_pct <= 2`
- **Điều kiện và thời gian duy trì:** Tỷ lệ `request_failed / request_received` lớn hơn 2% liên tục 3 phút.
- **Ảnh hưởng tới người dùng:** Yêu cầu thất bại hoặc không nhận được câu trả lời từ API.
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra panel Error rate để xác nhận tỷ lệ và breakdown theo `error_type`.
  2. Mở các trace lỗi trong cùng cửa sổ thời gian, xác định span/provider/tool thất bại.
  3. Tìm log theo `correlation_id`, so sánh theo feature và phiên bản prompt để khoanh vùng.
- **Mitigation tạm thời:** Rollback thay đổi gần nhất nếu có tương quan; tắt feature/incident gây lỗi hoặc chuyển sang fallback; kiểm tra lại error rate trong 3 phút.
- **Owner:** platform-team

## Alert 3

- **Tên:** CostBudgetAlert
- **Severity:** warning
- **SLI/SLO liên quan:** `daily_cost_usd <= 2.5`
- **Điều kiện và thời gian duy trì:** Chi phí cộng dồn lớn hơn 2.5 USD trong cửa sổ 1 giờ.
- **Ảnh hưởng tới người dùng:** Nguy cơ vượt ngân sách, bị throttling hoặc phải ngừng dịch vụ khi hết quota.
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra panel Cost và Tokens để xác nhận thời điểm tăng và input/output tokens đóng góp.
  2. Lọc trace có cost hoặc token cao trong cùng cửa sổ, nhóm theo feature và prompt version.
  3. Tìm log theo `trace_id`/`correlation_id`, kiểm tra request lặp, output dài hoặc traffic bất thường.
- **Mitigation tạm thời:** Giới hạn output tokens và concurrency; tắt workload/incident tạo cost bất thường; chuyển model tiết kiệm hơn nếu chính sách cho phép.
- **Owner:** finance-team
