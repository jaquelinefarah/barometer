from __future__ import annotations
import streamlit as st
from typing import Iterable, Mapping, Any, Optional
import pandas as pd

from .metrics import calculate_variation

# --- Formatadores ---
def _format_value(fmt: str, value):
    if value is None or pd.isna(value):
        return "—"
    if fmt == "int":
        try:
            return f"{int(round(value)):,}"
        except Exception:
            return str(value)
    if fmt == "float4":
        return f"{float(value):,.4f}"
    if fmt == "pct":
        return f"{float(value):.2f}%"
    return str(value)

def _format_delta(current, previous, fmt: str = "pct"):
    if previous in (None, 0) or pd.isna(previous):
        return None
    delta = calculate_variation(current, previous)
    if fmt == "pct":
        return f"{delta:+.2f}%"
    return f"{delta:+.2f}"

# --- Cards ---
def render_metric_cards(
    metrics: Iterable[Mapping[str, Any]],
    cols_per_row: int = 4,
    title: Optional[str] = None,
) -> None:
    """
    Renderiza cards de métricas com st.metric.
    metrics: Iterable de dicts gerados por compute_metrics()
    """
    metrics = list(metrics)

    if title:
        st.markdown(f"### {title}")

    if not metrics:
        st.info("No metrics to display for the selected period.")
        return

    rows = (len(metrics) + cols_per_row - 1) // cols_per_row
    idx = 0
    for _ in range(rows):
        cols = st.columns(cols_per_row)
        for c in cols:
            if idx >= len(metrics):
                break

            m = metrics[idx]
            label = m.get("label", "")
            cur = m.get("current")
            prev = m.get("previous")
            fmt = m.get("fmt", "raw")
            delta_color = m.get("delta_color", "normal")
            help_text = m.get("help")

            # formatando valor e variação
            value_str = _format_value(fmt, cur)
            delta_str = _format_delta(cur, prev, "pct")

            with c:
                st.metric(
                    label=label,
                    value=value_str,
                    delta=(delta_str if delta_str is not None else "—"),
                    delta_color=delta_color,
                    help=help_text if help_text else None
                )

            idx += 1
