import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    get_all_signals,
    get_recent_signals,
    get_symbol_performance
)

from performance import (
    get_statistics,
    get_win_rate
)


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="SNIPER PRO DASHBOARD",
    layout="wide"
)


# ================= TITLE =================
st.title("🚀 SNIPER PRO DASHBOARD")


# ================= LOAD DATA =================
signals_df = get_all_signals()

recent_df = get_recent_signals()

symbol_df = get_symbol_performance()

stats = get_statistics()


# ================= SAFE DEFAULTS =================
total_trades = stats.get("total", 0)

wins = stats.get("wins", 0)

losses = stats.get("losses", 0)

breakeven = stats.get("breakeven", 0)

timeout = stats.get("timeout", 0)

win_rate = stats.get("win_rate", 0)

expectancy = stats.get("expectancy", 0)

avg_rr = stats.get("avg_rr_win", 0)


# ================= TOP METRICS =================
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Trades",
    total_trades
)

col2.metric(
    "Wins",
    wins
)

col3.metric(
    "Losses",
    losses
)

col4.metric(
    "Win Rate",
    f"{win_rate}%"
)


# ================= SECOND ROW =================
col5, col6, col7 = st.columns(3)

col5.metric(
    "Breakeven",
    breakeven
)

col6.metric(
    "Expectancy",
    expectancy
)

col7.metric(
    "Average RR",
    avg_rr
)


st.divider()


# ================= RECENT SIGNALS =================
st.subheader("📊 Recent Signals")

if not recent_df.empty:

    st.dataframe(
        recent_df,
        use_container_width=True
    )

else:

    st.warning(
        "No recent signals found."
    )


st.divider()


# ================= SYMBOL PERFORMANCE =================
st.subheader("🏆 Symbol Performance")

if not symbol_df.empty:

    symbol_df["winrate"] = (
        symbol_df["wins"] /
        (
            symbol_df["wins"] +
            symbol_df["losses"]
        )
    ) * 100

    fig = px.bar(
        symbol_df,
        x="symbol",
        y="winrate",
        title="Win Rate By Symbol"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.warning(
        "No symbol statistics available."
    )


st.divider()


# ================= MARKET REGIME =================
st.subheader("🔥 Market Regime Distribution")

if (
    not signals_df.empty
    and "market_regime" in signals_df.columns
):

    regime_chart = px.pie(
        signals_df,
        names="market_regime",
        title="Market Regime"
    )

    st.plotly_chart(
        regime_chart,
        use_container_width=True
    )

else:

    st.warning(
        "No market regime data available."
    )


st.divider()


# ================= RESULT DISTRIBUTION =================
st.subheader("📈 Trade Results")

if (
    not signals_df.empty
    and "result" in signals_df.columns
):

    result_chart = px.histogram(
        signals_df,
        x="result",
        title="Trade Result Distribution"
    )

    st.plotly_chart(
        result_chart,
        use_container_width=True
    )


st.divider()


# ================= FULL HISTORY =================
st.subheader("🗂 Full Trade History")

if not signals_df.empty:

    st.dataframe(
        signals_df,
        use_container_width=True
    )

else:

    st.warning(
        "No trade history found."
    )
