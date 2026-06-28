<div align="center">

# 📊 Crypto Market Data Pipeline

**An end-to-end data pipeline: Fetch → Clean → Analyze → Visualize → Save**

`Python 3` · `pandas` · `NumPy` · `Matplotlib` · `ReportLab` · `Phase 1 — Day 8 (Final Project)`

</div>

---

## 📖 Overview

This is the **Phase 1 capstone project**, bringing together everything learned across Days 1–7: OOP principles, file/JSON handling, error handling & logging, API requests, and data analysis & visualization.

The pipeline fetches live market data for the top 20 cryptocurrencies from the **CoinGecko public API**, cleans it, runs statistical analysis, generates charts, exports a polished PDF report, and saves the processed dataset locally — all in one automated run.

---

## ✨ Features

| Stage | What it does |
|---|---|
| 🌐 **Fetch** | Pulls live market data from CoinGecko (no API key required) |
| 🧹 **Clean** | Drops invalid rows, fills missing values, standardizes columns |
| 📊 **Analyze** | Computes averages, medians, best/worst performers using NumPy & pandas |
| 📈 **Visualize** | Generates a bar chart, line chart, and pie chart with Matplotlib |
| 📄 **Report** | Exports a full PDF report with summary stats, a data table, and charts |
| 💾 **Save** | Saves the cleaned dataset as both CSV and JSON |
| 🛡️ **Resilience** | Gracefully handles API failures, missing data, and file errors with logging |

---

## ⚙️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/atharva-9423/UnProf_Pyai_8
cd

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python pipeline.py
```

All outputs are written to the `output/` folder:

```
output/
├── crypto_data.csv        # Cleaned dataset (CSV)
├── crypto_data.json       # Cleaned dataset (JSON)
├── crypto_report.pdf      # Full PDF report
├── bar_chart.png           # Market cap by coin
├── line_chart.png          # 24h price change
├── pie_chart.png           # Market share breakdown
└── pipeline.log             # Execution log
```

---

## 🧩 Pipeline Flow

```
Fetch (CoinGecko API)
   ↓
Clean (pandas — drop nulls, standardize columns)
   ↓
Analyze (NumPy — mean, median, best/worst performer)
   ↓
Visualize (Matplotlib — bar, line, pie charts)
   ↓
Save (CSV + JSON) → Report (PDF)
```

---

## 🛠️ Tech Stack

- **`requests`** — API calls & error handling
- **`pandas`** — DataFrame cleaning, transformation, CSV/JSON export
- **`NumPy`** — statistical computations
- **`Matplotlib`** — bar, line & pie chart generation
- **`reportlab`** — PDF report generation
- **`logging`** — execution tracking & error logs

---

## 🛡️ Error Handling

- API failures (timeouts, bad responses) are caught and logged — the pipeline exits cleanly instead of crashing.
- Rows with missing critical data (e.g. no price) are dropped; other missing numeric fields are filled rather than left as `NaN`.
- A custom `PipelineError` exception marks unrecoverable stage failures, keeping the control flow clean.

---

<div align="center">

🏁 Built as the **Phase 1 – Python Intermediate Capstone**
Fetch → Clean → Analyze → Visualize → Save

</div>