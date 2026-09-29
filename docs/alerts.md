# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: HighLatencyP95
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack (#alerts-llmops)
- SLI/SLO liên quan: Primary SLO `fast_successful_requests` (latency <= 3000ms, target 99.5%)
- Điều kiện và thời gian duy trì: `latency_p95 > 3000` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng trải nghiệm độ trễ phản hồi cao, chat UI có nguy cơ timeout
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra Dashboard panel Latency và TTFT xem độ trễ tăng ở bước TTFT (LLM) hay toàn bộ request.
  2. Tra cứu `data/logs.jsonl` lọc các log `response_sent` có `latency_ms > 3000` trong 5 phút gần nhất, lấy `correlation_id`.
  3. Mở Trace trên Langfuse bằng `correlation_id` để xác định span chậm (retrieval chậm do vector DB hay LLM generation chậm).
- Mitigation tạm thời:
  - Nếu retrieval chậm: kích hoạt cache tạm thời hoặc fallback query trực tiếp không qua heavy vector search.
  - Nếu LLM generation chậm: switch traffic sang backup LLM provider hoặc giảm output token limit.
- Owner: llmops-oncall

## Alert 2

- Tên: HighErrorRate
- Severity: critical
- Duration: 5m
- Kênh thông báo: Slack (#alerts-llmops-critical)
- SLI/SLO liên quan: Guardrail `error_rate_pct_max <= 2%`
- Điều kiện và thời gian duy trì: `error_rate_pct > 2.0` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: Request thất bại, người dùng nhận mã lỗi 500 hoặc thông báo lỗi hệ thống
- Ba bước kiểm tra đầu tiên:
  1. Mở Dashboard panel Errors xem phân loại `error_type` (RuntimeError, TimeoutError, etc.) và retrieval success rate.
  2. Tra cứu `data/logs.jsonl` tìm các event `request_failed`, kiểm tra `payload.detail` và `correlation_id`.
  3. Mở trace bị lỗi trên Langfuse bằng `correlation_id` để xác định chính xác span phát sinh exception.
- Mitigation tạm thời:
  - Nếu lỗi vector store (`tool_fail` / `RuntimeError: Vector store timeout`): restart service vector DB, bật cờ fallback cho retrieval.
  - Nếu lỗi downstream API: fallback sang static response hoặc degrade gracefully.
- Owner: llmops-oncall

## Alert 3

- Tên: LowQualityScoreOrRetrievalDegradation
- Severity: warning
- Duration: 10m
- Kênh thông báo: Slack (#alerts-llmops)
- SLI/SLO liên quan: Guardrail `quality_score_avg_min >= 0.75` và `retrieval_success_rate_pct_min >= 90%`
- Điều kiện và thời gian duy trì: `quality_avg < 0.75 or tool_success_rate_pct < 90` duy trì trong 10 phút
- Ảnh hưởng tới người dùng: Câu trả lời kém chất lượng, lạc đề hoặc phản hồi chung chung không có tài liệu dẫn chứng
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra Dashboard panel Quality proxy và Errors panel xem điểm chất lượng và tool success rate biến động từ khi nào.
  2. Tra cứu log `response_sent` có `quality_score < 0.7`, ghi nhận `prompt_version`, `model` và `feature`.
  3. Kiểm tra trace trên Langfuse để xem prompt template mới có làm giảm độ dài hoặc ngữ cảnh hữu ích không.
- Mitigation tạm thời:
  - Nếu do deploy prompt mới làm suy giảm chất lượng: rollback label `production` về version trước trên Langfuse.
  - Nếu do retrieval không tìm thấy tài liệu liên quan: re-index corpus hoặc bổ sung fallback knowledge documents.
- Owner: llmops-oncall

