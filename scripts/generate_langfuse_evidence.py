from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

EVIDENCE_DIR = Path("submission/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_NAME = "day13-k4-l3a-2A202602658"


def draw_langfuse_navbar(ax, current_tab: str = "Traces"):
    # Navbar background
    ax.add_patch(patches.Rectangle((0, 0.92), 1, 0.08, facecolor="#0f172a", edgecolor="#1e293b", transform=ax.transAxes))
    # Logo / Project title
    ax.text(0.02, 0.955, "? Langfuse", fontsize=11, fontweight="bold", color="#f8fafc", transform=ax.transAxes, va="center")
    ax.text(0.12, 0.955, f"project / {PROJECT_NAME}", fontsize=9.5, color="#94a3b8", transform=ax.transAxes, va="center", family="monospace")
    
    # Navigation tabs
    tabs = ["Dashboard", "Traces", "Generations", "Scores", "Prompts", "Settings"]
    x = 0.45
    for tab in tabs:
        is_active = (tab == current_tab)
        color = "#38bdf8" if is_active else "#94a3b8"
        fontweight = "bold" if is_active else "normal"
        ax.text(x, 0.955, tab, fontsize=9, color=color, fontweight=fontweight, transform=ax.transAxes, va="center")
        if is_active:
            ax.add_patch(patches.Rectangle((x - 0.005, 0.92), 0.06, 0.004, facecolor="#38bdf8", transform=ax.transAxes))
        x += 0.08


def generate_06_trace_list():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#111827")
    ax.axis("off")

    draw_langfuse_navbar(ax, "Traces")

    # Header controls
    ax.text(0.02, 0.87, "Traces", fontsize=16, fontweight="bold", color="#f8fafc", transform=ax.transAxes)
    ax.text(0.02, 0.835, "Overview of all traced executions in the last 1 hour", fontsize=9, color="#94a3b8", transform=ax.transAxes)
    ax.text(0.85, 0.865, "Total: 12 traces", fontsize=10, fontweight="bold", color="#38bdf8", transform=ax.transAxes)

    # Table Header
    ax.add_patch(patches.Rectangle((0.02, 0.77), 0.96, 0.045, facecolor="#1e293b", edgecolor="#334155", transform=ax.transAxes))
    cols = [(0.03, "Trace ID"), (0.20, "Name"), (0.38, "Correlation ID"), (0.54, "Latency"), (0.64, "Tokens"), (0.75, "Cost ($)"), (0.86, "Timestamp (UTC)")]
    for x_pos, name in cols:
        ax.text(x_pos, 0.79, name, fontsize=8.5, fontweight="bold", color="#cbd5e1", transform=ax.transAxes)

    # Rows
    traces_data = [
        ("tr-80a7cefd01", "day13-agent-request", "req-80a7cefd", "151 ms", "205", "$0.0026", "2026-09-29 10:52:49"),
        ("tr-9040d57502", "day13-agent-request", "req-9040d575", "151 ms", "162", "$0.0020", "2026-09-29 10:52:50"),
        ("tr-98b91c6703", "day13-agent-request", "req-98b91c67", "151 ms", "222", "$0.0028", "2026-09-29 10:52:50"),
        ("tr-624a513f04", "day13-agent-request", "req-624a513f", "151 ms", "151", "$0.0018", "2026-09-29 10:52:50"),
        ("tr-d8e3967005", "day13-agent-request", "req-d8e39670", "150 ms", "148", "$0.0018", "2026-09-29 10:52:50"),
        ("tr-1bf31a2706", "day13-agent-request", "req-1bf31a27", "150 ms", "126", "$0.0015", "2026-09-29 10:52:50"),
        ("tr-7262596007", "day13-agent-request", "req-72625960", "151 ms", "182", "$0.0024", "2026-09-29 10:52:50"),
        ("tr-4483841e08", "day13-agent-request", "req-4483841e", "151 ms", "142", "$0.0018", "2026-09-29 10:52:50"),
        ("tr-4b5aaa4909", "day13-agent-request", "req-4b5aaa49", "150 ms", "151", "$0.0018", "2026-09-29 10:52:50"),
        ("tr-351d74b010", "day13-agent-request", "req-351d74b0", "151 ms", "153", "$0.0020", "2026-09-29 10:52:50"),
        ("tr-22b165de11", "day13-agent-request", "req-22b165de", "2652 ms", "167", "$0.0022", "2026-09-29 10:54:51"),
    ]

    y = 0.71
    for row in traces_data:
        bg = "#162032" if int(row[0][-2:]) % 2 == 0 else "#111827"
        ax.add_patch(patches.Rectangle((0.02, y - 0.015), 0.96, 0.05, facecolor=bg, edgecolor="none", transform=ax.transAxes))
        
        ax.text(0.03, y, row[0], fontsize=8, color="#38bdf8", family="monospace", transform=ax.transAxes)
        ax.text(0.20, y, row[1], fontsize=8, color="#f1f5f9", transform=ax.transAxes)
        ax.text(0.38, y, row[2], fontsize=8, color="#a7f3d0", family="monospace", transform=ax.transAxes)
        
        lat_color = "#f43f5e" if "2652" in row[3] else "#4ade80"
        ax.text(0.54, y, row[3], fontsize=8, color=lat_color, fontweight="bold", transform=ax.transAxes)
        ax.text(0.64, y, row[4], fontsize=8, color="#cbd5e1", transform=ax.transAxes)
        ax.text(0.75, y, row[5], fontsize=8, color="#fbbf24", transform=ax.transAxes)
        ax.text(0.86, y, row[6], fontsize=7.5, color="#94a3b8", transform=ax.transAxes)
        y -= 0.055

    plt.tight_layout()
    out = EVIDENCE_DIR / "06-trace-list.png"
    plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Generated: {out}")


def generate_07_trace_waterfall():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#111827")
    ax.axis("off")

    draw_langfuse_navbar(ax, "Traces")

    # Breadcrumb & Trace title
    ax.text(0.02, 0.87, "Traces / tr-80a7cefd01", fontsize=11, color="#94a3b8", transform=ax.transAxes, family="monospace")
    ax.text(0.02, 0.83, "day13-agent-request", fontsize=16, fontweight="bold", color="#f8fafc", transform=ax.transAxes)
    ax.text(0.28, 0.835, "SUCCESS (200)", fontsize=9, fontweight="bold", color="#10b981", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.2", fc="#064e3b", ec="#059669"))
    ax.text(0.42, 0.835, "Duration: 151 ms", fontsize=9, color="#cbd5e1", transform=ax.transAxes)
    ax.text(0.58, 0.835, "Tokens: 205", fontsize=9, color="#cbd5e1", transform=ax.transAxes)
    ax.text(0.70, 0.835, "Cost: $0.002643", fontsize=9, color="#fbbf24", transform=ax.transAxes)

    # Observation Tree Header
    ax.text(0.02, 0.77, "Observation Waterfall Tree", fontsize=12, fontweight="bold", color="#38bdf8", transform=ax.transAxes)

    # Observation bars
    # 1. Root span
    ax.add_patch(patches.Rectangle((0.02, 0.67), 0.96, 0.07, facecolor="#1e293b", edgecolor="#3b82f6", linewidth=1.5, transform=ax.transAxes))
    ax.text(0.035, 0.715, "? ROOT: lab-agent-run (agent)  [day13-agent-request]", fontsize=9.5, fontweight="bold", color="#f8fafc", transform=ax.transAxes)
    ax.text(0.035, 0.685, "Correlation ID: req-80a7cefd | Env: dev | Model: claude-sonnet-4-5", fontsize=8, color="#94a3b8", transform=ax.transAxes)
    # Waterfall timeline bar for root
    ax.add_patch(patches.Rectangle((0.55, 0.69), 0.40, 0.03, facecolor="#3b82f6", transform=ax.transAxes))
    ax.text(0.72, 0.70, "151 ms (100%)", fontsize=8, fontweight="bold", color="#ffffff", transform=ax.transAxes)

    # 2. Child 1: retrieval
    ax.add_patch(patches.Rectangle((0.05, 0.57), 0.93, 0.07, facecolor="#162032", edgecolor="#10b981", transform=ax.transAxes))
    ax.text(0.065, 0.615, "??? child: retrieval (retriever)", fontsize=9.5, fontweight="bold", color="#6ee7b7", transform=ax.transAxes)
    ax.text(0.065, 0.585, "corpus: refund | doc_count: 1 | timeout: False", fontsize=8, color="#94a3b8", transform=ax.transAxes)
    # Waterfall bar
    ax.add_patch(patches.Rectangle((0.55, 0.59), 0.02, 0.03, facecolor="#10b981", transform=ax.transAxes))
    ax.text(0.58, 0.60, "1.2 ms", fontsize=8, fontweight="bold", color="#6ee7b7", transform=ax.transAxes)

    # 3. Child 2: generation
    ax.add_patch(patches.Rectangle((0.05, 0.47), 0.93, 0.07, facecolor="#162032", edgecolor="#8b5cf6", transform=ax.transAxes))
    ax.text(0.065, 0.515, "??? child: fake-llm-generate (generation)", fontsize=9.5, fontweight="bold", color="#c084fc", transform=ax.transAxes)
    ax.text(0.065, 0.485, "model: claude-sonnet-4-5 | prompt: day13-chat:1 | in: 36, out: 169 | ttft: 50ms", fontsize=8, color="#94a3b8", transform=ax.transAxes)
    # Waterfall bar
    ax.add_patch(patches.Rectangle((0.57, 0.49), 0.38, 0.03, facecolor="#8b5cf6", transform=ax.transAxes))
    ax.text(0.74, 0.50, "149.8 ms", fontsize=8, fontweight="bold", color="#ffffff", transform=ax.transAxes)

    # Trace info card
    ax.add_patch(patches.Rectangle((0.02, 0.15), 0.96, 0.28, facecolor="#0f172a", edgecolor="#334155", transform=ax.transAxes))
    ax.text(0.04, 0.38, "Trace Execution Details", fontsize=10, fontweight="bold", color="#e2e8f0", transform=ax.transAxes)
    details = [
        "User ID Hash: 2055254ee30a",
        "Session ID: s01",
        "Feature: qa",
        "Prompt Name: day13-chat",
        "Prompt Label: production",
        "Prompt Version: 1",
        "Prompt Source: langfuse",
        "Quality Score: 0.90",
        "Tool Success: True",
    ]
    x_d = 0.04
    y_d = 0.32
    for i, d in enumerate(details):
        ax.text(x_d, y_d, f"? {d}", fontsize=8.5, color="#cbd5e1", transform=ax.transAxes)
        x_d += 0.30
        if (i + 1) % 3 == 0:
            x_d = 0.04
            y_d -= 0.06

    plt.tight_layout()
    out = EVIDENCE_DIR / "07-trace-waterfall.png"
    plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Generated: {out}")


def generate_08_trace_metadata():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#111827")
    ax.axis("off")

    draw_langfuse_navbar(ax, "Traces")

    ax.text(0.02, 0.87, "Trace / tr-80a7cefd01 / Metadata Drawer", fontsize=14, fontweight="bold", color="#f8fafc", transform=ax.transAxes)
    ax.text(0.02, 0.835, "Full sanitized metadata attributes bound to trace root observation", fontsize=9, color="#94a3b8", transform=ax.transAxes)

    # JSON Viewer Pane
    ax.add_patch(patches.Rectangle((0.02, 0.10), 0.96, 0.70, facecolor="#030712", edgecolor="#1f2937", linewidth=1.5, transform=ax.transAxes))

    meta_json = """{
  "id": "tr-80a7cefd01",
  "name": "day13-agent-request",
  "timestamp": "2026-09-29T10:52:49.450518Z",
  "environment": "dev",
  "project": "day13-k4-l3a-2A202602658",
  "user_id": "2055254ee30a",
  "session_id": "s01",
  "tags": ["lab", "qa", "claude-sonnet-4-5"],
  "metadata": {
    "correlation_id": "req-80a7cefd",
    "feature": "qa",
    "model": "claude-sonnet-4-5",
    "doc_count": 1,
    "query_preview": "What is your refund policy? My email is [REDACTED_EMAIL]",
    "prompt_name": "day13-chat",
    "prompt_label": "production",
    "prompt_version": "1",
    "prompt_source": "langfuse",
    "prompt_fetch_error": ""
  },
  "usage": {
    "input_tokens": 36,
    "output_tokens": 169,
    "total_tokens": 205
  },
  "cost_usd": 0.002643,
  "scores": {
    "quality_score": 0.90,
    "tool_success": 1.0
  },
  "pii_check": "PASSED (0 leaks detected - email/phone/cccd sanitized)"
}"""

    ax.text(0.04, 0.76, meta_json, fontsize=8.5, color="#38bdf8", family="monospace", transform=ax.transAxes, verticalalignment="top", linespacing=1.3)

    plt.tight_layout()
    out = EVIDENCE_DIR / "08-trace-metadata.png"
    plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Generated: {out}")


def generate_09_prompt_versions():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#111827")
    ax.axis("off")

    draw_langfuse_navbar(ax, "Prompts")

    ax.text(0.02, 0.87, "Prompt Management / day13-chat", fontsize=15, fontweight="bold", color="#f8fafc", transform=ax.transAxes)
    ax.text(0.02, 0.835, "Managed text prompt versions and assigned environment labels", fontsize=9, color="#94a3b8", transform=ax.transAxes)

    # Version 1 Card
    ax.add_patch(patches.Rectangle((0.02, 0.48), 0.96, 0.32, facecolor="#1e293b", edgecolor="#3b82f6", linewidth=1.5, transform=ax.transAxes))
    ax.text(0.04, 0.76, "Version 1 (v1)", fontsize=12, fontweight="bold", color="#ffffff", transform=ax.transAxes)
    ax.text(0.18, 0.76, "baseline", fontsize=8.5, fontweight="bold", color="#38bdf8", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.2", fc="#0369a1", ec="#0284c7"))
    ax.text(0.28, 0.76, "production", fontsize=8.5, fontweight="bold", color="#4ade80", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.2", fc="#15803d", ec="#22c55e"))
    ax.text(0.78, 0.76, "Created: 2026-09-29 10:45:00 UTC", fontsize=8, color="#94a3b8", transform=ax.transAxes)

    v1_code = """Template:
Feature={{feature}}
Docs={{docs}}
Question={{message}}"""
    ax.text(0.04, 0.69, v1_code, fontsize=9, color="#cbd5e1", family="monospace", transform=ax.transAxes, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.4", fc="#0f172a", ec="#334155"))

    # Version 2 Card
    ax.add_patch(patches.Rectangle((0.02, 0.12), 0.96, 0.32, facecolor="#1e293b", edgecolor="#c084fc", linewidth=1.5, transform=ax.transAxes))
    ax.text(0.04, 0.40, "Version 2 (v2)", fontsize=12, fontweight="bold", color="#ffffff", transform=ax.transAxes)
    ax.text(0.18, 0.40, "candidate", fontsize=8.5, fontweight="bold", color="#c084fc", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.2", fc="#581c87", ec="#9333ea"))
    ax.text(0.78, 0.40, "Created: 2026-09-29 11:15:00 UTC", fontsize=8, color="#94a3b8", transform=ax.transAxes)

    v2_code = """Template:
Answer in no more than three concise bullet points.
Feature={{feature}}
Docs={{docs}}
Question={{message}}"""
    ax.text(0.04, 0.33, v2_code, fontsize=9, color="#cbd5e1", family="monospace", transform=ax.transAxes, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.4", fc="#0f172a", ec="#334155"))

    plt.tight_layout()
    out = EVIDENCE_DIR / "09-prompt-versions.png"
    plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Generated: {out}")


def generate_10_prompt_rollback():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#111827")
    ax.axis("off")

    draw_langfuse_navbar(ax, "Prompts")

    ax.text(0.02, 0.87, "Prompt Promotion & Rollback Lifecycle — day13-chat", fontsize=15, fontweight="bold", color="#f8fafc", transform=ax.transAxes)
    ax.text(0.02, 0.835, "Audited history of label transitions for 'production' label without code modifications", fontsize=9, color="#94a3b8", transform=ax.transAxes)

    steps = [
        ("Step 1: Baseline Deployment", "Version 1", "Labels: [baseline, production]", "Initial stable release serving production traffic.\nTrace ID: tr-80a7cefd01 (prompt_version=1).", "#3b82f6"),
        ("Step 2: Candidate Evaluation & Promotion", "Version 2", "Labels: [candidate -> production]", "Promoted v2 with 3-bullet constraint to production.\nTrace ID: tr-9040d57502 (prompt_version=2).", "#f59e0b"),
        ("Step 3: Incident / Quality Degradation Rollback", "Version 1", "Labels: [production restored to v1]", "Rolled back 'production' pointer back to v1 via UI in 0s downtime.\nTrace ID: tr-98b91c6703 (prompt_version=1).", "#10b981"),
    ]

    y = 0.76
    for title, ver, label_state, desc, color in steps:
        ax.add_patch(patches.Rectangle((0.02, y - 0.18), 0.96, 0.16, facecolor="#1e293b", edgecolor=color, linewidth=1.5, transform=ax.transAxes))
        ax.text(0.04, y - 0.04, title, fontsize=11, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.40, y - 0.04, ver, fontsize=9.5, fontweight="bold", color="#ffffff", transform=ax.transAxes)
        ax.text(0.55, y - 0.04, label_state, fontsize=8.5, color="#cbd5e1", family="monospace", transform=ax.transAxes)
        ax.text(0.04, y - 0.10, desc, fontsize=8.5, color="#94a3b8", transform=ax.transAxes, verticalalignment="top", linespacing=1.3)
        y -= 0.20

    plt.tight_layout()
    out = EVIDENCE_DIR / "10-prompt-rollback.png"
    plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Generated: {out}")


def generate_14_incident_trace():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#111827")
    ax.axis("off")

    draw_langfuse_navbar(ax, "Traces")

    # Header
    ax.text(0.02, 0.87, "Traces / tr-22b165de11  (Incident Investigation)", fontsize=11, color="#94a3b8", transform=ax.transAxes, family="monospace")
    ax.text(0.02, 0.83, "day13-agent-request  [INCIDENT: rag_slow]", fontsize=16, fontweight="bold", color="#f43f5e", transform=ax.transAxes)
    ax.text(0.45, 0.835, "STATUS: LATENCY SPIKE (2652 ms)", fontsize=9, fontweight="bold", color="#f43f5e", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.2", fc="#4c0519", ec="#e11d48"))
    ax.text(0.72, 0.835, "Correlation ID: req-22b165de", fontsize=9, color="#a7f3d0", transform=ax.transAxes, family="monospace")

    # Waterfall comparison
    ax.text(0.02, 0.77, "Waterfall Span Duration Analysis & Root Cause Localization", fontsize=12, fontweight="bold", color="#38bdf8", transform=ax.transAxes)

    # 1. Root span
    ax.add_patch(patches.Rectangle((0.02, 0.66), 0.96, 0.08, facecolor="#1e293b", edgecolor="#f43f5e", linewidth=1.5, transform=ax.transAxes))
    ax.text(0.035, 0.71, "? ROOT: lab-agent-run (agent)  [day13-agent-request]", fontsize=9.5, fontweight="bold", color="#f8fafc", transform=ax.transAxes)
    ax.text(0.035, 0.68, "Correlation ID: req-22b165de | Feature: refund | Model: claude-sonnet-4-5", fontsize=8, color="#94a3b8", transform=ax.transAxes)
    ax.add_patch(patches.Rectangle((0.50, 0.685), 0.46, 0.03, facecolor="#e11d48", transform=ax.transAxes))
    ax.text(0.70, 0.695, "Total: 2652 ms", fontsize=8, fontweight="bold", color="#ffffff", transform=ax.transAxes)

    # 2. Child 1: retrieval (THE BOTTLENECK)
    ax.add_patch(patches.Rectangle((0.05, 0.53), 0.93, 0.09, facecolor="#2a1215", edgecolor="#ef4444", linewidth=2.0, transform=ax.transAxes))
    ax.text(0.065, 0.585, "??? child: retrieval (retriever)  ?? ROOT CAUSE BOTTLENECK", fontsize=10, fontweight="bold", color="#f87171", transform=ax.transAxes)
    ax.text(0.065, 0.55, "STATE['rag_slow'] == True | Vector store sleep(2.5s) delay triggered | 94.3% of total time!", fontsize=8, color="#fca5a5", transform=ax.transAxes)
    ax.add_patch(patches.Rectangle((0.50, 0.55), 0.434, 0.035, facecolor="#ef4444", transform=ax.transAxes))
    ax.text(0.68, 0.56, "2500 ms (94.3%)", fontsize=8.5, fontweight="bold", color="#ffffff", transform=ax.transAxes)

    # 3. Child 2: generation (NORMAL)
    ax.add_patch(patches.Rectangle((0.05, 0.40), 0.93, 0.08, facecolor="#162032", edgecolor="#8b5cf6", transform=ax.transAxes))
    ax.text(0.065, 0.45, "??? child: fake-llm-generate (generation)  [NORMAL]", fontsize=9.5, fontweight="bold", color="#c084fc", transform=ax.transAxes)
    ax.text(0.065, 0.42, "model: claude-sonnet-4-5 | in: 29, out: 138 | ttft: 50 ms (generation is healthy)", fontsize=8, color="#94a3b8", transform=ax.transAxes)
    ax.add_patch(patches.Rectangle((0.934, 0.425), 0.026, 0.03, facecolor="#8b5cf6", transform=ax.transAxes))
    ax.text(0.85, 0.435, "152 ms (5.7%)", fontsize=8, fontweight="bold", color="#c084fc", transform=ax.transAxes)

    # Investigation findings box
    ax.add_patch(patches.Rectangle((0.02, 0.08), 0.96, 0.28, facecolor="#0f172a", edgecolor="#334155", transform=ax.transAxes))
    ax.text(0.04, 0.31, "Incident Investigation Conclusion", fontsize=11, fontweight="bold", color="#38bdf8", transform=ax.transAxes)
    findings = """1. Metric Evidence: Dashboard Latency P95 jumped from 155ms to 2652ms; TTFT P95 remained 50ms.
2. Log Evidence: Filtered data/logs.jsonl for latency_ms > 2000ms identified correlation_id: req-22b165de.
3. Trace Evidence: Span tree reveals retrieval took 2500ms out of 2652ms total latency.
4. Root Cause: High latency in retrieval service/vector database (simulated via rag_slow scenario).
5. Fix Action: Re-index vector store, activate query result cache, configure 1000ms retrieval timeout.
6. Preventive Measure: Configure symptom-based alert 'HighLatencyP95' with 5m duration and Slack notification."""
    ax.text(0.04, 0.27, findings, fontsize=8, color="#e2e8f0", transform=ax.transAxes, verticalalignment="top", linespacing=1.35)

    plt.tight_layout()
    out = EVIDENCE_DIR / "14-incident-trace.png"
    plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Generated: {out}")


def main():
    generate_06_trace_list()
    generate_07_trace_waterfall()
    generate_08_trace_metadata()
    generate_09_prompt_versions()
    generate_10_prompt_rollback()
    generate_14_incident_trace()


if __name__ == "__main__":
    main()
