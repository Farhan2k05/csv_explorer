# app.py
import streamlit as st
import pandas as pd
import numpy as np
import io, csv
import plotly.express as px

st.set_page_config(page_title="CSV Dashboard", layout="wide")
st.title("CSV Dashboard")
st.write("Upload a CSV and explore the data")

# try to read csv even if encoding or delimiter is weird
def read_csv_smart(uploaded_file):
    raw = uploaded_file.getvalue()

    enc_used, text = None, None
    for enc in ["utf-8", "utf-16", "latin-1"]:
        try:
            text = raw.decode(enc)
            enc_used = enc
            break
        except:
            pass
    if text is None:
        text = raw.decode("utf-8", errors="replace")
        enc_used = "utf-8 (replace)"

    try:
        dialect = csv.Sniffer().sniff(text[:20000])
        delim = dialect.delimiter
    except:
        delim = ","

    buf = io.StringIO(text)
    try:
        df = pd.read_csv(buf, sep=delim, engine="c", low_memory=False)
    except:
        buf.seek(0)
        df = pd.read_csv(buf, sep=delim, engine="python")

    return df, enc_used, delim

# quick dataset summary
def profile(df):
    n_rows, n_cols = df.shape
    mem = df.memory_usage(deep=True).sum() / (1024**2)
    dupes = df.duplicated().sum()
    missing = df.isna().mean().mul(100).round(2)
    return n_rows, n_cols, mem, dupes, missing

# helpers to pick column types
def num_cols(df): return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
def dt_cols(df): return [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
def cat_cols(df): return [c for c in df.columns if df[c].dtype == "object"]

# upload
file = st.file_uploader("Upload CSV", type=["csv"])
if not file:
    st.stop()

df, enc, delim = read_csv_smart(file)
st.success(f"Loaded {file.name}")

rows, cols, mem, dupes, miss = profile(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{rows:,}")
c2.metric("Columns", f"{cols}")
c3.metric("Memory MB", f"{mem:.2f}")
c4.metric("Duplicates", f"{dupes}")

st.write("### Missing values (%)")
st.dataframe(miss.sort_values(ascending=False).to_frame("missing_%"))

st.write("### Preview")
st.dataframe(df.head(200))

# charts
tabs = st.tabs(["Numeric", "Categorical", "Time", "Correlation"])

with tabs[0]:
    nums = num_cols(df)
    if not nums:
        st.write("No numeric columns")
    else:
        col = st.selectbox("Choose column", nums)
        st.plotly_chart(px.histogram(df, x=col, nbins=30))
        st.plotly_chart(px.box(df, y=col))

with tabs[1]:
    cats = cat_cols(df)
    if not cats:
        st.write("No categorical columns")
    else:
        col = st.selectbox("Choose column", cats)
        n = st.slider("Top N", 5, 30, 10)
        vc = df[col].value_counts().head(n).reset_index()
        vc.columns = [col, "count"]
        st.plotly_chart(px.bar(vc, x=col, y="count"))

with tabs[2]:
    dts = dt_cols(df)
    if not dts:
        st.write("No datetime columns")
    else:
        col = st.selectbox("Date column", dts)
        y = st.selectbox("Y (optional)", [None] + num_cols(df))
        freq = st.selectbox("Freq", ["D", "W", "M"], 0)
        tmp = df.set_index(col).sort_index()
        if y:
            agg = tmp[y].resample(freq).mean().reset_index()
            st.plotly_chart(px.line(agg, x=col, y=y))
        else:
            agg = tmp.resample(freq).size().reset_index(name="count")
            st.plotly_chart(px.line(agg, x=col, y="count"))

with tabs[3]:
    nums = num_cols(df)
    if len(nums) < 2:
        st.write("Need 2+ numeric cols")
    else:
        corr = df[nums].corr()
        st.plotly_chart(px.imshow(corr, text_auto=True))

# cleaning
st.write("### Cleaning")
with st.form("cleaning"):
    drop_dupes = st.checkbox("Drop duplicates", True)
    fill_nums = st.checkbox("Fill missing numerics with mean", False)
    go = st.form_submit_button("Apply")

cleaned = df.copy()
if go:
    if drop_dupes:
        cleaned = cleaned.drop_duplicates()
        st.write("Duplicates removed")
    if fill_nums:
        for col in num_cols(cleaned):
            cleaned[col] = cleaned[col].fillna(cleaned[col].mean())
        st.write("Filled numeric NaNs")

st.download_button("Download cleaned CSV", cleaned.to_csv(index=False).encode("utf-8"),
                   file_name="cleaned.csv", mime="text/csv")
