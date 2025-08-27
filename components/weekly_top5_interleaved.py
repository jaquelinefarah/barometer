# components/weekly_trading.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.periods import _last_closed_week_data  # já existente

def render_weekly_trading(df: pd.DataFrame, top_n: int = 5) -> None:
    st.subheader("🔎 Weekly Trading Activity – Top Buyers and Sellers (Net Volume)")

    if df.empty:
        st.info("No trading data available for this period.")
        return

    # Última semana fechada (pelos dados)
    start, end = _last_closed_week_data(df, "date")
    if start is None:
        st.warning("Dataset vazio ou sem semanas completas.")
        return

    # Normaliza datas
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.to_period("W-FRI").apply(lambda r: r.start_time.normalize())

    # Agregado semanal
    weekly = (
        df.groupby(["week", "broker"], as_index=False)
          .agg(buy_volume=("buy_volume", "sum"),
               sell_volume=("sell_volume", "sum"))
    )
    weekly["net_volume"] = weekly["buy_volume"] - weekly["sell_volume"]

    # Últimas 4 semanas baseadas nos dados
    last_4_weeks = sorted(weekly["week"].unique())[-4:]

    week_figs = []
    for week in last_4_weeks[::-1]:  # mais recente à esquerda
        week_df = weekly[weekly["week"] == week]
        if week_df.empty:
            continue

        buyers = week_df[week_df["net_volume"] > 0].sort_values("net_volume", ascending=False).head(top_n)
        sellers = week_df[week_df["net_volume"] < 0].sort_values("net_volume", ascending=True).head(top_n)

        bars = []
        for _, row in buyers.iterrows():
            bars.append({"label": row["broker"], "volume": row["net_volume"], "type": "Buy"})
        for _, row in sellers.iterrows():
            bars.append({"label": row["broker"], "volume": row["net_volume"], "type": "Sell"})

        wdf = pd.DataFrame(bars)
        order = wdf["label"].tolist()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=wdf.loc[wdf["type"]=="Buy", "label"],
            y=wdf.loc[wdf["type"]=="Buy", "volume"],
            name="Buy", marker_color="green"
        ))
        fig.add_trace(go.Bar(
            x=wdf.loc[wdf["type"]=="Sell", "label"],
            y=wdf.loc[wdf["type"]=="Sell", "volume"],
            name="Sell", marker_color="red"
        ))
        fig.update_xaxes(categoryorder="array", categoryarray=order, tickangle=-40)
        fig.update_layout(
            title=f"Week of {week.strftime('%b %d')} – Net Volume",
            barmode="group", template="simple_white", showlegend=False,
            height=380, margin=dict(l=20, r=20, t=40, b=20),
            yaxis_title="Net Volume"
        )
        week_figs.append(fig)

    # Layout em 2 gráficos por linha
    if not week_figs:
        st.warning("Nenhum dado para semanas recentes.")
        return

    for i in range(0, len(week_figs), 2):
        cols = st.columns(2)
        for j, fig in enumerate(week_figs[i:i+2]):
            with cols[j]:
                st.plotly_chart(fig, use_container_width=True)
