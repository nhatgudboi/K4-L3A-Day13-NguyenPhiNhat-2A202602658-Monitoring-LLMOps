# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Phi Nhật
- **MSSV:** 2A202602658
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/nhatgudboi/K4-L3A-Day13-NguyenPhiNhat-2A202602658-Monitoring-LLMOps
- **Commit SHA cuối:** 8a9fd5a
- **Challenge ID:** practice-rag_slow
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602658`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | [evidence/01-pytest.png](evidence/01-pytest.png) |
| Log validator | [evidence/02-log-validator.png](evidence/02-log-validator.png) |
| Dashboard validator | [evidence/03-dashboard-validator.png](evidence/03-dashboard-validator.png) |
| Structured log | [evidence/04-structured-log.png](evidence/04-structured-log.png) |
| PII redaction | [evidence/05-pii-redaction.png](evidence/05-pii-redaction.png) |
| Trace list | [evidence/06-trace-list.png](evidence/06-trace-list.png) |
| Trace waterfall | [evidence/07-trace-waterfall.png](evidence/07-trace-waterfall.png) |
| Trace metadata | [evidence/08-trace-metadata.png](evidence/08-trace-metadata.png) |
| Prompt versions | [evidence/09-prompt-versions.png](evidence/09-prompt-versions.png) |
| Prompt rollback | [evidence/10-prompt-rollback.png](evidence/10-prompt-rollback.png) |
| Dashboard runtime | [evidence/11-dashboard-overview.png](evidence/11-dashboard-overview.png) |
| Incident metric | [evidence/12-incident-metric.png](evidence/12-incident-metric.png) |
| Incident log | [evidence/13-incident-log.png](evidence/13-incident-log.png) |
| Incident trace | [evidence/14-incident-trace.png](evidence/14-incident-trace.png) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 | Đạt điểm tuyệt đối: đủ schema, correlation_id, context enrichment và PII scrubbing hoàn chỉnh |
| `validate_dashboard.py` | 6/6 panel | 6/6 panel | Hợp lệ 100% dashboard contract về các sự kiện, trường, phép tổng hợp và threshold |
| `pytest` | 22 passed | 26 passed | 100% pass toàn bộ test suite, bổ sung 4 unit/integration tests cho PII và context enrichment |
| Số traces hợp lệ | 0 | 11 | Đầy đủ quan hệ phân cấp cây root span, child retriever và child generation observations |
| Số PII leak | 0 | 0 | 100% PII (email, phone VN, CCCD, credit card, passport) được scrub trước khi ghi log/trace |
| Latency P95 / TTFT P95 | 155.0 ms / 50.0 ms | 151.0 ms / 50.0 ms | Độ trễ bình thường ổn định, cách xa ngưỡng cảnh báo SLO 3000ms |
| Retrieval success rate | 100% | 100% | Tool retrieval hoạt động chuẩn xác, không có ngoại lệ vector store ở trạng thái baseline |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
  Trong `app/middleware.py`, `CorrelationIdMiddleware` trước tiên gọi `clear_contextvars()` để xóa context cũ, ngăn ngừa tình trạng rò rỉ context giữa các request đồng thời trong mô hình bất đồng bộ. Sau đó middleware kiểm tra header `x-request-id` từ request client gửi lên; nếu có và không rỗng thì tái sử dụng, ngược lại thì sinh mới theo đúng định dạng `req-<8-hex>` bằng `f"req-{uuid.uuid4().hex[:8]}"`. Correlation ID này được bind vào contextvars của `structlog` (`bind_contextvars(correlation_id=correlation_id, env=os.getenv("APP_ENV", "dev"))`), lưu vào `request.state.correlation_id` để router truy cập, và được gán vào header phản hồi cho client: `response.headers["x-request-id"] = correlation_id` cùng `response.headers["x-response-time-ms"]`.
- **Các metadata được ghi vào structured log:**
  Tại endpoint `/chat` trong `app/main.py`, ngay trước khi ghi event `request_received`, ứng dụng gọi `bind_contextvars(user_id_hash=hash_user_id(body.user_id), session_id=body.session_id, feature=body.feature, model=agent.model, env=os.getenv("APP_ENV", "dev"))`. Nhờ cơ chế contextvars của structlog, tất cả các log events trong request đó (`request_received`, `response_sent`, hoặc `request_failed`) đều tự động chứa đầy đủ: `ts`, `level`, `service="api"`, `correlation_id`, `env`, `user_id_hash`, `session_id`, `feature`, `model`, cùng các trường metrics: `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name`, `tool_success`, và `payload` đã được sanitize.
- **Cách bảo đảm PII được scrub trước khi ghi:**
  Tại `app/logging_config.py`, processor `scrub_event` được đăng ký đứng trước `JsonlFileProcessor` và `JSONRenderer`. Hàm `scrub_event` duyệt đệ quy tất cả các trường và giá trị chuỗi trong log dictionary, gọi `scrub_text()` từ `app/pii.py`. Các biểu thức chính quy trong `PII_PATTERNS` (bao gồm `credit_card`, `cccd`, `email`, `phone_vn`, `passport`) sẽ thay thế toàn bộ dữ liệu nhạy cảm thành các token an toàn như `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CCCD]`, `[REDACTED_CREDIT_CARD]`. Việc scrubbing này diễn ra trực tiếp trên cấu trúc in-memory trước khi JSON được serialize hay ghi xuống `data/logs.jsonl` hoặc xuất ra console.
- **Cách kiểm chứng kết quả:**
  Chạy lệnh `python scripts/validate_logs.py` đọc toàn bộ file `data/logs.jsonl`. Kết quả đạt 100/100, 0 PII leaks, 0 records missing required/enrichment fields. Đồng thời chạy `python -m pytest -q` với bộ kiểm thử `tests/test_pii.py` và `tests/test_chat_observability.py` để bảo đảm các trường nhạy cảm đều được che giấu trong mọi điều kiện.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
  Project Langfuse được cấu hình mang tên định danh cá nhân `day13-k4-l3a-2A202602658`. Mỗi request chạy qua hệ thống đều tự động gán tags `["lab", feature, self.model]`, `environment="dev"`, và gán `user_id=hash_user_id(user_id)`. Tên trace thống nhất là `day13-agent-request`, metadata mang `correlation_id` khớp với từng dòng log tương ứng trong `data/logs.jsonl`.
- **Cấu trúc root/retrieval/generation observations:**
  Trace có cấu trúc cây quan hệ cha-con rõ ràng:
  - **Root observation:** Loại `agent` (`lab-agent-run`), theo dõi toàn bộ vòng đời xử lý request từ API đến agent logic.
  - **Child observation 1:** Loại `retriever` (`retrieval`) bọc quanh hàm `retrieve()`, theo dõi thời gian truy xuất tài liệu từ vector store và số lượng tài liệu (`doc_count`).
  - **Child observation 2:** Loại `generation` (`fake-llm-generate`) bọc quanh hàm `FakeLLM.generate()`, nhận managed prompt từ Langfuse, cập nhật thông tin model (`claude-sonnet-4-5`), `usage_details` (`input_tokens`, `output_tokens`), và `cost_details` tính toán dựa trên định mức token.
- **Cách nối trace với log:**
  Tại root span và trong hàm `run()` của `LabAgent`, `correlation_id` được truyền vào từ `request.state.correlation_id` và gán vào metadata của trace: `metadata={"correlation_id": correlation_id, "feature": feature, "model": self.model}`. Khi quan sát log trong `data/logs.jsonl`, kỹ sư lấy giá trị `correlation_id` và tìm kiếm trên ô filter metadata của Langfuse để mở ngay trace tương ứng.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 (`v1`), gắn label `baseline` và `production`.
- **Version/label candidate:** Version 2 (`v2`), gắn label `candidate` (với chỉ dẫn: *Answer in no more than three concise bullet points*).
- **Trace ID của mỗi version:**
  - Baseline (v1): `tr-80a7cefd01` (prompt_version=1, label=baseline)
  - Candidate (v2): `tr-9040d57502` (prompt_version=2, label=candidate)
  - Rollback (v1): `tr-98b91c6703` (prompt_version=1, label=production)
- **Cách promote và rollback `production`:**
  - **Promote:** Trên giao diện Prompt Management của Langfuse cho prompt `day13-chat`, gỡ label `production` khỏi v1 và gán label `production` cho v2. Ứng dụng khi chạy với `LANGFUSE_PROMPT_LABEL=production` sẽ tự động fetch nội dung mới của v2 mà không cần thay đổi hay build lại mã nguồn.
  - **Rollback:** Khi phát hiện candidate v2 không đáp ứng kỳ vọng hoặc làm suy giảm chất lượng câu trả lời, quản trị viên chỉ cần chuyển label `production` trỏ ngược lại vào v1 ngay trên giao diện Langfuse. App sẽ tự động tải lại v1, hoàn tất rollback tức thì mà không có thời gian gián đoạn dịch vụ (zero-downtime).

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
  Dashboard được xây dựng đúng theo đặc tả `config/dashboard.yaml` với nguồn dữ liệu chuẩn từ `data/logs.jsonl` bao gồm 6 panel:
  1. *Latency*: Hiển thị P50, P95, P99 và TTFT P95 (ms); đường threshold P95 <= 3000ms.
  2. *Traffic*: Hiển thị tổng số request nhận được và tốc độ request/phút (rate_per_minute); ngưỡng >= 1 req/min.
  3. *Errors*: Tỷ lệ lỗi toàn hệ thống (error_rate_pct) và tỷ lệ truy xuất retrieval thành công (tool_success_rate_pct); ngưỡng error <= 2%.
  4. *Cost*: Tổng chi phí USD tích lũy và chi phí theo từng request; ngưỡng ngân sách <= $2.50.
  5. *Tokens*: Tổng số token đầu vào (tokens_in) và token đầu ra (tokens_out); ngưỡng giới hạn <= 50,000 tokens.
  6. *Quality*: Điểm chất lượng trung bình của câu trả lời (quality_score từ 0.0 đến 1.0); ngưỡng mục tiêu >= 0.75.
- **SLO và lý do chọn:**
  - Primary SLO: `fast_successful_requests` với SLI là `event == "response_sent" and latency_ms <= 3000` trên tổng số `event == "request_received"`.
  - Cửa sổ đo lường (window): 28 ngày (rolling 28d window).
  - Mục tiêu (Target): 99.5%.
  - Lý do chọn: Với ứng dụng AI assistant tương tác thời gian thực, người dùng kỳ vọng nhận được phản hồi trong vòng 3 giây. Ngưỡng 3000ms là ranh giới giữa trải nghiệm mượt mà và sự mất kiên nhẫn dẫn đến drop-off. Mức target 99.5% phù hợp với tiêu chuẩn dịch vụ doanh nghiệp, cho phép 0.5% buffer cho các tình huống tail latency do network hoặc tải cao.
- **Cách tính error budget:**
  Error Budget (%) = 100% - Target SLO (%) = 100% - 99.5% = 0.5%.
  Ví dụ: Trong cửa sổ 28 ngày với 100,000 requests, ngân sách lỗi cho phép là 0.5% × 100,000 = 500 requests được phép chạy chậm quá 3000ms hoặc thất bại. Khi tỷ lệ vi phạm vượt quá 500 requests, error budget bị cạn kiệt, đội ngũ phải đóng băng việc release tính năng mới và tập trung vào tối ưu hiệu năng/độ tin cậy.
- **Ba alert và runbook tương ứng:**
  1. **Alert 1 (`HighLatencyP95`)**: Severity `warning`, điều kiện `latency_p95 > 3000` trong `5m`, kênh Slack `#alerts-llmops`. Runbook: kiểm tra TTFT vs Total Latency, lọc log `response_sent` chậm lấy `correlation_id`, mở trace kiểm tra span retrieval/generation, bật cache hoặc degrade retrieval nếu vector store quá tải.
  2. **Alert 2 (`HighErrorRate`)**: Severity `critical`, điều kiện `error_rate_pct > 2.0` trong `5m`, kênh Slack `#alerts-llmops-critical`. Runbook: xem error breakdown trên panel Errors, tra cứu `request_failed` tìm `payload.detail`, kiểm tra trạng thái vector store / LLM API endpoint, restart container hoặc chuyển sang fallback static response.
  3. **Alert 3 (`LowQualityScoreOrRetrievalDegradation`)**: Severity `warning`, điều kiện `quality_avg < 0.75 or tool_success_rate_pct < 90` trong `10m`, kênh Slack `#alerts-llmops`. Runbook: so sánh xu hướng chất lượng câu trả lời, đối chiếu `prompt_version` vừa cập nhật, nếu do prompt mới thì rollback ngay `production` về version trước trên Langfuse, nếu do thiếu dữ liệu thì bổ sung domain documents.

## 7. Điều tra challenge

- **Challenge ID:** `practice-rag_slow`
- **Khoảng thời gian điều tra:** `2026-09-29 17:54:40 - 17:55:10` (local) / `10:54:40 - 10:55:10 UTC`
- **Triệu chứng từ metrics:**
  Panel Latency trên Dashboard ghi nhận độ trễ P95 tăng vọt từ 155ms lên 2652ms (tăng gấp hơn 17 lần), tiệm cận ngưỡng vi phạm SLO 3000ms. Tuy nhiên, TTFT P95 vẫn duy trì ở mức bình thường là 50ms.
- **Log line và correlation ID liên quan:**
  - Correlation ID: `req-22b165de`
  - Log line `request_received`:
    `{"service": "api", "payload": {"message_preview": "What is your refund policy?"}, "event": "request_received", "session_id": "s_incident_01", "model": "claude-sonnet-4-5", "feature": "refund", "env": "dev", "user_id_hash": "6959f68b1d57", "correlation_id": "req-22b165de", "level": "info", "ts": "2026-09-29T10:54:51.247326Z"}`
  - Log line `response_sent`:
    `{"service": "api", "latency_ms": 2652, "ttft_ms": 50, "tokens_in": 29, "tokens_out": 138, "cost_usd": 0.002157, "quality_score": 0.9, "tool_name": "retrieval", "tool_success": true, "event": "response_sent", "correlation_id": "req-22b165de", "level": "info", "ts": "2026-09-29T10:54:53.900563Z"}`
- **Trace ID và span gây ảnh hưởng:**
  - Trace ID: `tr-22b165de11`
  - Span gây ảnh hưởng: Child span `retrieval` (loại `retriever`). Thời gian thực thi của span này lên tới 2500ms (chiếm 94.3% tổng thời gian request), trong khi span LLM generation `fake-llm-generate` chỉ tốn 150ms.
- **Root cause:**
  Vector database / dịch vụ tìm kiếm tài liệu (`retrieve()`) bị nghẽn (do kịch bản `rag_slow` kích hoạt độ trễ giả lập 2.5s), dẫn đến toàn bộ luồng xử lý bị block chờ kết quả retrieval trước khi chuyển tiếp sang LLM.
- **Fix action:**
  Tắt kịch bản sự cố (`python scripts/inject_incident.py --scenario rag_slow --disable`); trong thực tế triển khai cache tầng retrieval (Redis/In-memory vector cache), đặt timeout cứng cho bước retrieval là 1000ms (nếu quá thời gian thì chuyển ngay sang fallback prompt không có context thay vì làm treo cả request).
- **Preventive measure:**
  Cấu hình cảnh báo sớm trên thời gian thực thi của riêng span `retrieval` (> 1000ms), kích hoạt circuit breaker tự động ngắt kết nối với vector DB bị quá tải, và thiết lập SLO chuyên biệt cho thành phần retrieval.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
  Quyết định đặt processor `scrub_event` chạy đệ quy trước cả `JsonlFileProcessor` và `JSONRenderer` trong chuỗi pipeline của structlog. Lý do: PII phải được làm sạch ở tầng dữ liệu trong bộ nhớ trước khi dữ liệu được chuyển đổi thành chuỗi JSON hay ghi ra bất kỳ storage nào (file, stdout, telemetry exporter). Điều này triệt tiêu hoàn toàn nguy cơ rò rỉ PII ở mọi tầng output.
- **Một lỗi/blocker đã gặp:**
  Khi chạy `validate_logs.py` ở baseline, điểm số chỉ đạt 30/100 do `correlation_id` bị thiếu ở tất cả các bản ghi log và contextvars chưa được truyền tự động vào các log event. Ngoài ra log cũ còn tồn đọng trong `data/logs.jsonl` khiến validator tính điểm cả log trước khi sửa code.
- **Cách tìm nguyên nhân và xử lý:**
  Đọc source của `scripts/validate_logs.py` để nắm rõ tiêu chí tính điểm (`REQUIRED_FIELDS`, `ENRICHMENT_FIELDS`, regex PII). Sau đó hoàn thiện `CorrelationIdMiddleware` với `clear_contextvars()` và `bind_contextvars()`, bổ sung `bind_contextvars` các trường context (`user_id_hash`, `session_id`, `feature`, `model`, `env`) ngay đầu endpoint `/chat`. Trước khi kiểm tra lại, lưu backup baseline thành `data/logs_baseline.jsonl` rồi xóa file log cũ để đo đạc chuẩn xác.
- **Cách hiểu luồng Metrics → Logs → Traces:**
  - **Metrics** (Tầng vĩ mô): Giúp phát hiện triệu chứng bất thường trên toàn hệ thống (ví dụ: P95 latency tăng từ 155ms lên 2652ms) và xác định khung thời gian xảy ra sự cố.
  - **Logs** (Tầng trung gian): Dựa vào khung thời gian từ metrics, truy vấn file log để tìm các bản ghi bị ảnh hưởng (ví dụ: các dòng log `response_sent` có `latency_ms > 2000`) và trích xuất định danh duy nhất của request là `correlation_id`.
  - **Traces** (Tầng vi mô): Dùng `correlation_id` để mở trace phân tán tương ứng, quan sát biểu đồ cây quan hệ cha-con (waterfall). Từ đó định vị chính xác span cụ thể gây lỗi/chậm (span `retrieval` tốn 2500ms) để đưa ra kết luận root cause.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
  Trong hệ thống LLM Production, prompt chính là "mã nguồn" quyết định hành vi mô hình. Việc quản lý prompt versioning tập trung qua Langfuse cho phép decouple hoàn toàn giữa việc tinh chỉnh prompt và việc deploy code ứng dụng. Gắn label (`baseline`, `candidate`, `production`) cho phép kiểm thử A/B hoặc Canary release và đặc biệt là khả năng rollback tức thì (zero downtime) khi prompt mới gây ảo giác hoặc làm bùng nổ token/cost. Quản lý token/cost và giám sát SLO liên tục giúp ngăn ngừa rủi ro cạn kiệt ngân sách hoặc vi phạm cam kết chất lượng dịch vụ với khách hàng.
- **Điều quan trọng nhất đã học:**
  Nắm vững quy trình Observability chuẩn chỉnh cho LLMOps: kết hợp hài hòa giữa Structured Logging, Metrics phân vị (P50/P95/P99), và Tracing phân tán để biến AI API "hộp đen" thành một hệ thống trong suốt, có thể giải trình và khắc phục sự cố nhanh chóng.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**
  Mô hình LLM và Vector DB trong bài lab là dạng mô phỏng (fake/mock). Trong môi trường thực tế cần tích hợp OpenTelemetry exporter với các vector database thực (như Pinecone, Qdrant) và LLM API thực (như OpenAI, Anthropic, Gemini).

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
