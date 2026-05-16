import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    get_all_signals,
    get_statistics,
    get_symbol_performance,
    get_recent_signals
)


# ================= PAGE =================
st.set_page_config(
    page_title="SNIPER PRO DASHBOARD",
    layout="wide"
)


st.title("🚀 SNIPER PRO DASHBOARD")


# ================= LOAD DATA =================
signals_df = get_all_signals()

stats = get_statistics()

symbol_df = get_symbol_performance()

recent_df = get_recent_signals()


# ================= METRICS =================
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Trades",
    stats["total"]
)

col2.metric(
    "Wins",
    stats["wins"]
)

col3.metric(
    "Losses",
    stats["losses"]
)

col4.metric(
    "Win Rate",
    f"{stats['winrate']}%"
)


st.divider()


# ================= RECENT SIGNALS =================
st.subheader("📊 Recent Signals")

st.dataframe(
    recent_df,
    use_container_width=True
)


st.divider()


# ================= SYMBOL PERFORMANCE =================
st.subheader("🏆 Symbol Performance")

if not symbol_df.empty:

    fig = px.bar(
        symbol_df,
        x="symbol",
        y="wins",
        title="Wins By Symbol"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()


# ================= MARKET REGIME =================
st.subheader("🔥 Market Regime")

if not signals_df.empty:

    regime_chart = px.pie(
        signals_df,
        names="market_regime",
        title="Market Regime Distribution"
    )

    st.plotly_chart(
        regime_chart,
        use_container_width=True
    )


st.divider()


# ================= ALL SIGNALS =================
st.subheader("🗂 Full Trade History")

st.dataframe(
    signals_df,
    use_container_width=True
)
