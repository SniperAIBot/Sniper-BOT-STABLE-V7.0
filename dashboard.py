import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    get_all_signals,
    get_symbol_performance,
    get_recent_signals
)

from performance import (
    get_statistics,
    get_win_rate,
    get_expectancy
)


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="SNIPER PRO DASHBOARD",
    layout="wide"
)


# ================= TITLE =================
st.title(
    "🚀 SNIPER PRO DASHBOARD V 7.0"
)

st.caption(
    "Advanced Trading Analytics System"
)


# ================= LOAD DATA =================
signals_df = get_all_signals()

stats = get_statistics()

symbol_df = get_symbol_performance()

recent_df = get_recent_signals()

win_rate = get_win_rate()

expectancy = get_expectancy()


# ================= METRICS =================
st.subheader("📈 System Performance")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Trades",
    stats["total_trades"]
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
    f"{win_rate}%"
)

col5.metric(
    "Expectancy",
    expectancy
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
        hover_data=[
            "wins",
            "losses"
        ],
        title="Win Rate By Symbol"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.warning(
        "No symbol analytics available."
    )


st.divider()


# ================= MARKET REGIME =================
st.subheader("🔥 Market Regime Distribution")

if not signals_df.empty:

    regime_df = (
        signals_df.groupby(
            "market_regime"
        )
        .size()
        .reset_index(name="count")
    )

    regime_chart = px.pie(
        regime_df,
        names="market_regime",
        values="count",
        title="Market Regime Distribution"
    )

    st.plotly_chart(
        regime_chart,
        use_container_width=True
    )

else:

    st.warning(
        "No market regime data."
    )


st.divider()


# ================= WIN / LOSS =================
st.subheader("⚔️ Win vs Loss")

if not signals_df.empty:

    results_df = (
        signals_df.groupby(
            "result"
        )
        .size()
        .reset_index(name="count")
    )

    results_chart = px.pie(
        results_df,
        names="result",
        values="count",
        title="Win / Loss Distribution"
    )

    st.plotly_chart(
        results_chart,
        use_container_width=True
    )


st.divider()


# ================= STRATEGY PERFORMANCE =================
st.subheader("🧠 Strategy Versions")

if (
    not signals_df.empty
    and "strategy_version" in signals_df.columns
):

    strategy_df = (
        signals_df.groupby(
            "strategy_version"
        )
        .size()
        .reset_index(name="count")
    )

    strategy_chart = px.bar(
        strategy_df,
        x="strategy_version",
        y="count",
        title="Trades Per Strategy Version"
    )

    st.plotly_chart(
        strategy_chart,
        use_container_width=True
    )


st.divider()


# ================= FULL TRADE HISTORY =================
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
