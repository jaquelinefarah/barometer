import pandas as pd

# --- Funções auxiliares seguras ---
def _safe_sum(s: pd.Series) -> float:
    return float(pd.to_numeric(s, errors="coerce").fillna(0).sum())

def _safe_mean(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce")
    return float(s.mean()) if len(s) else 0.0

def _sir(df: pd.DataFrame) -> float:
    si = _safe_sum(df.get("short_interest", pd.Series(dtype=float)))
    eb = _safe_sum(df.get("end_balance", pd.Series(dtype=float)))
    return float(si / eb) if eb else 0.0

# --- Função de variação ---
def calculate_variation(current: float, previous: float) -> float:
    """Calcula variação percentual entre valores atual e anterior."""
    if previous in (None, 0) or pd.isna(previous):
        return 0.0
    return ((current - previous) / previous) * 100.0

# --- Função principal ---
def compute_metrics(cur_df: pd.DataFrame, prev_df: pd.DataFrame, grouped_df: pd.DataFrame | None = None):
    """
    Calcula métricas conforme solicitado:
      - Buy/Sell Volume: soma
      - VWAP Buy / VWAP Sell: média
      - Total Brokers: nunique
      - Start/End Balance: soma
      - Short Interest Ratio: sum(short_interest) / sum(end_balance)
      - (Opcional) Total Volume: buy+sell
    grouped_df: dataframe agregado (ex.: por dia/semana) para série de tendência (opcional)
    Retorna lista de dicionários: {label, current, previous, fmt, delta_color, help, trend?}
    """
    # ---- atuais
    cur_buy   = _safe_sum(cur_df.get("buy_volume", pd.Series(dtype=float)))
    cur_sell  = _safe_sum(cur_df.get("sell_volume", pd.Series(dtype=float)))
    cur_vol   = cur_buy + cur_sell

    cur_vwap_buy  = _safe_mean(cur_df.get("buy_vwap", pd.Series(dtype=float)))
    cur_vwap_sell = _safe_mean(cur_df.get("sell_vwap", pd.Series(dtype=float)))

    cur_brok = int(cur_df["broker"].nunique()) if "broker" in cur_df.columns else 0
    cur_sb   = _safe_sum(cur_df.get("start_balance", pd.Series(dtype=float)))
    cur_eb   = _safe_sum(cur_df.get("end_balance", pd.Series(dtype=float)))
    cur_sir  = _sir(cur_df)

    # ---- anteriores
    prev_buy   = _safe_sum(prev_df.get("buy_volume", pd.Series(dtype=float)))
    prev_sell  = _safe_sum(prev_df.get("sell_volume", pd.Series(dtype=float)))
    prev_vol   = prev_buy + prev_sell

    prev_vwap_buy  = _safe_mean(prev_df.get("buy_vwap", pd.Series(dtype=float)))
    prev_vwap_sell = _safe_mean(prev_df.get("sell_vwap", pd.Series(dtype=float)))

    prev_brok = int(prev_df["broker"].nunique()) if "broker" in prev_df.columns else 0
    prev_sb   = _safe_sum(prev_df.get("start_balance", pd.Series(dtype=float)))
    prev_eb   = _safe_sum(prev_df.get("end_balance", pd.Series(dtype=float)))
    prev_sir  = _sir(prev_df)

    # ---- séries de tendência (opcional)
    trend_buy   = grouped_df["buy_volume"]    if (grouped_df is not None and "buy_volume" in grouped_df.columns) else None
    trend_sell  = grouped_df["sell_volume"]   if (grouped_df is not None and "sell_volume" in grouped_df.columns) else None
    trend_vb    = grouped_df["buy_vwap"]      if (grouped_df is not None and "buy_vwap" in grouped_df.columns) else None
    trend_vs    = grouped_df["sell_vwap"]     if (grouped_df is not None and "sell_vwap" in grouped_df.columns) else None
    trend_sb    = grouped_df["start_balance"] if (grouped_df is not None and "start_balance" in grouped_df.columns) else None
    trend_eb    = grouped_df["end_balance"]   if (grouped_df is not None and "end_balance" in grouped_df.columns) else None
    trend_sir   = grouped_df["sir"]           if (grouped_df is not None and "sir" in grouped_df.columns) else None
    trend_vol   = (grouped_df["buy_volume"] + grouped_df["sell_volume"]) if (grouped_df is not None and {"buy_volume","sell_volume"}.issubset(grouped_df.columns)) else None

    metrics = [
        {"label": "Buy Volume",     "current": cur_buy,   "previous": prev_buy,   "fmt": "int",     "delta_color": "normal",  "help": None, "trend": trend_buy},
        {"label": "Sell Volume",    "current": cur_sell,  "previous": prev_sell,  "fmt": "int",     "delta_color": "normal",  "help": None, "trend": trend_sell},

        {"label": "VWAP Buy",       "current": cur_vwap_buy,  "previous": prev_vwap_buy,  "fmt": "float4", "delta_color": "normal",  "help": None, "trend": trend_vb},
        {"label": "VWAP Sell",      "current": cur_vwap_sell, "previous": prev_vwap_sell, "fmt": "float4", "delta_color": "normal",  "help": None, "trend": trend_vs},

        {"label": "Total Brokers",  "current": cur_brok,  "previous": prev_brok,  "fmt": "int",     "delta_color": "normal",  "help": "Distinct brokers", "trend": None},

        {"label": "Start Balance",  "current": cur_sb,    "previous": prev_sb,    "fmt": "int",     "delta_color": "normal",  "help": None, "trend": trend_sb},
        {"label": "End Balance",    "current": cur_eb,    "previous": prev_eb,    "fmt": "int",     "delta_color": "normal",  "help": None, "trend": trend_eb},

        {"label": "Short Interest Ratio", "current": cur_sir, "previous": prev_sir, "fmt": "float4",
         "delta_color": "inverse", "help": "sum(short_interest) / sum(end_balance)", "trend": trend_sir},
    ]
    return metrics
