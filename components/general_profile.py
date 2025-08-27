# components/general_profile.py
from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# --- helpers ---
def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")

def _wavg(values: pd.Series, weights: pd.Series) -> float:
    values = _to_num(values)
    weights = _to_num(weights)
    w = np.nansum(weights)
    return float(np.nan) if (w is None or w == 0) else float(np.nansum(values * weights) / w)

def _pct_delta(curr: float, prev: float) -> str | None:
    if prev is None or np.isnan(prev) or prev == 0:
        return None
    return f"{( (curr - prev) / prev ) * 100:+.1f}%"

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    # Normaliza nomes usuais
    for col in ["buy_volume","sell_volume","buy_vwap","sell_vwap","date"]:
        if col in data.columns:
            if col in ["buy_volume","sell_volume","buy_vwap","sell_vwap"]:
                data[col] = _to_num(data[col])
            if col == "date":
                data[col] = pd.to_datetime(data[col], errors="coerce")

    # Profile: aceita "profile" ou "most_common_profile"
    if "profile" not in data.columns:
        if "most_common_profile" in data.columns:
            data = data.rename(columns={"most_common_profile": "profile"})
        else:
            data["profile"] = "Unknown"

    # Anonymous: aceita coluna booleana ou volume anônimo
    if "anon_volume" not in data.columns:
        data["anon_volume"] = 0
    if "anonymous" not in data.columns:
        # cria boolean com base no volume anônimo
        data["anonymous"] = _to_num(data["anon_volume"]) > 0

    return data

def _aggregate(df: pd.DataFrame) -> dict:
    total_buy  = float(np.nansum(df["buy_volume"]))  if "buy_volume"  in df.columns else float("nan")
    total_sell = float(np.nansum(df["sell_volume"])) if "sell_volume" in df.columns else float("nan")

    w_buy  = _wavg(df.get("buy_vwap", pd.Series(dtype=float)),  df.get("buy_volume",  pd.Series(dtype=float)))
    w_sell = _wavg(df.get("sell_vwap", pd.Series(dtype=float)), df.get("sell_volume", pd.Series(dtype=float)))

    # % de volume anônimo: usa 'anon_volume' quando existir; senão, soma buy+sell das linhas anonymous=True
    if "anon_volume" in df.columns and df["anon_volume"].notna().any():
        anon_vol = float(np.nansum(_to_num(df["anon_volume"])))
    else:
        anon_vol = float(np.nansum(_to_num(df.get("buy_volume", 0))[df.get("anonymous", False)])) \
                 + float(np.nansum(_to_num(df.get("sell_volume", 0))[df.get("anonymous", False)]))

    denom = (0 if np.isnan(total_buy) else total_buy) + (0 if np.isnan(total_sell) else total_sell)
    anon_pct = float("nan") if denom == 0 else (anon_vol / denom) * 100.0

    # perfil topo por buy volume
    if "profile" in df.columns and "buy_volume" in df.columns:
        top_prof_row = (df.groupby("profile", as_index=False)["buy_volume"].sum()
                          .sort_values("buy_volume", ascending=False).head(1))
        top_profile = top_prof_row["profile"].iloc[0] if len(top_prof_row) else "Unknown"
    else:
        top_profile = "Unknown"

    # número de brokers/investors distintos (aceita 'broker' ou 'investor')
    ent_col = "broker" if "broker" in df.columns else ("investor" if "investor" in df.columns else None)
    n_entities = int(df[ent_col].nunique()) if ent_col else 0

    return {
        "total_buy": total_buy,
        "total_sell": total_sell,
        "w_buy_vwap": w_buy,
        "w_sell_vwap": w_sell,
        "anon_pct": anon_pct,
        "top_profile": top_profile,
        "n_entities": n_entities,
    }

def render_general_profile(cur_df: pd.DataFrame, prev_df: pd.DataFrame | None = None) -> None:
    """
    General Profile: cards de resumo + pizza de 'Buy Volume by Profile'.
    Lê colunas: date, broker/investor, buy_volume, sell_volume, buy_vwap, sell_vwap, profile,
                anon_volume (opcional) e/ou anonymous (opcional).
    """
    if cur_df is None or cur_df.empty:
        st.info("No data in the selected period.")
        return

    cur = _normalize_columns(cur_df)
    prev = _normalize_columns(prev_df) if (prev_df is not None and not prev_df.empty) else None

    cur_agg  = _aggregate(cur)
    prev_agg = _aggregate(prev) if prev is not None else None

    # === CARDS ===
    st.markdown("#### General Profile")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Buy Volume",  f"{cur_agg['total_buy']:,.0f}",
                  _pct_delta(cur_agg['total_buy'],  prev_agg['total_buy']  if prev_agg else None))
        st.metric("Top Profile", cur_agg["top_profile"])
    with col2:
        st.metric("Sell Volume", f"{cur_agg['total_sell']:,.0f}",
                  _pct_delta(cur_agg['total_sell'], prev_agg['total_sell'] if prev_agg else None))
        st.metric("Anonymous Activity", f"{cur_agg['anon_pct']:.1f}%"
                  if not np.isnan(cur_agg['anon_pct']) else "n/a",
                  _pct_delta(cur_agg['anon_pct'], prev_agg['anon_pct'] if prev_agg else None))
    with col3:
        st.metric("VWAP Buy (w)",  f"{cur_agg['w_buy_vwap']:.4f}"
                  if not np.isnan(cur_agg['w_buy_vwap']) else "n/a",
                  _pct_delta(cur_agg['w_buy_vwap'],  prev_agg['w_buy_vwap']  if prev_agg else None))
        st.metric("VWAP Sell (w)", f"{cur_agg['w_sell_vwap']:.4f}"
                  if not np.isnan(cur_agg['w_sell_vwap']) else "n/a",
                  _pct_delta(cur_agg['w_sell_vwap'], prev_agg['w_sell_vwap'] if prev_agg else None))

    # === PIE: Buy Volume by Profile ===
    st.markdown("#### Distribution of Investor Profiles by Buy Volume")
    if "buy_volume" in cur.columns and "profile" in cur.columns:
        df_profile = (cur.groupby("profile", as_index=False)["buy_volume"].sum()
                         .rename(columns={"buy_volume": "total_buy_volume"}))
        fig_pie = px.pie(
            df_profile,
            names="profile",
            values="total_buy_volume",
            title="Buy Volume by Investor Profile",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig_pie.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=280)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Missing columns for the pie chart (need 'profile' and 'buy_volume').")
