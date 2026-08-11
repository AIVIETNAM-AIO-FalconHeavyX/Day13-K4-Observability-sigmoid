from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


LOG_PATH = Path("data/logs.jsonl")
WINDOW_MINUTES = 60
REFRESH_SECONDS = 30
K4_LATENCY_THRESHOLD_MS = 2000
CONTRACT_LATENCY_THRESHOLD_MS = 3000
ERROR_THRESHOLD_PCT = 2
COST_THRESHOLD_USD = 2.5
QUALITY_THRESHOLD = 0.75


def load_logs(path: Path = LOG_PATH) -> tuple[pd.DataFrame, int]:
    """Read JSONL logs, retaining valid objects and counting malformed lines."""
    records: list[dict] = []
    invalid = 0
    if not path.exists():
        return pd.DataFrame(), invalid
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            invalid += 1
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            invalid += 1
    frame = pd.DataFrame.from_records(records)
    if not frame.empty and "ts" in frame:
        frame["ts"] = pd.to_datetime(frame["ts"], utc=True, errors="coerce")
        frame = frame.dropna(subset=["ts"])
    return frame, invalid


def last_window(frame: pd.DataFrame, minutes: int = WINDOW_MINUTES) -> pd.DataFrame:
    if frame.empty or "ts" not in frame:
        return frame
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=minutes)
    return frame.loc[frame["ts"] >= cutoff].copy()


def percentile(series: pd.Series, quantile: float) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna()
    return float(values.quantile(quantile)) if not values.empty else 0.0


def add_threshold(fig: go.Figure, value: float, label: str, color: str = "#d62728") -> None:
    fig.add_hline(
        y=value,
        line_dash="dash",
        line_color=color,
        annotation_text=label,
        annotation_position="top left",
    )


def empty_panel(message: str) -> None:
    st.info(message)


def render_dashboard() -> None:
    frame, invalid = load_logs()
    data = last_window(frame)
    st.caption(
        f"Nguồn: {LOG_PATH} · Time range: {WINDOW_MINUTES} phút · "
        f"Refresh: {REFRESH_SECONDS} giây · Cập nhật: {pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M:%S UTC}"
    )
    if invalid:
        st.warning(f"Đã bỏ qua {invalid} dòng JSON không hợp lệ.")
    if data.empty:
        st.warning("Không có log hợp lệ trong 60 phút gần nhất. Hãy chạy scripts/load_test.py.")

    responses = data.loc[data.get("event", pd.Series(index=data.index, dtype=str)) == "response_sent"].copy()
    requests = data.loc[data.get("event", pd.Series(index=data.index, dtype=str)) == "request_received"].copy()
    failures = data.loc[data.get("event", pd.Series(index=data.index, dtype=str)) == "request_failed"].copy()

    st.subheader("1. Latency percentiles")
    if responses.empty or "latency_ms" not in responses:
        empty_panel("Chưa có response_sent.latency_ms.")
    else:
        p50 = percentile(responses["latency_ms"], 0.50)
        p95 = percentile(responses["latency_ms"], 0.95)
        p99 = percentile(responses["latency_ms"], 0.99)
        cols = st.columns(3)
        cols[0].metric("P50", f"{p50:,.0f} ms")
        cols[1].metric("P95", f"{p95:,.0f} ms", delta=f"{p95-K4_LATENCY_THRESHOLD_MS:,.0f} ms vs K4", delta_color="inverse")
        cols[2].metric("P99", f"{p99:,.0f} ms")
        latency = responses.set_index("ts")["latency_ms"].resample("1min").quantile([0.5, 0.95, 0.99]).unstack()
        latency.columns = ["P50", "P95", "P99"]
        fig = px.line(latency, x=latency.index, y=list(latency.columns), labels={"value": "Latency (ms)", "ts": "Time", "variable": "Percentile"})
        add_threshold(fig, K4_LATENCY_THRESHOLD_MS, "K4 SLO: 2000 ms")
        add_threshold(fig, CONTRACT_LATENCY_THRESHOLD_MS, "Contract: 3000 ms", "#ff7f0e")
        st.plotly_chart(fig, width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("2. Request traffic")
        if requests.empty:
            empty_panel("Chưa có request_received.")
        else:
            traffic = requests.set_index("ts").resample("1min").size().rename("requests_per_minute")
            st.metric("Requests (60m)", f"{len(requests):,}")
            fig = px.bar(traffic, x=traffic.index, y="requests_per_minute", labels={"ts": "Time", "requests_per_minute": "requests/min"})
            add_threshold(fig, 1, "Minimum traffic: 1 req/min", "#2ca02c")
            st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("3. Error rate and breakdown")
        error_rate = len(failures) / len(requests) * 100 if len(requests) else 0.0
        st.metric("Error rate", f"{error_rate:.2f}%", delta=f"{error_rate-ERROR_THRESHOLD_PCT:.2f}% vs SLO", delta_color="inverse")
        if failures.empty:
            empty_panel("Không có request_failed trong cửa sổ hiện tại (breakdown trống).")
        else:
            error_types = failures.get("error_type", pd.Series("unknown", index=failures.index)).fillna("unknown").value_counts()
            fig = px.bar(error_types, x=error_types.index, y=error_types.values, labels={"x": "error_type", "y": "count"})
            st.plotly_chart(fig, width="stretch")
        st.caption("SLO threshold: error rate ≤ 2%")

    left, right = st.columns(2)
    with left:
        st.subheader("4. Cost over time")
        if responses.empty or "cost_usd" not in responses:
            empty_panel("Chưa có response_sent.cost_usd.")
        else:
            costs = pd.to_numeric(responses["cost_usd"], errors="coerce").fillna(0)
            total_cost = float(costs.sum())
            st.metric("Total cost (60m)", f"${total_cost:,.4f}", delta=f"${total_cost-COST_THRESHOLD_USD:,.4f} vs budget", delta_color="inverse")
            series = responses.assign(cost_usd=costs).set_index("ts")["cost_usd"].resample("1min").sum().cumsum()
            fig = px.line(series, x=series.index, y="cost_usd", labels={"ts": "Time", "cost_usd": "Cumulative cost (USD)"})
            add_threshold(fig, COST_THRESHOLD_USD, "Budget: $2.50")
            st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("5. Input and output tokens")
        if responses.empty or not {"tokens_in", "tokens_out"}.issubset(responses.columns):
            empty_panel("Chưa có tokens_in/tokens_out.")
        else:
            token_totals = pd.DataFrame({
                "field": ["tokens_in", "tokens_out"],
                "tokens": [pd.to_numeric(responses["tokens_in"], errors="coerce").sum(), pd.to_numeric(responses["tokens_out"], errors="coerce").sum()],
            })
            st.metric("Total tokens", f"{token_totals['tokens'].sum():,.0f}")
            fig = px.bar(token_totals, x="field", y="tokens", color="field", labels={"field": "Token type", "tokens": "Tokens"})
            add_threshold(fig, 50000, "Contract threshold: 50,000")
            st.plotly_chart(fig, width="stretch")

    st.subheader("6. Quality proxy")
    if responses.empty or "quality_score" not in responses:
        empty_panel("Chưa có response_sent.quality_score.")
    else:
        quality = pd.to_numeric(responses["quality_score"], errors="coerce")
        mean_quality = float(quality.mean())
        st.metric("Mean quality", f"{mean_quality:.3f}", delta=f"{mean_quality-QUALITY_THRESHOLD:+.3f} vs SLO")
        series = responses.assign(quality_score=quality).set_index("ts")["quality_score"].resample("1min").mean()
        fig = px.line(series, x=series.index, y="quality_score", markers=True, labels={"ts": "Time", "quality_score": "Score (0–1)"})
        add_threshold(fig, QUALITY_THRESHOLD, "SLO: 0.75", "#2ca02c")
        fig.update_yaxes(range=[0, 1])
        st.plotly_chart(fig, width="stretch")


st.set_page_config(page_title="Day 13 K4 Observability", page_icon="📊", layout="wide")
st.title("Day 13 K4 AI Observability Dashboard")
st.caption("Challenge: day13-k4-observability-v1 · Incident: rag_slow · K4 latency threshold: 2000 ms")


@st.fragment(run_every=f"{REFRESH_SECONDS}s")
def auto_refreshing_dashboard() -> None:
    render_dashboard()


auto_refreshing_dashboard()
