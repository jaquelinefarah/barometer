from datetime import datetime, timedelta
from typing import Tuple
import pandas as pd

PERIOD_PRESETS = [
    "Last closed week",
    "Last 4 weeks",
    "Last 3 months",
    "Last 12 months",
]


def _last_closed_week_calendar() -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Seg–Sex da última semana fechada (pelo calendário, independente do dataset)."""
    today = datetime.today()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday + 7)
    friday = monday + timedelta(days=4)
    return pd.to_datetime(monday.date()), pd.to_datetime(friday.date())


def _last_closed_week_data(df: pd.DataFrame, date_col: str = "date") -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Última semana fechada *com dados* no dataset (Seg–Sex)."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    max_date = df[date_col].max()
    if pd.isna(max_date):
        return None, None  # dataset vazio

    # encontra a última sexta-feira <= max_date
    friday = max_date - pd.Timedelta(days=(max_date.weekday() - 4) % 7)

    # correção: não permitir sexta depois do max_date
    if friday > max_date:
        friday -= pd.Timedelta(weeks=1)

    monday = friday - pd.Timedelta(days=4)

    return monday.normalize(), friday.normalize()


def _last_n_weeks_range(n: int, df: pd.DataFrame | None = None, date_col: str = "date") -> Tuple[pd.Timestamp, pd.Timestamp]:
    """N semanas completas terminando na última semana fechada (alinhadas Seg–Sex)."""
    if df is not None:
        start0, end0 = _last_closed_week_data(df, date_col)
    else:
        start0, end0 = _last_closed_week_calendar()

    if start0 is None or end0 is None:
        return None, None

    startN = start0 - timedelta(weeks=n - 1)
    return startN.normalize(), end0.normalize()


def get_period_by_preset(preset: str, df: pd.DataFrame | None = None, date_col: str = "date") -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Período atual para cada preset."""
    
    if preset == "Last closed week":
        if df is None:
            raise ValueError("Para 'Last closed week' é necessário passar o DataFrame.")
        return _last_closed_week_data(df, date_col)

    # ancora na última semana fechada (pelos dados se possível)
    if df is not None:
        _, anchor_end = _last_closed_week_data(df, date_col)
    else:
        _, anchor_end = _last_closed_week_calendar()

    if anchor_end is None:
        return None, None

    if preset == "Last 4 weeks":
        return _last_n_weeks_range(4, df, date_col)

    if preset == "Last 3 months":
        start = anchor_end - pd.DateOffset(months=3)
        return start.normalize(), anchor_end.normalize()

    if preset == "Last 12 months":
        start = anchor_end - pd.DateOffset(years=1)
        return start.normalize(), anchor_end.normalize()

    raise ValueError(f"Preset desconhecido: {preset}")


def previous_period_by_preset(preset: str,
                              start_date: pd.Timestamp,
                              end_date: pd.Timestamp) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Janela imediatamente anterior equivalente ao preset atual."""
    start_date = pd.to_datetime(start_date); end_date = pd.to_datetime(end_date)

    if preset == "Last closed week":
        prev_end = start_date - pd.Timedelta(days=1)
        prev_start = prev_end - pd.Timedelta(days=4)
        return prev_start.normalize(), prev_end.normalize()

    if preset == "Last 4 weeks":
        # mantém sempre blocos completos de 4 semanas (Seg–Sex)
        prev_end = start_date - pd.Timedelta(days=1)
        prev_start = prev_end - pd.Timedelta(weeks=4) + pd.Timedelta(days=1)
        return prev_start.normalize(), prev_end.normalize()

    if preset == "Last 3 months":
        prev_end = start_date - pd.Timedelta(days=1)
        prev_start = prev_end - pd.DateOffset(months=3) + pd.Timedelta(days=1)
        return prev_start.normalize(), prev_end.normalize()

    if preset == "Last 12 months":
        prev_end = start_date - pd.Timedelta(days=1)
        prev_start = prev_end - pd.DateOffset(years=1) + pd.Timedelta(days=1)
        return prev_start.normalize(), prev_end.normalize()

    # fallback: mesma duração deslocada pra trás
    prev_end = start_date - pd.Timedelta(days=1)
    prev_start = prev_end - (end_date - start_date)
    return prev_start.normalize(), prev_end.normalize()
