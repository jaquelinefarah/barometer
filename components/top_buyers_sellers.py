# components/top_traders.py
from __future__ import annotations
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def _to_num(s: pd.Series) -> pd.Series:
    """Converte série em numérica, tratando erros."""
    return pd.to_numeric(s, errors="coerce")


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza colunas e garante consistência de tipos."""
    data = df.copy()
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for c in ["buy_volume", "sell_volume"]:
        data[c] = _to_num(data[c]) if c in data.columns else 0
    if "broker" not in data.columns:
        if "investor" in data.columns:
            data = data.rename(columns={"investor": "broker"})
        else:
            data["broker"] = "Unknown"
    return data


def _format_number(x: float) -> str:
    """Formata números de forma compacta (1.5K, 2.3M)."""
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    elif abs(x) >= 1_000:
        return f"{x/1_000:.1f}K"
    return f"{x:.0f}"


def _bar_h(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str) -> go.Figure:
    """Cria gráfico horizontal de barras com números compactos."""
    fig = go.Figure(go.Bar(
        x=df[x_col],
        y=df[y_col],
        orientation="h",
        marker=dict(color=color),
        text=[_format_number(v) for v in df[x_col]],
        textposition="outside"
    ))
    h = max(220, 38 * len(df))  # altura adaptável
    fig.update_layout(
        title=title,
        height=h,
        margin=dict(l=10, r=40, t=40, b=10),
        xaxis_title="Volume",
        yaxis_title=None,
        xaxis=dict(automargin=True)
    )
    return fig


def render_top_buyers_sellers(cur_df: pd.DataFrame, top_n: int = 5, show_tables: bool = False) -> None:
    """Renderiza gráficos Top Buyers & Sellers (Gross ou Net) em linhas separadas."""
    if cur_df is None or cur_df.empty:
        st.info("No data in the selected period.")
        return

    data = _normalize(cur_df)

    # Altern mode
    mode = st.radio("Calculation Mode:", ["Gross (Total Volumes)", "Net (Buy - Sell)"], horizontal=True)

    if mode.startswith("Gross"):
        buyers = (data.groupby("broker", as_index=False)["buy_volume"].sum()
                  .sort_values("buy_volume", ascending=False).head(top_n))

        sellers = (data.groupby("broker", as_index=False)["sell_volume"].sum()
                   .assign(sell_volume=lambda d: -d["sell_volume"])  # deixa negativo para sellers
                   .sort_values("sell_volume").head(top_n))

        buyers_title = f"Top {top_n} Buyers – Gross Volume"
        sellers_title = f"Top {top_n} Sellers – Gross Volume"

    else:  # Net
        net = (data.groupby("broker", as_index=False)
               .agg(buy_volume=("buy_volume", "sum"),
                    sell_volume=("sell_volume", "sum")))
        net["net_volume"] = net["buy_volume"] - net["sell_volume"]

        buyers = net[net["net_volume"] > 0].sort_values("net_volume", ascending=False).head(top_n)
        sellers = net[net["net_volume"] < 0].sort_values("net_volume", ascending=True).head(top_n)

        buyers_title = f"Top {top_n} Buyers – Net Volume"
        sellers_title = f"Top {top_n} Sellers – Net Volume"

    # === Layout===
  
    # Buyers
    st.markdown(f"### Top {top_n} Buyers")
    st.plotly_chart(
        _bar_h(buyers, buyers.columns[-1], "broker", buyers_title, "#2ecc71"),
        use_container_width=True
    )

    # Sellers
    st.markdown(f"### Top {top_n} Sellers")
    st.plotly_chart(
        _bar_h(sellers, sellers.columns[-1], "broker", sellers_title, "#e74c3c"),
        use_container_width=True
    )

    # Optional
    if show_tables:
        with st.expander("🔎 See data tables"):
            st.dataframe(buyers, use_container_width=True)
            st.dataframe(sellers, use_container_width=True)








