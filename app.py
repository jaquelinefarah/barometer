from __future__ import annotations
import pandas as pd
from pathlib import Path
import streamlit as st

from utils.load_data import load_broker_data, fill_missing_business_days, preprocess_custody, preprocess_buyers_sellers
from components.layout import set_global_styles, render_sidebar_brand
from utils.periods_sidebar import render_period_sidebar
from utils.filter_data import filter_data
from components.metrics import compute_metrics
from components.cards import render_metric_cards
from components.short_interest import render_short_interest
from components.general_profile import render_general_profile
from components.top_buyers_sellers import render_top_buyers_sellers
from components.weekly_top5_interleaved import render_weekly_trading
from components.custody import render_custody
from components.buyeres_sellers import render_buyers_sellers

def main():
    # 1) Page + global CSS
    st.set_page_config(page_title="Broker Trading Barometer", layout="wide")
    set_global_styles()

    # 2) Brand in the sidebar
    win_logo = Path(r"C:\Projects\valore_dashboard_brokers\assets\logo.png")
    logo_path = str(win_logo) if win_logo.exists() else "assets/logo.png"
    render_sidebar_brand(title="Broker Trading Barometer", logo_path=logo_path)

    # 3) Load bases
    df = load_broker_data()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 👉 versão preenchida (pra calendário/filtros)
    df_fill = fill_missing_business_days(df, date_col="date")

    # Preprocess custody table (usa o df cru → só dias reais)
    df_custody = preprocess_custody(df)

    # Preprocess buyers/sellers table (idem)
    df_bs = preprocess_buyers_sellers(df)

    # 4) Sidebar → seção + períodos
    section, preset, start_date, end_date, cur_df, prev_df, period_label = render_period_sidebar(
        df_fill,  # 👉 usa df_fill aqui, pq a sidebar depende do calendário completo
        date_col="date",
        sections=[
            "Company View",
            "Short Interest",
            "General Profile",
            "Top Buyers & Sellers",
            # "Weekly Trading (demo)",
            "Custody",
            "Buyers & Sellers"
        ],
        show_filters_title=False,
    )

    # 5) Conteúdo principal
    title_prefix = f"{section} – {period_label}"

    if section == "Company View":
        st.subheader(f" {title_prefix}")
        metrics = compute_metrics(cur_df, prev_df)
        render_metric_cards(metrics, cols_per_row=4)

    elif section == "Short Interest":
        st.subheader(f" {title_prefix}")
        render_short_interest(cur_df)

    elif section == "General Profile":
        st.subheader(f" {title_prefix}")
        render_general_profile(cur_df, prev_df)

    elif section == "Top Buyers & Sellers":
        st.subheader(f" {title_prefix}")
        render_top_buyers_sellers(cur_df, top_n=5)

    # você comentou o Weekly Trading, então pode apagar ou deixar só comentado
    # elif section == "Weekly Trading (demo)":
    #     st.subheader(f" {title_prefix}")
    #     render_weekly_trading(cur_df, 5)

    elif section == "Custody":
        st.subheader(f" {title_prefix}")
        render_custody(cur_df)

    elif section == "Buyers & Sellers":
        st.subheader(f" {title_prefix}")
        render_buyers_sellers(cur_df)

    else:
        st.info("Select a section in the sidebar.")


if __name__ == "__main__":
    main()
