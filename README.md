# Enterprise-Grade Level Retail Sales Data Analysis

An end-to-end production-level retail analytics platform built from the Superstore Sales Dataset. Features a modular Python pipeline with Pandera schema validation, advanced analytics (RFM segmentation, association rule mining, anomaly detection), an interactive Streamlit dashboard with Plotly visualizations, and full DevOps deployment infrastructure (Docker, GitHub Actions CI/CD, Terraform/AWS).

---

## Architecture

```
Retail Sales Data Analysis/
│
├── data/
│   ├── 01_raw/                    # Immutable source data (superstore.csv)
│   └── 02_processed/              # Cleaned/serialized outputs
│
├── notebooks/
│   └── analysis.ipynb             # Interactive EDA notebook
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Ingestion + Pandera validation + cleaning
│   ├── feature_engine.py          # Temporal features, RFM, association rules, anomaly detection
│   └── analysis.py                # Core analytical aggregations
│
├── dashboard/
│   ├── app.py                     # Streamlit application entry point
│   └── components.py              # Reusable Plotly chart & UI widgets
│
├── visuals/                       # Exported static chart assets
├── tests/                         # Pytest test suite
│
├── .streamlit/config.toml         # Streamlit theme configuration
├── .github/workflows/ci-cd.yml   # GitHub Actions pipeline
├── terraform/                     # AWS ECS Fargate infrastructure (IaC)
├── Dockerfile                     # Container build instructions
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard Locally

```bash
streamlit run dashboard/app.py
```

The dashboard will open at **http://localhost:8501**.

### 3. Run Tests

```bash
pytest tests/ -v
```

---

## Docker Deployment

### Build the Image

```bash
docker build -t retail-sales-dashboard .
```

### Run the Container

```bash
docker run -p 8501:8501 retail-sales-dashboard
```

Access at **http://localhost:8501**.

---

## AWS Deployment (Terraform)

The `terraform/` directory contains Infrastructure as Code for deploying to AWS ECS Fargate behind an Application Load Balancer.

```bash
cd terraform
terraform init
terraform plan -var="container_image=<YOUR_ECR_IMAGE_URI>"
terraform apply -var="container_image=<YOUR_ECR_IMAGE_URI>"
```

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automates:

1. **Test** — Runs Pytest on every push/PR
2. **Build & Push** — Builds Docker image and pushes to Amazon ECR (on `main` branch)
3. **Deploy** — Triggers ECS rolling deployment (on `main` branch)

Configure `AWS_ROLE_ARN` in GitHub repository secrets.

---

## Dataset

**Superstore Sales Dataset** — 9,994 retail transactions across 21 dimensions:

| Dimension | Columns |
|-----------|---------|
| Chronological | Order Date, Ship Date, Ship Mode |
| Geographic | Country, City, State, Postal Code, Region |
| Categorical | Category, Sub-Category, Product Name, Segment |
| Financial | Sales, Quantity, Discount, Profit |

Date range: **January 2014 – December 2017** · All United States transactions.

---

## Dashboard Features

### Executive KPIs
- Total Sales, Total Profit, Profit Margin %, Order Count
- Dynamic filtering by Region, Category, Segment, and Year

### Core Visualizations
- **Monthly Revenue Trend** — Time-series line chart with Sales & Profit overlay
- **Category Performance** — Bar chart comparing Furniture, Office Supplies, Technology
- **Top 10 Sub-Categories** — Horizontal bar chart of revenue drivers
- **Regional Performance** — Bar chart of sales by geographic territory
- **Profit vs Sales Scatter** — Interactive scatter with zero-profit baseline and Category hue
- **Discount Impact** — Average profit by discount bracket
- **Profit Margin by Category** — Comparative margin analysis

### Advanced Analytics
- **RFM Customer Segmentation** — Recency/Frequency/Monetary analysis with quintile scoring and segment labeling (Champions, Loyal, At-Risk, etc.)
- **Association Rule Mining** — FP-Growth algorithm on Sub-Category co-purchases revealing cross-sell opportunities
- **Anomaly Detection** — Isolation Forest model flagging suspicious transactions

---

## Key Business Insights

1. **Technology Dominance** — Technology generates the highest aggregate revenue, serving as the primary revenue engine
2. **West Region Superiority** — The West outpaces all other territories in gross revenue
3. **December Peak** — Massive seasonal spike in Q4/December driven by holiday purchasing
4. **High Sales / Negative Profit Anomaly** — Significant transactions with high revenue but negative margins indicate catastrophic discounting that erodes operational profitability

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Processing | Pandas, NumPy, Pandera |
| Feature Engineering | scikit-learn, mlxtend |
| Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Testing | Pytest |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Infrastructure | Terraform, AWS ECS Fargate, ALB |
