import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import time
from datetime import datetime, timedelta
from collections import Counter

st.set_page_config(
    page_title="VerifyIQ Dashboard",
    page_icon="✓",
    layout="wide",
)

_NAV_PAGES = ["Overview", "Claim History", "Fraud Analysis", "Risk Trends", "System Health"]


def _mock_claims(n=100):
    statuses = ["supported", "contradicted", "not_enough_information"]
    severities = ["low", "medium", "high", "none", "unknown"]
    risk_levels = ["low", "medium", "high", "critical"]
    fraud_types = ["none", "image_manipulation", "behavioral", "metadata", "multiple"]
    data = []
    for i in range(n):
        claim_id = f"CLM-{1000 + i:04d}"
        created = datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
        data.append({
            "claim_id": claim_id,
            "status": random.choice(statuses),
            "severity": random.choice(severities),
            "risk_level": random.choice(risk_levels),
            "fraud_type": random.choice(fraud_types),
            "fraud_score": round(random.uniform(0, 1), 3),
            "confidence": round(random.uniform(0.5, 1.0), 3),
            "created": created,
            "processed": created + timedelta(seconds=random.randint(5, 300)),
        })
    return pd.DataFrame(data)


def _mock_metrics():
    return {
        "total_claims": 1047,
        "fraud_count": 89,
        "fraud_rate": 0.085,
        "avg_confidence": 0.872,
        "avg_latency_ms": 1423.5,
        "uptime_pct": 99.7,
        "cache_hit_rate": 0.64,
        "model_requests": 12893,
    }


def _overview_page():
    st.title("System Overview")
    m = _mock_metrics()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Claims Processed", f"{m['total_claims']:,}", "+12%")
    col2.metric("Fraud Detected", f"{m['fraud_count']:,}", f"{m['fraud_rate']:.1%}")
    col3.metric("Avg Confidence", f"{m['avg_confidence']:.1%}", "+2.3%")
    col4.metric("Avg Latency", f"{m['avg_latency_ms']:.0f}ms", "-5.1%")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    claims = _mock_claims(50)
    status_counts = claims["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig1 = px.pie(status_counts, values="count", names="status", title="Claim Status Distribution", hole=0.4)
    col_a.plotly_chart(fig1, use_container_width=True)

    severity_counts = claims["severity"].value_counts().reset_index()
    severity_counts.columns = ["severity", "count"]
    fig2 = px.bar(severity_counts, x="severity", y="count", title="Claims by Severity", color="severity")
    col_b.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Recent Activity")
    activity = claims.sort_values("created", ascending=False).head(10)
    for _, row in activity.iterrows():
        st.text(f"{row['created'].strftime('%Y-%m-%d %H:%M')} — {row['claim_id']} — {row['status']} (risk: {row['risk_level']})")


def _claim_history_page():
    st.title("Claim History")
    claims = _mock_claims(200)

    st.markdown("### Filters")
    col1, col2, col3 = st.columns(3)
    status_filter = col1.multiselect("Status", options=claims["status"].unique(), default=list(claims["status"].unique()))
    risk_filter = col2.multiselect("Risk Level", options=claims["risk_level"].unique(), default=list(claims["risk_level"].unique()))
    severity_filter = col3.multiselect("Severity", options=claims["severity"].unique(), default=list(claims["severity"].unique()))

    filtered = claims[
        claims["status"].isin(status_filter)
        & claims["risk_level"].isin(risk_filter)
        & claims["severity"].isin(severity_filter)
    ]

    st.markdown(f"Showing {len(filtered)} of {len(claims)} claims")
    display = filtered[["claim_id", "created", "status", "severity", "risk_level", "fraud_score", "confidence"]]
    st.dataframe(display, use_container_width=True, hide_index=True)


def _fraud_analysis_page():
    st.title("Fraud Analysis")

    claims = _mock_claims(200)

    fraud_data = claims[claims["fraud_type"] != "none"]
    non_fraud = claims[claims["fraud_type"] == "none"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Fraud Cases", f"{len(fraud_data)}/{len(claims)}", f"{len(fraud_data)/len(claims):.1%}")
    col2.metric("Avg Fraud Score", f"{fraud_data['fraud_score'].mean():.3f}" if len(fraud_data) > 0 else "N/A")
    col3.metric("Non-Fraud Score", f"{non_fraud['fraud_score'].mean():.3f}" if len(non_fraud) > 0 else "N/A")

    col_a, col_b = st.columns(2)

    fraud_type_counts = claims["fraud_type"].value_counts().reset_index()
    fraud_type_counts.columns = ["fraud_type", "count"]
    fig1 = px.bar(fraud_type_counts, x="fraud_type", y="count", title="Fraud Flags Distribution", color="fraud_type")
    col_a.plotly_chart(fig1, use_container_width=True)

    if len(fraud_data) > 5:
        fig2 = px.histogram(fraud_data, x="fraud_score", nbins=20, title="Fraud Score Distribution", color_discrete_sequence=["red"])
        col_b.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Recent Fraud Detections")
    recent = claims[claims["fraud_type"] != "none"].sort_values("created", ascending=False).head(20)
    if len(recent) > 0:
        display = recent[["claim_id", "created", "fraud_type", "fraud_score", "risk_level"]]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No fraud cases in simulated data.")


def _risk_trends_page():
    st.title("Risk Trends")

    claims = _mock_claims(200)
    claims["date"] = claims["created"].dt.date

    col_a, col_b = st.columns(2)

    daily_risk = claims.groupby("date")["fraud_score"].mean().reset_index()
    daily_risk.columns = ["date", "avg_fraud_score"]
    fig1 = px.line(daily_risk, x="date", y="avg_fraud_score", title="Average Fraud Score Over Time", markers=True)
    col_a.plotly_chart(fig1, use_container_width=True)

    severity_risk = claims.groupby(["severity", "risk_level"]).size().reset_index(name="count")
    fig2 = px.bar(
        severity_risk,
        x="severity",
        y="count",
        color="risk_level",
        title="Severity vs Risk Level",
        barmode="stack",
    )
    col_b.plotly_chart(fig2, use_container_width=True)

    risk_counts = claims["risk_level"].value_counts().reset_index()
    risk_counts.columns = ["risk_level", "count"]
    fig3 = px.pie(risk_counts, values="count", names="risk_level", title="Risk Level Distribution", hole=0.4)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### Risk Summary by Severity")
    pivot = claims.pivot_table(index="severity", columns="risk_level", aggfunc="size", fill_value=0)
    st.dataframe(pivot, use_container_width=True)


def _system_health_page():
    st.title("System Health")

    m = _mock_metrics()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Uptime", f"{m['uptime_pct']:.1f}%")
    col2.metric("Cache Hit Rate", f"{m['cache_hit_rate']:.0%}")
    col3.metric("Model Requests", f"{m['model_requests']:,}")
    col4.metric("Avg Latency", f"{m['avg_latency_ms']:.0f}ms")

    st.markdown("### API Health Status")

    endpoints = [
        ("GET /health", 200, "OK", "12ms"),
        ("GET /metrics", 200, "OK", "45ms"),
        ("GET /claim/{id}", 200, "OK", "120ms"),
        ("POST /evaluate", 200, "OK", "1800ms"),
        ("POST /analyze", 200, "OK", "2300ms"),
    ]
    health_df = pd.DataFrame(endpoints, columns=["Endpoint", "Status Code", "Status", "Latency"])
    st.dataframe(health_df, use_container_width=True, hide_index=True)

    st.markdown("### Module Latencies")
    modules = {
        "Image Preprocessor": (120, 350),
        "CV Analysis": (200, 800),
        "VLM Inference": (800, 5000),
        "Rule Engine": (5, 50),
        "Fraud Detection": (100, 600),
        "Consensus": (10, 100),
        "Reporting": (20, 150),
    }
    mod_data = []
    for name, (mn, mx) in modules.items():
        mod_data.append({"Module": name, "Min (ms)": mn, "Max (ms)": mx, "Avg (ms)": (mn + mx) // 2})
    mod_df = pd.DataFrame(mod_data)
    fig = px.bar(mod_df, x="Module", y="Avg (ms)", title="Average Latency by Module", color="Module")
    st.plotly_chart(fig, use_container_width=True)


_PAGE_FUNCS = {
    "Overview": _overview_page,
    "Claim History": _claim_history_page,
    "Fraud Analysis": _fraud_analysis_page,
    "Risk Trends": _risk_trends_page,
    "System Health": _system_health_page,
}


def main():
    st.sidebar.title("VerifyIQ Dashboard")
    st.sidebar.markdown("---")
    selected = st.sidebar.radio("Navigation", _NAV_PAGES, index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**v0.1.0-dev**")

    page_func = _PAGE_FUNCS.get(selected)
    if page_func:
        page_func()


if __name__ == "__main__":
    main()
