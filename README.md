# 📈 Stock Price Analytics Pipeline

An end-to-end data pipeline using **Airflow**, **Snowflake**, **dbt**, and **Superset** to analyze historical stock prices (e.g., AAPL, NVDA).

---

## 🔧 Tools Used
- **Airflow** – Orchestrates ETL & dbt runs
- **Snowflake** – Stores raw and transformed data
- **dbt** – Transforms, tests, and snapshots data
- **Superset** – Visualizes key metrics (MA14, MA50, RSI)

---

## ⚙️ Pipeline Flow

1. `Airflow DAG` fetches stock data from Yahoo Finance.
2. Data is stored in `Snowflake (raw.stock_data)`.
3. `dbt` transforms it into `analytics.stock_metrics`.
4. `Superset` displays dashboards with filters & charts.

---

## 🧪 dbt Highlights
- `raw_stock_data.sql` – Raw data model
- `stock_metrics.sql` – Adds moving averages
- Tests for nulls
- Snapshot of daily close

---

## 📸 Dashboards
Includes:
- Closing price trend
- MA14 vs MA50
- Symbol/date filters


