import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="China A-Share Sector Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

COLUMN_MAP = {
    "日期": "date", "开盘": "open", "收盘": "close",
    "最高": "high", "最低": "low", "成交量": "volume",
    "成交额": "amount", "振幅": "amplitude", "涨跌幅": "pct_change",
    "涨跌额": "change", "换手率": "turnover",
}

@st.cache_data
def load_sector_data():
    path = os.path.join(DATA_DIR, "sector_indices.csv")
    if not os.path.exists(path):
        st.error("Data file not found: data/sector_indices.csv. Please run fetch_data.py first.")
        st.stop()
    df = pd.read_csv(path)
    df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns}, inplace=True)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    df.sort_values(["sector", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["daily_return"] = df.groupby("sector")["close"].pct_change() * 100
    first_rows = df.groupby("sector").head(1).index
    df.loc[first_rows, "daily_return"] = 0
    df["ma20"] = df.groupby("sector")["close"].transform(
        lambda x: x.rolling(window=20, min_periods=10).mean()
    )
    df["volatility_20d"] = df.groupby("sector")["daily_return"].transform(
        lambda x: x.rolling(window=20, min_periods=10).std()
    )
    df["cum_return"] = df.groupby("sector")["daily_return"].transform(
        lambda x: (1 + x / 100).cumprod() - 1
    ) * 100
    return df

@st.cache_data
def load_market_data():
    path = os.path.join(DATA_DIR, "market_indices.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns}, inplace=True)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    df.sort_values(["index_name", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["daily_return"] = df.groupby("index_name")["close"].pct_change() * 100
    first_rows = df.groupby("index_name").head(1).index
    df.loc[first_rows, "daily_return"] = 0
    df["ma20"] = df.groupby("index_name")["close"].transform(
        lambda x: x.rolling(window=20, min_periods=10).mean()
    )
    return df

sector_df = load_sector_data()
market_df = load_market_data()

sectors = sorted(sector_df["sector"].unique())
dates = sector_df["date"]

st.sidebar.markdown("## 📈 China A-Share Sector Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Overview", "📈 Sector Trends", "⚖️ Risk-Return", "🔗 Correlation", "📉 Market Indices", "📋 Data Explorer"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")
selected_sectors = st.sidebar.multiselect("Select Sectors", sectors, default=sectors[:5])

date_min = sector_df["date"].min().to_pydatetime()
date_max = sector_df["date"].max().to_pydatetime()
date_range = st.sidebar.slider(
    "Date Range",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
    format="YYYY-MM-DD",
)

filtered = sector_df[
    (sector_df["sector"].isin(selected_sectors))
    & (sector_df["date"] >= date_range[0])
    & (sector_df["date"] <= date_range[1])
]

if page == "📊 Overview":
    st.title("📊 China A-Share Sector Performance Overview")
    st.markdown(
        "Explore and compare sector-level performance in China's A-share market. "
        "This interactive tool helps investors, analysts, and students assess sector dynamics "
        "for portfolio allocation and market understanding."
    )
    st.markdown("---")

    latest_date = filtered["date"].max()
    latest = filtered[filtered["date"] == latest_date]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sectors Selected", len(selected_sectors))
    with col2:
        if not latest.empty:
            best = latest.loc[latest["daily_return"].idxmax()]
            st.metric("Best Sector Today", best["sector"], f"{best['daily_return']:.2f}%")
    with col3:
        if not latest.empty:
            worst = latest.loc[latest["daily_return"].idxmin()]
            st.metric("Worst Sector Today", worst["sector"], f"{worst['daily_return']:.2f}%")
    with col4:
        if not latest.empty:
            avg_ret = latest["daily_return"].mean()
            st.metric("Avg Sector Return", f"{avg_ret:.2f}%")

    st.markdown("---")
    st.subheader("Sector Performance Summary")

    summary = filtered.groupby("sector").agg(
        avg_daily_return=("daily_return", "mean"),
        avg_volatility=("volatility_20d", "mean"),
        total_cum_return=("cum_return", "last"),
        last_close=("close", "last"),
    ).round(4)
    summary["risk_return_ratio"] = (summary["avg_daily_return"] / summary["avg_volatility"]).round(4)
    summary = summary.sort_values("total_cum_return", ascending=False)
    summary.columns = ["Avg Daily Ret (%)", "Avg Volatility (%)", "Cum Return (%)", "Last Close", "Risk-Return Ratio"]
    st.dataframe(summary, use_container_width=True)

    st.markdown("---")
    st.subheader("Cumulative Returns Comparison")
    fig = px.line(
        filtered, x="date", y="cum_return", color="sector",
        title="Sector Cumulative Returns",
        labels={"date": "Date", "cum_return": "Cumulative Return (%)", "sector": "Sector"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Sector Trends":
    st.title("📈 Sector Trend Analysis")
    st.markdown("Explore individual sector price trends, returns, and technical indicators.")

    selected = st.selectbox("Select Sector", sectors)
    sdata = sector_df[sector_df["sector"] == selected].copy()

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Price & MA20", "Daily Return", "20-Day Volatility"),
        row_heights=[0.5, 0.25, 0.25],
    )
    fig.add_trace(go.Scatter(x=sdata["date"], y=sdata["close"], name="Close", line=dict(color="blue")), row=1, col=1)
    fig.add_trace(go.Scatter(x=sdata["date"], y=sdata["ma20"], name="MA20", line=dict(color="orange", dash="dash")), row=1, col=1)
    fig.add_trace(go.Bar(x=sdata["date"], y=sdata["daily_return"], name="Daily Return", marker_color="gray", opacity=0.6), row=2, col=1)
    fig.add_trace(go.Scatter(x=sdata["date"], y=sdata["volatility_20d"], name="Volatility 20D", line=dict(color="red")), row=3, col=1)
    fig.update_layout(height=800, title=f"{selected} Sector — Price, Return & Volatility")
    fig.update_xaxes(title_text="Date", row=3, col=1)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Descriptive Statistics")
    stats = sdata[["close", "daily_return", "volume"]].describe().round(4)
    stats.columns = ["Close Price", "Daily Return (%)", "Volume"]
    st.dataframe(stats, use_container_width=True)

elif page == "⚖️ Risk-Return":
    st.title("⚖️ Risk-Return Analysis")
    st.markdown("Compare sectors on risk-adjusted return metrics.")

    summary = filtered.groupby("sector").agg(
        avg_daily_return=("daily_return", "mean"),
        avg_volatility=("volatility_20d", "mean"),
        total_cum_return=("cum_return", "last"),
    ).round(4).reset_index()

    fig = px.scatter(
        summary, x="avg_volatility", y="avg_daily_return",
        color="total_cum_return", color_continuous_scale="RdYlGn",
        size="total_cum_return", size_max=30,
        hover_name="sector",
        title="Risk-Return Profile by Sector",
        labels={"avg_volatility": "Avg 20-Day Volatility (%)", "avg_daily_return": "Avg Daily Return (%)", "total_cum_return": "Cum Return (%)"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Volatility Distribution (Box Plot)")
    vol_data = filtered.dropna(subset=["daily_return"])
    fig_box = px.box(
        vol_data, x="sector", y="daily_return",
        title="Daily Return Distribution by Sector",
        labels={"sector": "Sector", "daily_return": "Daily Return (%)"},
    )
    st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Risk-Return Ranking")
    summary["risk_return_ratio"] = (summary["avg_daily_return"] / summary["avg_volatility"]).round(4)
    summary_sorted = summary.sort_values("risk_return_ratio", ascending=False)
    fig_bar = px.bar(
        summary_sorted, x="sector", y="risk_return_ratio",
        title="Risk-Return Ratio (Higher = Better Risk-Adjusted Return)",
        labels={"sector": "Sector", "risk_return_ratio": "Risk-Return Ratio"},
        color="risk_return_ratio", color_continuous_scale="RdYlGn",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

elif page == "🔗 Correlation":
    st.title("🔗 Sector Correlation Analysis")
    st.markdown("Explore return correlations between sectors for diversification insights.")

    pivot = filtered.pivot_table(index="date", columns="sector", values="daily_return")
    corr = pivot.corr().round(3)

    fig = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1, aspect="auto",
        title="Sector Return Correlation Matrix",
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Scatter: Compare Two Sectors")
    col1, col2 = st.columns(2)
    with col1:
        x_sector = st.selectbox("X-Axis Sector", sectors, index=0)
    with col2:
        y_sector = st.selectbox("Y-Axis Sector", sectors, index=1 if len(sectors) > 1 else 0)

    if x_sector != y_sector:
        x_data = sector_df[sector_df["sector"] == x_sector][["date", "daily_return"]].rename(columns={"daily_return": "x_ret"})
        y_data = sector_df[sector_df["sector"] == y_sector][["date", "daily_return"]].rename(columns={"daily_return": "y_ret"})
        merged = pd.merge(x_data, y_data, on="date").dropna()
        if not merged.empty:
            fig_scatter = px.scatter(
                merged, x="x_ret", y="y_ret",
                title=f"{x_sector} vs {y_sector} Daily Returns",
                labels={"x_ret": f"{x_sector} Return (%)", "y_ret": f"{y_sector} Return (%)"},
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            corr_val = merged["x_ret"].corr(merged["y_ret"])
            st.info(f"Correlation coefficient: **{corr_val:.3f}**")

    st.subheader("Key Correlation Insights")
    if not corr.empty:
        insights = []
        cols = corr.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = corr.iloc[i, j]
                if abs(val) > 0.6:
                    direction = "positive" if val > 0 else "negative"
                    strength = "Strong" if abs(val) > 0.8 else "Moderate"
                    insights.append(f"- **{cols[i]}** & **{cols[j]}**: {strength} {direction} (r={val:.2f})")
        if insights:
            for ins in insights:
                st.markdown(ins)
        else:
            st.info("No strong correlations (|r| > 0.6) found among selected sectors.")

elif page == "📉 Market Indices":
    st.title("📉 Major Market Indices")
    st.markdown("Track major A-share market benchmarks alongside sector performance.")

    if market_df.empty:
        st.warning("Market index data not available. Run fetch_data.py to download.")
    else:
        index_names = market_df["index_name"].unique().tolist()
        selected_indices = st.multiselect("Select Indices", index_names, default=index_names[:3])

        m_filtered = market_df[market_df["index_name"].isin(selected_indices)]

        fig = px.line(
            m_filtered, x="date", y="close", color="index_name",
            title="Market Index Trends",
            labels={"date": "Date", "close": "Index Level", "index_name": "Index"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Index Summary")
        m_summary = m_filtered.groupby("index_name").agg(
            avg_daily_return=("daily_return", "mean"),
            max_close=("close", "max"),
            min_close=("close", "min"),
            last_close=("close", "last"),
        ).round(4)
        m_summary.columns = ["Avg Daily Ret (%)", "Max", "Min", "Latest"]
        st.dataframe(m_summary, use_container_width=True)

        st.subheader("Sector vs Market Benchmark")
        benchmark = st.selectbox("Select Benchmark", index_names, index=0)
        bench_data = market_df[market_df["index_name"] == benchmark][["date", "close"]].rename(columns={"close": "benchmark_close"})
        bench_data["bench_cum"] = (bench_data["benchmark_close"] / bench_data["benchmark_close"].iloc[0] - 1) * 100

        sector_cum = filtered.groupby(["date"])["cum_return"].mean().reset_index()
        sector_cum.columns = ["date", "sector_avg_cum"]

        compare = pd.merge(bench_data[["date", "bench_cum"]], sector_cum, on="date", how="inner").dropna()
        if not compare.empty:
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(x=compare["date"], y=compare["bench_cum"], name=benchmark))
            fig_comp.add_trace(go.Scatter(x=compare["date"], y=compare["sector_avg_cum"], name="Avg Sector"))
            fig_comp.update_layout(title=f"Sector Average vs {benchmark}", yaxis_title="Cumulative Return (%)")
            fig_comp.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
            st.plotly_chart(fig_comp, use_container_width=True)

elif page == "📋 Data Explorer":
    st.title("📋 Data Explorer")
    st.markdown("Browse and download the raw sector data.")

    display_cols = ["sector", "date", "open", "close", "high", "low", "volume", "daily_return", "cum_return"]
    available = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[available].sort_values(["sector", "date"]), use_container_width=True, hide_index=True)

    st.markdown("---")
    csv = filtered[available].to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="sector_data.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small>Data Source: Simulated based on AKShare / East Money structure<br>"
    "Generation Date: April 2026<br>"
    "Built with Streamlit & Plotly</small>",
    unsafe_allow_html=True,
)
