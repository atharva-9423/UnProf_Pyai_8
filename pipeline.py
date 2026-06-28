import json
import logging
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for scripts/servers
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                 Table, TableStyle)


API_URL = "https://api.coingecko.com/api/v3/coins/markets"
API_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 20,
    "page": 1,
    "price_change_percentage": "24h",
}

OUTPUT_DIR = "output"
CSV_PATH = os.path.join(OUTPUT_DIR, "crypto_data.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "crypto_data.json")
PDF_PATH = os.path.join(OUTPUT_DIR, "crypto_report.pdf")
BAR_CHART_PATH = os.path.join(OUTPUT_DIR, "bar_chart.png")
LINE_CHART_PATH = os.path.join(OUTPUT_DIR, "line_chart.png")
PIE_CHART_PATH = os.path.join(OUTPUT_DIR, "pie_chart.png")
LOG_PATH = os.path.join(OUTPUT_DIR, "pipeline.log")

os.makedirs(OUTPUT_DIR, exist_ok=True)


logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class PipelineError(Exception):
    pass



def fetch_data():
    print("🌐 Fetching live data from CoinGecko...")
    try:
        response = requests.get(API_URL, params=API_PARAMS, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise PipelineError("API returned an empty dataset.")
        logging.info(f"Fetched {len(data)} records from CoinGecko.")
        print(f"✅ Fetched {len(data)} coins.")
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        print(f"❌ Could not reach CoinGecko API: {e}")
        raise PipelineError("Data fetch failed.") from e


def clean_data(raw_data):
    print("🧹 Cleaning data...")

    df = pd.DataFrame(raw_data)

    columns_needed = [
        "id", "symbol", "name", "current_price", "market_cap",
        "total_volume", "price_change_percentage_24h", "high_24h", "low_24h",
    ]
    df = df[[c for c in columns_needed if c in df.columns]].copy()

    df.rename(columns={
        "current_price": "price_usd",
        "price_change_percentage_24h": "change_24h_pct",
    }, inplace=True)

    before = len(df)
    df.dropna(subset=["price_usd"], inplace=True)
    dropped = before - len(df)
    if dropped:
        logging.warning(f"Dropped {dropped} rows with missing price data.")

    numeric_cols = ["market_cap", "total_volume", "change_24h_pct", "high_24h", "low_24h"]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    df["symbol"] = df["symbol"].str.upper()
    df.sort_values("market_cap", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    logging.info(f"Cleaned dataset shape: {df.shape}")
    print(f"✅ Cleaned dataset: {len(df)} rows, {len(df.columns)} columns.")
    return df


def analyze_data(df):
    print("📊 Analyzing data...")

    prices = df["price_usd"].to_numpy()
    changes = df["change_24h_pct"].to_numpy()

    summary = {
        "total_coins": int(len(df)),
        "avg_price_usd": float(np.mean(prices)),
        "median_price_usd": float(np.median(prices)),
        "avg_change_24h_pct": float(np.mean(changes)),
        "best_performer": df.loc[df["change_24h_pct"].idxmax(), "name"],
        "best_performer_pct": float(df["change_24h_pct"].max()),
        "worst_performer": df.loc[df["change_24h_pct"].idxmin(), "name"],
        "worst_performer_pct": float(df["change_24h_pct"].min()),
        "total_market_cap": float(df["market_cap"].sum()),
    }

    logging.info(f"Analysis summary: {summary}")
    print("✅ Analysis complete.")
    return summary


def visualize_data(df):
    print("🎨 Generating charts...")
    top10 = df.head(10)

    # Bar chart — market cap of top 10 coins
    plt.figure(figsize=(8, 5))
    plt.bar(top10["symbol"], top10["market_cap"] / 1e9, color="#3b82f6")
    plt.title("Top 10 Coins by Market Cap")
    plt.ylabel("Market Cap (Billion USD)")
    plt.xlabel("Coin")
    plt.tight_layout()
    plt.savefig(BAR_CHART_PATH, dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(top10["symbol"], top10["change_24h_pct"], marker="o", color="#f97316")
    plt.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    plt.title("24h Price Change (%) - Top 10 Coins")
    plt.ylabel("Change (%)")
    plt.xlabel("Coin")
    plt.tight_layout()
    plt.savefig(LINE_CHART_PATH, dpi=150)
    plt.close()

    top5 = df.head(5).copy()
    other_cap = df["market_cap"].sum() - top5["market_cap"].sum()
    labels = list(top5["symbol"]) + ["Other"]
    sizes = list(top5["market_cap"]) + [other_cap]

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Market Cap Share (Top 5 vs Rest)")
    plt.tight_layout()
    plt.savefig(PIE_CHART_PATH, dpi=150)
    plt.close()

    logging.info("Charts generated: bar, line, pie.")
    print("✅ Charts saved to output/")



def save_data(df):
    print("💾 Saving processed data...")
    try:
        df.to_csv(CSV_PATH, index=False)
        df.to_json(JSON_PATH, orient="records", indent=2)
        logging.info(f"Data saved to {CSV_PATH} and {JSON_PATH}.")
        print(f"✅ Saved to {CSV_PATH} and {JSON_PATH}")
    except OSError as e:
        logging.error(f"Failed to save data files: {e}")
        print(f"❌ Could not save data files: {e}")
        raise PipelineError("Data save failed.") from e


def generate_pdf_report(df, summary):
    print("📄 Generating PDF report...")

    doc = SimpleDocTemplate(PDF_PATH, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Cryptocurrency Market Report", styles["Title"]))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"],
    ))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Summary", styles["Heading2"]))
    summary_lines = [
        f"Total coins analyzed: {summary['total_coins']}",
        f"Average price: ${summary['avg_price_usd']:,.2f}",
        f"Median price: ${summary['median_price_usd']:,.2f}",
        f"Average 24h change: {summary['avg_change_24h_pct']:.2f}%",
        f"Best performer (24h): {summary['best_performer']} "
        f"({summary['best_performer_pct']:+.2f}%)",
        f"Worst performer (24h): {summary['worst_performer']} "
        f"({summary['worst_performer_pct']:+.2f}%)",
        f"Combined market cap (top {summary['total_coins']}): "
        f"${summary['total_market_cap']:,.0f}",
    ]
    for line in summary_lines:
        story.append(Paragraph(line, styles["Normal"]))
    story.append(Spacer(1, 16))


    story.append(Paragraph("Top 10 Coins by Market Cap", styles["Heading2"]))
    table_data = [["Symbol", "Name", "Price (USD)", "24h Change (%)"]]
    for _, row in df.head(10).iterrows():
        table_data.append([
            row["symbol"],
            row["name"],
            f"${row['price_usd']:,.2f}",
            f"{row['change_24h_pct']:+.2f}%",
        ])

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Visualizations", styles["Heading2"]))
    for path in (BAR_CHART_PATH, LINE_CHART_PATH, PIE_CHART_PATH):
        story.append(Image(path, width=420, height=260))
        story.append(Spacer(1, 12))

    doc.build(story)
    logging.info(f"PDF report generated: {PDF_PATH}")
    print(f"✅ PDF report saved to {PDF_PATH}")



def run_pipeline():
    print("🚀 Starting Crypto Market Data Pipeline\n" + "=" * 40)
    logging.info("===== Pipeline started =====")

    try:
        raw_data = fetch_data()
        df = clean_data(raw_data)
        summary = analyze_data(df)
        visualize_data(df)
        save_data(df)
        generate_pdf_report(df, summary)

        print("\n" + "=" * 40)
        print("🎉 Pipeline completed successfully!")
        logging.info("===== Pipeline completed successfully =====")

    except PipelineError as e:
        print(f"\n❌ Pipeline stopped: {e}")
        logging.error(f"Pipeline stopped: {e}")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    run_pipeline()
