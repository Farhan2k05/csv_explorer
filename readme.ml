# CSV Dashboard

A lightweight data exploration tool built with Python and Streamlit. Upload any CSV and instantly get a visual summary of your data — no setup, no SQL, no pandas knowledge required.

## What it does

- **Smart ingestion** — auto-detects file encoding (UTF-8, UTF-16, Latin-1) and delimiter, so messy real-world CSVs load without manual fiddling
- **Dataset overview** — row/column count, memory usage, duplicate count, and a missing-value breakdown at a glance
- **Four chart tabs** — histograms and box plots for numeric columns, bar charts for categoricals, time-series line charts for datetime columns, and a correlation heatmap
- **Basic cleaning** — drop duplicates and/or fill numeric nulls with column means, then download the result

## Stack

Python · Streamlit · pandas · Plotly Express

## Run locally
```bash
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # Mac/Linux
pip install streamlit pandas plotly
python -m streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Sample data

Three test CSVs are included — a clean retail dataset, a messy semicolon-delimited Pokémon file, and a Latin-1 encoded variant — to exercise the parser edge cases.