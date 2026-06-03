import pandas as pd
from datetime import datetime, timedelta, timezone
from data.download import load_local_data
CACHE_DIR = "cache/prices"

def load_price_history(ticker: str) -> pd.Series:

    data = load_local_data(ticker)
    history = data['history']


    latest_date = history.index[-1] # 最新の日付を取得
    one_year_ago = latest_date - pd.DateOffset(years=1) # 1年前の日付を計算（PandasのDateOffsetが便利です）
    history_1y = history.loc[one_year_ago:] # その期間を切り出す（スライス）

    return history_1y['Close']

def load_prices(tickers):

    data = {}

    for t in tickers:

        data[t] = load_price_history(t)

    return pd.DataFrame(data)
