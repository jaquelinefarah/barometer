import pandas as pd
import os

def load_broker_data(file_path="data/Broker_Daily_Data.csv"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    # === Initial cleaning ===
    df.columns = df.columns.str.strip().str.lower()  # normalize column names
    df['date'] = pd.to_datetime(df['date'])  # ensure date column is datetime

    # === Create anon_volume column if it does not exist ===
    if 'anon_volume' not in df.columns:
        df['anon_volume'] = 0

    # === Create boolean 'anonymous' flag based on anon_volume ===
    df['anonymous'] = df['anon_volume'] > 0  # True if there is any anonymous volume

    return df

def fill_missing_business_days(df: pd.DataFrame, date_col: str = "date", broker_col: str = "broker") -> pd.DataFrame:
    """
    Preenche dias úteis faltantes para cada broker separadamente.
    Mantém todas as linhas originais e adiciona linhas de datas que estavam ausentes.
    """
    if df.empty or date_col not in df.columns:
        return df

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Range completo de dias úteis
    start = df[date_col].min()
    end = df[date_col].max()
    all_days = pd.bdate_range(start=start, end=end, freq="C")

    brokers = df[broker_col].unique()
    df_list = []

    for broker in brokers:
        df_b = df[df[broker_col] == broker].set_index(date_col).sort_index()
        df_b = df_b.reindex(all_days)  # insere dias faltantes
        df_b[broker_col] = broker      # reatribui o broker
        df_list.append(df_b.reset_index().rename(columns={"index": date_col}))

    df_fill = pd.concat(df_list, ignore_index=True)

    # Forward fill só para colunas numéricas
    num_cols = df_fill.select_dtypes(include=["number"]).columns
    df_fill[num_cols] = df_fill.groupby(broker_col)[num_cols].ffill()

    return df_fill



# === Custody Table prepossing (dedicated DataFrame) ===
def preprocess_custody(df):
    # Garante datetime
    df["date"] = pd.to_datetime(df["date"])

    # Group by broker and date (daily custody snapshot)
    df_custody = (
        df.groupby(["broker", "date"]).agg(
            start_balance=("start_balance", "first"),
            end_balance=("end_balance", "last")
        ).reset_index()
    )

    # Compute metrics
    df_custody["total_change"] = df_custody["end_balance"] - df_custody["start_balance"]
    df_custody["variation_pct"] = (
        df_custody["total_change"] / df_custody["start_balance"]
    ) * 100

    return df_custody




# === Buyers & Sellers Table prepossing (dedicated DataFrame) ===

def preprocess_buyers_sellers(df):
    # Garante datetime
    df["date"] = pd.to_datetime(df["date"])

    # Consolida por broker + date (igual custody)
    df_bs = (
        df.groupby(["broker", "date"]).agg(
            start_balance=("start_balance", "first"),
            end_balance=("end_balance", "last")
        ).reset_index()
    )

    # Calcula métricas
    df_bs["total_change"] = df_bs["end_balance"] - df_bs["start_balance"]
    df_bs["variation_pct"] = (df_bs["total_change"] / df_bs["start_balance"]) * 100

    # Classificação Buyer / Seller
    df_bs["Category"] = df_bs["total_change"].apply(
        lambda x: "Buyer" if x > 0 else ("Seller" if x < 0 else "Neutral")
    )

    return df_bs








 