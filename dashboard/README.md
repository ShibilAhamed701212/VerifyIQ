# VerifyIQ Dashboard

Streamlit-based admin dashboard for the VerifyIQ claim verification platform.

## Quick Start

```bash
# Install dashboard dependencies
pip install "verifyiq[dashboard]"

# Run the dashboard
streamlit run dashboard/app.py

# Or use the entry point
python -m dashboard.run
```

## Features

- **Overview**: Key metrics, claim status distribution, severity breakdown
- **Claim History**: Filterable table of all claims
- **Fraud Analysis**: Fraud flag distribution, fraud score histograms
- **Risk Trends**: Time-series fraud scores, severity vs risk level
- **System Health**: API endpoint status, module latency breakdown

## Pages

| Page | Description |
|------|-------------|
| Overview | High-level KPIs and quick charts |
| Claim History | Searchable/filterable claims table |
| Fraud Analysis | Fraud detection patterns |
| Risk Trends | Temporal analysis of risk scores |
| System Health | API health & performance metrics |
