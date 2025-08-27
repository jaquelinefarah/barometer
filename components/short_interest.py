import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def render_short_interest(cur_df: pd.DataFrame) -> None:
    if cur_df.empty:
        st.info("No data in the selected period.")
        return

    tmp = cur_df.copy()
    tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
    tmp["short_interest"] = pd.to_numeric(tmp["short_interest"], errors="coerce")

    sir_by_date = (
        tmp.groupby("date", as_index=False)["short_interest"]
           .sum()
           .sort_values("date")
    )

    mu = sir_by_date["short_interest"].mean()
    sd = sir_by_date["short_interest"].std(ddof=0)
    if pd.notna(sd) and sd > 0:
        threshold = float(mu + 2*sd); method_label = "μ + 2σ"
        peaks_by_date = sir_by_date[sir_by_date["short_interest"] > threshold]
    else:
        threshold = float(sir_by_date["short_interest"].quantile(0.95)); method_label = "q > 0.95"
        peaks_by_date = sir_by_date[sir_by_date["short_interest"] > threshold]

    st.markdown("## Short Interest Evolution with Highlighted Peaks")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sir_by_date["date"], y=sir_by_date["short_interest"],
                             mode="lines", name="Total Short Interest", line=dict(width=2)))
    fig.add_trace(go.Scatter(x=peaks_by_date["date"], y=peaks_by_date["short_interest"],
                             mode="markers", name="Detected Peaks",
                             marker=dict(size=9, symbol="diamond")))
    try:
        fig.add_hline(y=threshold, line=dict(dash="dash"),
                      annotation_text=f"Threshold ({method_label})",
                      annotation_position="top left")
    except Exception:
        pass
    fig.update_layout(height=320, margin=dict(l=10,r=10,t=30,b=30),
                      xaxis_title="Date", yaxis_title="Total Short Interest")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Brokers Active on Peak Days")
    if peaks_by_date.empty:
        st.info("No peaks detected for the selected period.")
        return

    df_picos = tmp[tmp["date"].isin(peaks_by_date["date"])].copy()
    cols = [c for c in ["date","broker","profile","anonymous",
                        "buy_volume","buy_vwap","sell_volume","sell_vwap"]
            if c in df_picos.columns]
    if "date" not in cols:
        cols = ["date"] + cols

    sort_cols = ["date"] + (["buy_volume"] if "buy_volume" in df_picos.columns else [])
    sort_asc  = [True] + ([False] if "buy_volume" in df_picos.columns else [])
    st.dataframe(df_picos[cols].sort_values(sort_cols, ascending=sort_asc)
                            .reset_index(drop=True),
                 use_container_width=True)
