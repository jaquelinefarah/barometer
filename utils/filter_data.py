import pandas as pd

def filter_data(
    df: pd.DataFrame,
    date_range: tuple = None,
    broker: str = None,
    ticker: str = None
) -> pd.DataFrame:
    """
    Filtra dados por intervalo de datas, broker e (opcional) ticker.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Filtro por data
    if date_range:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df = df[(df["date"] >= start) & (df["date"] <= end)]

    # Filtro por broker
    if broker and broker != "All":
        df = df[df["broker"] == broker]

    # 🔒 ticker (futuro)
    if ticker and ticker != "All":
        df = df[df["ticker"] == ticker]

    return df