import pandas as pd
import streamlit as st
from utils.periods import PERIOD_PRESETS, get_period_by_preset, previous_period_by_preset
from utils.filter_data import filter_data


def render_period_sidebar(
    df: pd.DataFrame,
    date_col: str = "date",
    sections: list[str] | None = None,
    show_filters_title: bool = True,
):
    if sections is None:
        sections = ["Company View", "Short Interest"]

    if show_filters_title:
        st.sidebar.title("🔎 Filters")

    # Seções
    section = st.sidebar.selectbox("Section", sections, index=0)

    # Preset de período (lista de strings, não função!)
    preset = st.sidebar.selectbox("Reference period", PERIOD_PRESETS, index=0)

    # Se for "Last closed week" → calcula com base no dataset
    if preset == "Last closed week":
        start_date, end_date = get_period_by_preset(preset, df, date_col=date_col)
    else:
        start_date, end_date = get_period_by_preset(preset)

    # Filtros adicionais
    brokers = ["All"] + sorted(df["broker"].dropna().unique().tolist())
    broker = st.sidebar.selectbox("Broker", brokers, index=0)

    # aplica filtro
    cur_df = filter_data(df, date_range=(start_date, end_date), broker=broker)

    # Período anterior
    prev_start, prev_end = previous_period_by_preset(preset, start_date, end_date)
    prev_df = filter_data(df, date_range=(prev_start, prev_end), broker=broker)

    # Label para títulos
    period_label = f"{start_date:%Y/%m/%d} – {end_date:%Y/%m/%d}"

    return section, preset, start_date, end_date, cur_df, prev_df, period_label

