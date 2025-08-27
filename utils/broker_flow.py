import pandas as pd

def get_weekly_top5_brokers(df):
    """
    Retorna os 5 brokers com maior volume líquido (buy - sell) por semana.
    """
    # Garantir que a coluna 'date' está em datetime
    df['date'] = pd.to_datetime(df['date'])

    # Criar coluna de semana
    df['week'] = df['date'].dt.to_period("W").apply(lambda r: r.start_time.date())

    # Calcular volume líquido por broker
    df['net_volume'] = df['buy_volume'] - df['sell_volume']

    # Agrupar por semana e broker
    grouped = df.groupby(['week', 'broker'], as_index=False)['net_volume'].sum()

    # Obter top 5 por semana
    top5_list = []
    for week, group in grouped.groupby('week'):
        top5 = group.sort_values('net_volume', ascending=False).head(5)
        top5['rank'] = range(1, len(top5) + 1)
        top5_list.append(top5)

    weekly_top5 = pd.concat(top5_list).reset_index(drop=True)
    return weekly_top5


def analyze_broker_flow(weekly_top5):
    """
    Analisa quais brokers entraram, saíram ou permaneceram no top 5 entre semanas consecutivas.
    """
    weeks = sorted(weekly_top5['week'].unique())
    transitions = []

    for i in range(len(weeks) - 1):
        current_week = weeks[i]
        next_week = weeks[i + 1]

        current_brokers = set(weekly_top5[weekly_top5['week'] == current_week]['broker'])
        next_brokers = set(weekly_top5[weekly_top5['week'] == next_week]['broker'])

        entered = next_brokers - current_brokers
        exited = current_brokers - next_brokers
        remained = current_brokers & next_brokers

        transitions.append({
            'week': next_week,
            'entered': list(entered),
            'exited': list(exited),
            'remained': list(remained)
        })

    return pd.DataFrame(transitions)
