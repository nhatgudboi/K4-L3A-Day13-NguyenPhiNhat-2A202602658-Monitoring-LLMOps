from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

LOG_PATH = Path("data/logs.jsonl")
OUTPUT_PATH = Path("submission/evidence/11-dashboard-overview.png")


def parse_iso(ts_str: str) -> datetime:
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))


def percentile(values: list[float | int], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = max(0, min(len(s) - 1, round((p / 100) * len(s) + 0.5) - 1))
    return float(s[idx])


def load_metrics(log_path: Path = LOG_PATH) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    req_received = [r for r in records if r.get("event") == "request_received"]
    resp_sent = [r for r in records if r.get("event") == "response_sent"]
    req_failed = [r for r in records if r.get("event") == "request_failed"]

    latencies = [r["latency_ms"] for r in resp_sent if "latency_ms" in r and r["latency_ms"] is not None]
    ttfts = [r["ttft_ms"] for r in resp_sent if "ttft_ms" in r and r["ttft_ms"] is not None]

    p50_lat = percentile(latencies, 50)
    p95_lat = percentile(latencies, 95)
    p99_lat = percentile(latencies, 99)
    p95_ttft = percentile(ttfts, 95)

    traffic_count = len(req_received)
    # calculate rate per minute based on time range
    if req_received:
        timestamps = [parse_iso(r["ts"]) for r in req_received if "ts" in r]
        duration_sec = max(1.0, (max(timestamps) - min(timestamps)).total_seconds())
        rate_per_min = (traffic_count / duration_sec) * 60.0
    else:
        rate_per_min = 0.0

    total_reqs = traffic_count or (len(resp_sent) + len(req_failed)) or 1
    error_rate_pct = (len(req_failed) / total_reqs) * 100.0

    tool_success_count = sum(1 for r in resp_sent if r.get("tool_success") is True)
    tool_total = tool_success_count + len([r for r in req_failed if r.get("tool_name") == "retrieval"]) or 1
    tool_success_rate_pct = (tool_success_count / tool_total) * 100.0

    costs = [r.get("cost_usd", 0.0) for r in resp_sent]
    total_cost = sum(costs)

    tokens_in = sum(r.get("tokens_in", 0) for r in resp_sent)
    tokens_out = sum(r.get("tokens_out", 0) for r in resp_sent)

    quality_scores = [r["quality_score"] for r in resp_sent if "quality_score" in r and r["quality_score"] is not None]
    avg_quality = (sum(quality_scores) / len(quality_scores)) if quality_scores else 0.0

    return {
        "p50_lat": p50_lat,
        "p95_lat": p95_lat,
        "p99_lat": p99_lat,
        "p95_ttft": p95_ttft,
        "latencies": latencies,
        "ttfts": ttfts,
        "traffic_count": traffic_count,
        "rate_per_min": rate_per_min,
        "error_rate_pct": error_rate_pct,
        "req_failed_count": len(req_failed),
        "tool_success_rate_pct": tool_success_rate_pct,
        "total_cost": total_cost,
        "costs": costs,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "avg_quality": avg_quality,
        "quality_scores": quality_scores,
    }


def render_dashboard(metrics: dict[str, Any], output_path: Path = OUTPUT_PATH, title_suffix: str = "") -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.style.use("dark_background")
    fig = plt.figure(figsize=(16, 10), dpi=150)
    fig.patch.set_facecolor("#0f172a")

    # Header
    fig.suptitle(
        f"K4-L3A Day 13 Monitoring & LLMOps Dashboard — Runtime 6-Panels {title_suffix}\n"
        f"Window: 60m | Refresh: 30s | Source: data/logs.jsonl | Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        fontsize=16,
        fontweight="bold",
        color="#f8fafc",
        y=0.97,
    )

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.25, top=0.90, bottom=0.08, left=0.07, right=0.95)

    # Panel 1: Latency & TTFT
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#1e293b")
    ax1.set_title("1. Latency Percentiles & TTFT (ms)\n[Threshold: P95 <= 3000 ms]", fontsize=11, fontweight="bold", color="#38bdf8", pad=8)
    bars = ax1.bar(["P50", "P95", "P99", "TTFT P95"], [metrics["p50_lat"], metrics["p95_lat"], metrics["p99_lat"], metrics["p95_ttft"]], color=["#38bdf8", "#818cf8", "#c084fc", "#4ade80"])
    ax1.axhline(3000, color="#ef4444", linestyle="--", linewidth=1.5, label="SLO Threshold: 3000ms")
    ax1.set_ylabel("Milliseconds (ms)", color="#94a3b8", fontsize=9)
    ax1.legend(loc="upper right", fontsize=8, facecolor="#0f172a", edgecolor="#475569")
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}ms", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#f1f5f9", fontweight="bold")
    ax1.tick_params(colors="#94a3b8", labelsize=8)
    ax1.grid(axis="y", linestyle=":", alpha=0.3, color="#64748b")

    # Panel 2: Request Traffic
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#1e293b")
    ax2.set_title("2. Request Traffic (req/min)\n[Threshold: Rate >= 1 req/min]", fontsize=11, fontweight="bold", color="#38bdf8", pad=8)
    ax2.bar(["Total Requests", "Rate/Min (est)"], [metrics["traffic_count"], metrics["rate_per_min"]], color=["#0ea5e9", "#06b6d4"])
    ax2.axhline(1.0, color="#22c55e", linestyle="--", linewidth=1.5, label="Min Threshold: 1 req/min")
    ax2.set_ylabel("Requests", color="#94a3b8", fontsize=9)
    ax2.legend(loc="upper right", fontsize=8, facecolor="#0f172a", edgecolor="#475569")
    for bar in ax2.patches:
        h = bar.get_height()
        ax2.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#f1f5f9", fontweight="bold")
    ax2.tick_params(colors="#94a3b8", labelsize=8)
    ax2.grid(axis="y", linestyle=":", alpha=0.3, color="#64748b")

    # Panel 3: Error Rate and Retrieval Success
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor("#1e293b")
    ax3.set_title("3. Error Rate & Retrieval Success (%)\n[Threshold: Error <= 2%]", fontsize=11, fontweight="bold", color="#38bdf8", pad=8)
    bars3 = ax3.bar(["Error Rate %", "Retrieval Success %"], [metrics["error_rate_pct"], metrics["tool_success_rate_pct"]], color=["#f43f5e" if metrics["error_rate_pct"] > 2 else "#22c55e", "#10b981"])
    ax3.axhline(2.0, color="#f43f5e", linestyle="--", linewidth=1.5, label="Max Error: 2%")
    ax3.set_ylabel("Percentage (%)", color="#94a3b8", fontsize=9)
    ax3.set_ylim(0, 110)
    ax3.legend(loc="upper right", fontsize=8, facecolor="#0f172a", edgecolor="#475569")
    for bar in bars3:
        h = bar.get_height()
        ax3.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#f1f5f9", fontweight="bold")
    ax3.tick_params(colors="#94a3b8", labelsize=8)
    ax3.grid(axis="y", linestyle=":", alpha=0.3, color="#64748b")

    # Panel 4: Cost Over Time
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor("#1e293b")
    ax4.set_title("4. Cost Over Time ($ USD)\n[Threshold: Total <= $2.50]", fontsize=11, fontweight="bold", color="#38bdf8", pad=8)
    if metrics["costs"]:
        ax4.plot(range(1, len(metrics["costs"]) + 1), metrics["costs"], marker="o", color="#fbbf24", linewidth=2, label="Cost/req ($)")
    ax4.axhline(2.50, color="#ef4444", linestyle="--", linewidth=1.5, label="Max Budget: $2.50")
    ax4.set_xlabel("Request sequence", color="#94a3b8", fontsize=9)
    ax4.set_ylabel("USD ($)", color="#94a3b8", fontsize=9)
    ax4.annotate(f"Total: ${metrics['total_cost']:.5f}", xy=(0.05, 0.85), xycoords="axes fraction", fontsize=10, color="#fde047", fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="#0f172a", ec="#fbbf24"))
    ax4.legend(loc="upper right", fontsize=8, facecolor="#0f172a", edgecolor="#475569")
    ax4.tick_params(colors="#94a3b8", labelsize=8)
    ax4.grid(axis="both", linestyle=":", alpha=0.3, color="#64748b")

    # Panel 5: Input & Output Tokens
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor("#1e293b")
    ax5.set_title("5. Input & Output Tokens (tokens)\n[Threshold: Total <= 50,000]", fontsize=11, fontweight="bold", color="#38bdf8", pad=8)
    tot_tok = metrics["tokens_in"] + metrics["tokens_out"]
    bars5 = ax5.bar(["Tokens In", "Tokens Out", "Total Tokens"], [metrics["tokens_in"], metrics["tokens_out"], tot_tok], color=["#a855f7", "#ec4899", "#8b5cf6"])
    ax5.axhline(50000, color="#ef4444", linestyle="--", linewidth=1.5, label="Threshold: 50k")
    ax5.set_ylabel("Token count", color="#94a3b8", fontsize=9)
    ax5.legend(loc="upper right", fontsize=8, facecolor="#0f172a", edgecolor="#475569")
    for bar in bars5:
        h = bar.get_height()
        ax5.annotate(f"{h:,}", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#f1f5f9", fontweight="bold")
    ax5.tick_params(colors="#94a3b8", labelsize=8)
    ax5.grid(axis="y", linestyle=":", alpha=0.3, color="#64748b")

    # Panel 6: Quality Proxy
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor("#1e293b")
    ax6.set_title("6. Quality Proxy (score 0.0 - 1.0)\n[Threshold: Mean >= 0.75]", fontsize=11, fontweight="bold", color="#38bdf8", pad=8)
    bars6 = ax6.bar(["Average Quality"], [metrics["avg_quality"]], color=["#22c55e" if metrics["avg_quality"] >= 0.75 else "#eab308"], width=0.4)
    ax6.axhline(0.75, color="#22c55e", linestyle="--", linewidth=1.5, label="Target SLO: >= 0.75")
    ax6.set_ylim(0, 1.1)
    ax6.set_ylabel("Score (0.0 - 1.0)", color="#94a3b8", fontsize=9)
    ax6.legend(loc="upper right", fontsize=8, facecolor="#0f172a", edgecolor="#475569")
    for bar in bars6:
        h = bar.get_height()
        ax6.annotate(f"{h:.2f} / 1.0", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=10, color="#f1f5f9", fontweight="bold")
    ax6.tick_params(colors="#94a3b8", labelsize=8)
    ax6.grid(axis="y", linestyle=":", alpha=0.3, color="#64748b")

    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Dashboard saved successfully to {output_path}")


if __name__ == "__main__":
    m = load_metrics()
    render_dashboard(m)
