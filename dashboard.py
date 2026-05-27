import streamlit as st
import plotly.express as px

from database import get_all_signals
from performance import get_statistics


st.set_page_config(
    page_title="SNIPER PRO",
    layout="wide"
)

st.title("🚀 SNIPER PRO DASHBOARD")


df = get_all_signals()

stats = get_statistics()


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Trades", stats["total_trades"])
col2.metric("Wins", stats["wins"])
col3.metric("Losses", stats["losses"])
col4.metric("Win Rate", f"{stats['win_rate']}%")
col5.metric("Expectancy", stats["expectancy"])


st.divider()


if not df.empty:

    st.subheader("📊 Trade History")

    st.dataframe(df, use_container_width=True)

    st.subheader("🏆 Performance By Coin")

    symbol_chart = (
        df[df["result"] == "WIN"]
        .groupby("symbol")
        .size()
        .reset_index(name="wins")
    )

    fig = px.bar(
        symbol_chart,
        x="symbol",
        y="wins"
    )

    st.plotly_chart(fig, use_container_width=True)
